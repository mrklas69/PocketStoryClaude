"""
Simulation tick engine.

Each call to tick(world) advances time by one step and applies all BEHAVIOR
effects to entities that have them — either directly, or inherited via TYPE_OF.

BEHAVIOR lookup order:
  1. BEHAVIOR relation where ent1 == entity.id  (entity-specific override)
  2. BEHAVIOR relation where ent1 == category   (for each TYPE_OF category)

DECAY behavior:
  Reduces hp of the target entity by the behavior's NUMBER per tick.
  When hp reaches 0 the entity is considered spoiled / dead.
"""

from backend.core.world import World
from backend.core.relation import RelationType


def _get_behavior(world: World, entity_id: str, behavior_name: str) -> int | None:
    """
    Return the intensity (NUMBER) of a named behavior for an entity,
    looking first at entity-specific rules then at TYPE_OF categories.
    Returns None if no matching behavior is found.
    """
    # 1. Entity-specific BEHAVIOR
    for r in world.relations.values():
        if (r.type == RelationType.BEHAVIOR
                and r.ent1 == entity_id
                and r.ent2 == behavior_name):
            return r.number

    # 2. Inherited via TYPE_OF categories
    categories = [
        r.ent2 for r in world.relations.values()
        if r.type == RelationType.TYPE_OF and r.ent1 == entity_id
    ]
    for category in categories:
        for r in world.relations.values():
            if (r.type == RelationType.BEHAVIOR
                    and r.ent1 == category
                    and r.ent2 == behavior_name):
                return r.number

    return None


def tick(world: World) -> list[str]:
    """
    Advance the world by one tick.
    Returns a list of human-readable log messages describing what happened.
    """
    log: list[str] = []

    for entity in list(world.entities.values()):
        if entity.hp is None:
            continue  # Entity doesn't have HP — skip

        decay = _get_behavior(world, entity.id, "DECAY")
        if decay is None:
            continue

        old_hp = entity.hp
        entity.hp = max(0, entity.hp - decay)

        if entity.hp < old_hp:
            log.append(
                f"{entity.name}: HP {old_hp} -> {entity.hp}"
                + (" [SPOILED]" if entity.hp == 0 else "")
            )

    return log
