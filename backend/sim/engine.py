"""
Simulation tick engine.

Each call to tick(world) advances time by one step and applies all BEHAVIOR
effects to entities that have HP — either defined directly on the entity,
or inherited via TYPE_OF categories.

BEHAVIOR number convention:
  positive  → HP drain  (hunger, decay, battery drain, entropy ...)
  negative  → HP gain   (recharge, regeneration ...)

Lookup order per entity (all four sources summed):
  1. BEHAVIOR relations where ent1 == entity.id         (entity-specific)
  2. BEHAVIOR relations where ent1 == category          (TYPE_OF cascade)
  3. BEHAVIOR relations where ent1 == location.id       (location-direct)
  4. BEHAVIOR relations where ent1 == location_category (location TYPE_OF cascade)

All matching behaviors are collected and their rates summed — an entity
under multiple effects accumulates them all each tick.
"""

import math
import random
from dataclasses import dataclass

from backend.core.world import World
from backend.core.entity import Entity, EntityType
from backend.core.relation import Relation, RelationType


# ── Intent ───────────────────────────────────────────────────────────────────

@dataclass
class Intent:
    """A single action a CHAR wants to perform this tick.

    Produced by _collect_intents(); consumed by _execute_intents().
    Intents are ephemeral — they live only within one tick() call.
    """
    actor_id: str
    action: str              # "EAT", "MOVE", "PICK", …
    target_id: str | None = None
    amount: int = 1
    weight: float = 1.0      # urgency: 0.0 = low, 1.0 = critical


def _poisson(lam: float, max_yield: int = 4) -> int:
    """Draw a sample from Poisson(lam), capped at max_yield. Uses Knuth's algorithm."""
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= random.random()
    return min(k - 1, max_yield)


def _process_produce(world: World) -> list[str]:
    """Apply all PRODUCE relations.

    Either/or yield mode:
      - lambda > 0  → stochastic: draw from Poisson(lambda), capped at number
      - lambda == 0 → deterministic: fixed yield equal to number
    Stock cap (optional): if both producer.capacity and item.capacity are set,
    total stock is capped at producer.capacity × item.capacity.

    Type-based producer: if ent1 is not a known entity ID, it is treated as a
    TYPE_OF category name. All ENVI entities of that type are found; those
    occupied by at least one CHAR are excluded. One empty ENVI is chosen at
    random to receive the produced items this tick.
    """
    log: list[str] = []
    produce_rels = [r for r in world.relations.values() if r.type == RelationType.PRODUCE]
    for r in produce_rels:
        amount = _poisson(r.lambda_, r.number) if r.lambda_ > 0 else r.number
        if amount == 0:
            continue

        item = world.get(r.ent2)

        # Resolve producer: direct entity or type-based (pick random empty ENVI).
        # UNIQUE entities are archetypes/type-names — treat them as type-based producers.
        producer = world.get(r.ent1)
        if producer is None or producer.type == EntityType.UNIQUE:
            # Type-based: find all ENVI entities with TYPE_OF(x, r.ent1).
            candidates = [
                world.get(rel.ent1) for rel in world.relations.values()
                if rel.type == RelationType.TYPE_OF and rel.ent2 == r.ent1
                and world.get(rel.ent1) is not None
                and world.get(rel.ent1).type == EntityType.ENVI
            ]
            # Exclude ENVIs that already hold a CHAR child (occupied squares).
            occupied = {
                rel.ent1 for rel in world.relations.values()
                if rel.type == RelationType.LOCATION
                and world.get(rel.ent2) is not None
                and world.get(rel.ent2).type == EntityType.CHAR
            }
            candidates = [e for e in candidates if e.id not in occupied]
            if not candidates:
                continue
            producer = random.choice(candidates)

        # Find existing LOCATION(producer.id → ent2) to read current stock.
        loc = next(
            (l for l in world.relations.values()
             if l.type == RelationType.LOCATION and l.ent1 == producer.id and l.ent2 == r.ent2),
            None,
        )
        current = loc.number if loc is not None else 0

        # Cap: producer.capacity × item.capacity (only when both are defined).
        if (item is not None
                and producer.capacity is not None and item.capacity is not None):
            stock_cap = producer.capacity * item.capacity
            amount = min(amount, stock_cap - current)

        if amount <= 0:
            continue

        if loc is not None:
            # HP: blend existing stack with freshly produced items (weighted average).
            if item is not None and item.hp_max is not None and loc.hp is not None:
                total = current + amount
                loc.hp = round((current * loc.hp + amount * item.hp_max) / total)
            loc.number += amount
        else:
            new_id = max(world.relations.keys(), default=0) + 1
            init_hp = item.hp_max if (item is not None and item.hp_max is not None) else None
            world.relations[new_id] = Relation(
                id=new_id,
                type=RelationType.LOCATION,
                ent1=producer.id,
                ent2=r.ent2,
                number=amount,
                hp=init_hp,
            )
        log.append(f"{producer.name}: +{amount} {item.name}")
    return log


