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

from backend.core.world import World
from backend.core.relation import RelationType


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
        r.type == RelationType.TYPE_OF and r.ent1 == location.id and r.ent2 == "GRAVEYARD"
        for r in world.relations.values()
    )


def tick(world: World) -> list[str]:
    """
    Advance the world by one tick.
    Returns a list of human-readable log messages describing what happened.
    """
    log: list[str] = []

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
