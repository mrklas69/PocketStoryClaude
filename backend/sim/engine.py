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

from backend.core.world import World
from backend.core.entity import EntityType
from backend.core.relation import Relation, RelationType


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

    log += _process_triggers(world)
    return log