def _collect_behaviors(
    world: World,
    entity_id: str,
    location_id: str | None = None,
) -> list[tuple[str, int]]:
    """
    Return all (behavior_name, rate) pairs active for entity_id.

    Four sources (applied in order, all summed):
      1. Entity-specific BEHAVIOR relations (direct override).
      2. TYPE_OF category cascade — behaviors on each category the entity belongs to.
      3. Location-direct — BEHAVIOR on the specific ENVI the entity currently occupies.
      4. Location-category cascade — BEHAVIOR on TYPE_OF categories of that ENVI
         (e.g. TYPE_OF(D1, HOME_SQUARE) + BEHAVIOR(HOME_SQUARE, RECHARGE, -5)).

    location_id: if provided, use this entity as the location instead of calling
                 world.location_of(). Used by _process_sums_hp to handle per-stack
                 HP for SUMS entities with multiple LOCATION relations.
    """
    behaviors: list[tuple[str, int]] = []

    # 1. Entity-specific behaviors
    for r in world.relations.values():
        if r.type == RelationType.BEHAVIOR and r.ent1 == entity_id:
            behaviors.append((r.ent2, r.number))

    # 2. Inherited via TYPE_OF categories
    categories = [
        r.ent2 for r in world.relations.values()
        if r.type == RelationType.TYPE_OF and r.ent1 == entity_id
    ]
    for category in categories:
        for r in world.relations.values():
            if r.type == RelationType.BEHAVIOR and r.ent1 == category:
                behaviors.append((r.ent2, r.number))

    # 3 + 4. Location-based: behaviors on the entity's current ENVI,
    #         and on the TYPE_OF categories of that ENVI.
    location = world.get(location_id) if location_id is not None else world.location_of(entity_id)
    if location is not None:
        for r in world.relations.values():
            if r.type == RelationType.BEHAVIOR and r.ent1 == location.id:
                behaviors.append((r.ent2, r.number))
        location_categories = [
            r.ent2 for r in world.relations.values()
            if r.type == RelationType.TYPE_OF and r.ent1 == location.id
        ]
        for category in location_categories:
            for r in world.relations.values():
                if r.type == RelationType.BEHAVIOR and r.ent1 == category:
                    behaviors.append((r.ent2, r.number))

    return behaviors


def _process_sums_hp(world: World) -> list[str]:
    """Apply BEHAVIOR-based HP drain to per-LOCATION stacks of SUMS entities.

    Iterates all LOCATION relations that carry an hp value (freshness/durability).
    When hp reaches 0, the stack is wiped (number set to 0).
    Only LOCATION relations pointing to SUMS entities are processed here;
    CHAR/UNIQUE HP is handled in the main entity loop in tick().
    """
    log: list[str] = []
    for loc_rel in list(world.relations.values()):
        if loc_rel.type != RelationType.LOCATION:
            continue
        if loc_rel.hp is None:
            continue
        item = world.get(loc_rel.ent2)
        if item is None or item.type != EntityType.SUMS:
            continue

        behaviors = _collect_behaviors(world, loc_rel.ent2, location_id=loc_rel.ent1)
        if not behaviors:
            continue

        total_drain = sum(rate for _, rate in behaviors)
        if total_drain == 0:
            continue

        old_hp = loc_rel.hp
        hp_max = item.hp_max if item.hp_max is not None else old_hp
        loc_rel.hp = max(0, min(hp_max, loc_rel.hp - total_drain))

        if loc_rel.hp != old_hp:
            causes = "+".join(name for name, _ in behaviors)
            if loc_rel.hp == 0:
                del world.relations[loc_rel.id]
                log.append(f"{item.name}: HP {old_hp} -> 0  [{causes}] [WIPED]")
            else:
                log.append(f"{item.name}: HP {old_hp} -> {loc_rel.hp}  [{causes}]")
    return log


