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
      - lambda > 0  → stochastic: draw from Poisson(lambda), capped at max_yield
      - lambda == 0 → deterministic: fixed yield equal to number
    Stock cap (optional): if both producer.capacity and item.capacity are set,
    total stock is capped at producer.capacity × item.capacity.
    """
    log: list[str] = []
    produce_rels = [r for r in world.relations.values() if r.type == RelationType.PRODUCE]
    for r in produce_rels:
        amount = _poisson(r.lambda_) if r.lambda_ > 0 else r.number
        if amount == 0:
            continue

        producer = world.get(r.ent1)
        item = world.get(r.ent2)

        # Find existing LOCATION(ent1 → ent2) to read current stock.
        loc = next(
            (l for l in world.relations.values()
             if l.type == RelationType.LOCATION and l.ent1 == r.ent1 and l.ent2 == r.ent2),
            None,
        )
        current = loc.number if loc is not None else 0

        # Cap: producer.capacity × item.capacity (only when both are defined).
        if (producer is not None and item is not None
                and producer.capacity is not None and item.capacity is not None):
            stock_cap = producer.capacity * item.capacity
            amount = min(amount, stock_cap - current)

        if amount <= 0:
            continue

        if loc is not None:
            loc.number += amount
        else:
            new_id = max(world.relations.keys(), default=0) + 1
            world.relations[new_id] = Relation(
                id=new_id,
                type=RelationType.LOCATION,
                ent1=r.ent1,
                ent2=r.ent2,
                number=amount,
            )
        log.append(f"{producer.name}: +{amount} {item.name}")
    return log


def _collect_behaviors(world: World, entity_id: str) -> list[tuple[str, int]]:
    """
    Return all (behavior_name, rate) pairs active for entity_id.

    Four sources (applied in order, all summed):
      1. Entity-specific BEHAVIOR relations (direct override).
      2. TYPE_OF category cascade — behaviors on each category the entity belongs to.
      3. Location-direct — BEHAVIOR on the specific ENVI the entity currently occupies.
      4. Location-category cascade — BEHAVIOR on TYPE_OF categories of that ENVI
         (e.g. TYPE_OF(D1, HOME_SQUARE) + BEHAVIOR(HOME_SQUARE, RECHARGE, -5)).
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
    location = world.location_of(entity_id)
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

    for entity in list(world.entities.values()):
        if entity.hp is None:
            continue  # Entity has no HP — skip

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

    return log
