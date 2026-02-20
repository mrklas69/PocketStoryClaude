from enum import Enum
from uuid import uuid4
from typing import Optional


class EntityType(Enum):
    ENVI   = "ENVI"    # Prostředí, kontejnery (obsahují enatity) NUMBER = max. počet slotů ~ Kulisy
    CHAR   = "CHAR"    # Hráči, NPC, démoni (autonomní entitiy) ~ Herci
    UNIQUE = "UNIQUE"  # Unikátní objekty, předměty — unique item (cannot stack) CAPACITY = 1 ~ Rekvizity
    SUMS   = "SUMS"    # Hromadné objekty, zdroje (lze stackovat) CAPACITY = max. počet slotů v jednom stacku ~ Rekvizity


# Containment rules: which entity types can be children of which
# (validated on every LOCATION relation; see also World.move())
#
#   ENVI   → anything (rooms hold everything)
#   CHAR   → CHAR (carry a companion/kitten), UNIQUE, SUMS (inventory)
#   UNIQUE → UNIQUE, SUMS — only when capacity is explicitly set (backpack, chest)
#   SUMS   → nothing (a pile of coins cannot hold things)
CONTAINMENT_RULES: dict[EntityType, set[EntityType]] = {
    EntityType.ENVI:   {EntityType.ENVI, EntityType.CHAR, EntityType.UNIQUE, EntityType.SUMS},
    EntityType.CHAR:   {EntityType.CHAR, EntityType.UNIQUE, EntityType.SUMS},
    EntityType.UNIQUE: {EntityType.UNIQUE, EntityType.SUMS},
    EntityType.SUMS:   set(),
}


def can_contain(parent_type: EntityType, child_type: EntityType) -> bool:
    return child_type in CONTAINMENT_RULES.get(parent_type, set())


def _new_id() -> str:
    return uuid4().hex[:8]


class Entity:
    def __init__(
        self,
        name: str,
        type: EntityType,
        description: Optional[str] = None,
        number: int = 1,
        capacity: Optional[int] = None,
        id: Optional[str] = None,
        rank: int = 1,
        hp: Optional[int] = None,
        hp_max: Optional[int] = None,
    ):
        self.id: str = id or _new_id()
        self.name: str = name
        self.description: Optional[str] = description
        self.type: EntityType = type
        self.number: int = number
        # SUMS only: max stack size per slot (static property of the item type).
        # The actual current quantity is stored in the LOCATION relation, not here.

        self.capacity: Optional[int] = capacity
        # ENVI only: max number of item slots (counts only UNIQUE + SUMS children).
        # CHAR and ENVI children are free and do not count toward capacity.

        self.rank: int = rank
        # Conflict resolution weight — higher rank wins intent disputes.

        self.hp: Optional[int] = hp
        self.hp_max: Optional[int] = hp_max
        # Current / maximum health (freshness, durability...). None = not applicable.

    def __repr__(self) -> str:
        return f"Entity({self.type.value}, id={self.id!r}, name={self.name!r})"