def _get_dialogue(world: World, entity_id: str | None) -> str | None:
    """Return description of a dialogue UNIQUE entity, or None."""
    if entity_id is None:
        return None
    entity = world.get(entity_id)
    return entity.description if entity is not None else None


def _process_triggers(world: World) -> list[str]:
    """Fire TRIGGER relations — character dialogue driven by HP or probability.

    Three modes (controlled by 'number' field):
      number > 0   HP-threshold, fire-once: fires when ent1.hp <= number.
                   Probability = normal CDF Phi((number - hp) / lambda_).
                   lambda_ == 0 means fire immediately (p = 1.0).
                   Fired IDs tracked in meta.vars["triggers_fired"].
      number == 0  Ambient, repeatable: fires each tick with Bernoulli
                   probability lambda_. No HP condition required.
      number == -1 Resurrection: fires when ent1.hp == 0, resets hp to
                   hp_max, and clears this entity's threshold triggers from
                   fired so the arc can repeat in the next life.
    """
    log: list[str] = []
    fired: list = world.meta.vars.setdefault("triggers_fired", [])

    for r in list(world.relations.values()):
        if r.type != RelationType.TRIGGER:
            continue
        speaker = world.get(r.ent1)
        if speaker is None:
            continue

        # ── Resurrection (number == -1) ───────────────────────────
        if r.number == -1:
            if speaker.hp is not None and speaker.hp == 0 and speaker.hp_max is not None:
                speaker.hp = speaker.hp_max
                # Reset threshold triggers so the despair arc repeats next life
                reset_ids = [
                    tr.id for tr in world.relations.values()
                    if tr.type == RelationType.TRIGGER
                    and tr.ent1 == r.ent1
                    and tr.number > 0
                    and tr.id in fired
                ]
                for tid in reset_ids:
                    fired.remove(tid)
                line = _get_dialogue(world, r.ent2)
                suffix = f" | \"{line}\"" if line else ""
                log.append(f"[RESURRECT] {speaker.name} 0 -> {speaker.hp_max} HP{suffix}")
            continue

        # ── Ambient (number == 0) ─────────────────────────────────
        if r.number == 0:
            if r.lambda_ > 0 and random.random() < r.lambda_:
                line = _get_dialogue(world, r.ent2)
                if line:
                    log.append(f"{speaker.name}: \"{line}\"")
            continue

        # ── HP-threshold, fire-once (number > 0) ─────────────────
        if r.id in fired:
            continue
        if speaker.hp is None or speaker.hp > r.number:
            continue

        # Probability via normal CDF: p = Phi((threshold - hp) / sigma)
        if r.lambda_ > 0:
            z = (r.number - speaker.hp) / r.lambda_
            p = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
        else:
            p = 1.0  # No sigma = always fire when threshold is crossed

        if random.random() < p:
            fired.append(r.id)
            line = _get_dialogue(world, r.ent2)
            if line:
                log.append(f"{speaker.name}: \"{line}\"  [HP {speaker.hp} <= {r.number}]")

    return log


# ── Intent pipeline ──────────────────────────────────────────────────────────

_SURVIVAL_THRESHOLD = 0.8   # EAT when hp / hp_max falls below this


def _find_food_in_inventory(world: World, actor_id: str) -> Entity | None:
    """Return the first SUMS item in actor's direct inventory with nutritional value (hp_max > 0)."""
    for entity, qty in world.children(actor_id):
        if entity.type == EntityType.SUMS and entity.hp_max and qty > 0:
            return entity
    return None


def _actor_categories(world: World, actor_id: str) -> set[str]:
    """Return the set of TYPE_OF category strings for this actor."""
    return {
        r.ent2 for r in world.relations.values()
        if r.type == RelationType.TYPE_OF and r.ent1 == actor_id and r.ent2 is not None
    }


def _edge_allows(world: World, from_id: str, to_id: str, actor_id: str) -> bool:
    """Return True if at least one EDGE permits actor to move from from_id to to_id.

    Checks direction (one_way) and deny (TYPE_OF category restriction).
    """
    actor_cats = _actor_categories(world, actor_id)
    for r in world.relations.values():
        if r.type != RelationType.EDGE:
            continue
        if r.ent1 == from_id and r.ent2 == to_id:
            pass  # forward direction
        elif r.ent2 == from_id and r.ent1 == to_id and not r.one_way:
            pass  # reverse direction, bidirectional edge
        else:
            continue
        if r.deny is not None and r.deny in actor_cats:
            continue  # this edge denies the actor — try next
        return True
    return False


def _find_healing_envi(world: World, actor_id: str) -> Entity | None:
    """Return a reachable ENVI (via EDGE) that provides net healing for this actor.

    Reachable means: connected to the actor's current ENVI by an EDGE that allows
    this actor (respects one_way and deny).
    Healing means: the candidate ENVI (or one of its TYPE_OF categories) has at
    least one BEHAVIOR with a negative rate (drain < 0).
    """
    current_loc = world.location_of(actor_id)
    if current_loc is None or current_loc.type != EntityType.ENVI:
        return None

    # Collect entity IDs that carry a net-healing BEHAVIOR (negative rate)
    healing_sources: set[str] = {
        r.ent1 for r in world.relations.values()
        if r.type == RelationType.BEHAVIOR and r.number < 0
    }

    # Walk all EDGE relations touching current_loc
    actor_cats = _actor_categories(world, actor_id)
    for r in world.relations.values():
        if r.type != RelationType.EDGE:
            continue
        if r.ent1 == current_loc.id:
            target_id = r.ent2
        elif r.ent2 == current_loc.id and not r.one_way:
            target_id = r.ent1
        else:
            continue
        if r.deny is not None and r.deny in actor_cats:
            continue  # actor denied on this edge
        if target_id is None:
            continue
        candidate = world.get(target_id)
        if candidate is None or candidate.type != EntityType.ENVI:
            continue
        # Direct healing on this ENVI, or via its TYPE_OF categories
        candidate_sources = {candidate.id} | {
            r2.ent2 for r2 in world.relations.values()
            if r2.type == RelationType.TYPE_OF and r2.ent1 == candidate.id
        }
        if candidate_sources & healing_sources:
            return candidate
    return None


def _survival_brain(world: World, entity: Entity) -> list[Intent]:
    """Generate intents for a CHAR in survival mode.

    Priority order:
      1. EAT — food already in inventory (SUMS with hp_max > 0)
      2. MOVE — towards a sibling ENVI that has a healing BEHAVIOR
    Only fires when hp < SURVIVAL_THRESHOLD * hp_max.
    """
    if entity.hp is None or entity.hp_max is None or entity.hp_max == 0:
        return []
    if entity.hp / entity.hp_max >= _SURVIVAL_THRESHOLD:
        return []

    urgency = 1.0 - entity.hp / entity.hp_max

    food = _find_food_in_inventory(world, entity.id)
    if food is not None:
        return [Intent(actor_id=entity.id, action="EAT", target_id=food.id, weight=urgency)]

    healing = _find_healing_envi(world, entity.id)
    if healing is not None:
        return [Intent(actor_id=entity.id, action="MOVE", target_id=healing.id, weight=urgency)]

    return []


def _collect_intents(world: World) -> list[Intent]:
    """Ask every active CHAR for its intent this tick."""
    intents: list[Intent] = []
    for entity in world.entities.values():
        if entity.type != EntityType.CHAR or entity.control is None:
            continue
        match entity.control:
            case "survival":
                intents.extend(_survival_brain(world, entity))
            case "player" | "rand" | _:
                pass   # stubs — future iterations
    return intents


def _execute_intents(world: World, intents: list[Intent]) -> list[str]:
    """Execute collected intents and return log messages.

    EAT  — consume 1 unit of a SUMS item from inventory; restore hp_max // 4 HP.
    MOVE — relocate actor to target ENVI (validated by world.move()).
    """
    log: list[str] = []
    for intent in intents:
        actor = world.get(intent.actor_id)
        if actor is None:
            continue

        if intent.action == "EAT":
            item = world.get(intent.target_id)
            if item is None or item.hp_max is None:
                continue
            loc_rel = next(
                (r for r in world.relations.values()
                 if r.type == RelationType.LOCATION
                 and r.ent1 == intent.actor_id and r.ent2 == intent.target_id),
                None,
            )
            if loc_rel is None or loc_rel.number <= 0:
                continue
            restore = max(1, item.hp_max // 4)
            old_hp = actor.hp
            actor.hp = min(actor.hp_max, actor.hp + restore)
            loc_rel.number -= 1
            note = " [last]" if loc_rel.number == 0 else f" x{loc_rel.number} left"
            if loc_rel.number == 0:
                del world.relations[loc_rel.id]
            log.append(
                f"{actor.name}: EAT {item.name}{note}  "
                f"(+{restore} HP  {old_hp} -> {actor.hp})"
            )

        elif intent.action == "MOVE":
            target = world.get(intent.target_id)
            if target is None:
                continue
            current_loc = world.location_of(intent.actor_id)
            if current_loc is None or not _edge_allows(world, current_loc.id, intent.target_id, intent.actor_id):
                continue  # no valid EDGE or actor denied
            try:
                world.move(intent.actor_id, intent.target_id)
                log.append(f"{actor.name}: MOVE -> {target.name}")
            except ValueError:
                pass   # containment or capacity violation — silently skip

    return log


def _in_graveyard(world: World, entity_id: str) -> bool:
    """Return True if entity_id resides in an ENVI marked TYPE_OF GRAVEYARD."""
    location = world.location_of(entity_id)
    if location is None:
        return False
    return any(
        r.type == RelationType.TYPE_OF and r.ent1 == location.id and r.ent2 == "Graveyards"
        for r in world.relations.values()
    )


def tick(world: World) -> list[str]:
    """
    Advance the world by one tick.
    Returns a list of human-readable log messages describing what happened.
    """
    log: list[str] = []

    log += _process_produce(world)
    log += _process_sums_hp(world)

    for entity in list(world.entities.values()):
        if entity.hp is None:
            continue  # Entity has no HP — skip
        if entity.type == EntityType.SUMS:
            continue  # SUMS HP is per-LOCATION; handled by _process_sums_hp

        # Graveyard rule: any entity inside a GRAVEYARD-typed ENVI loses all HP instantly.
        if entity.hp > 0 and _in_graveyard(world, entity.id):
            entity.hp = 0
            log.append(f"{entity.name}: captured — HP -> 0  [GRAVEYARD]")
            continue

        behaviors = _collect_behaviors(world, entity.id)
        if not behaviors:
            continue

        total_drain = sum(rate for _, rate in behaviors)
        if total_drain == 0:
            continue

        old_hp = entity.hp
        cap = entity.hp_max if entity.hp_max is not None else entity.hp
        entity.hp = max(0, min(cap, entity.hp - total_drain))

        if entity.hp != old_hp:
            causes = "+".join(name for name, _ in behaviors)
            suffix = " [DEAD]" if entity.hp == 0 else ""
            log.append(f"{entity.name}: HP {old_hp} -> {entity.hp}  [{causes}]{suffix}")

    intents = _collect_intents(world)
    log += _execute_intents(world, intents)

    log += _process_triggers(world)
    return log
