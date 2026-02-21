from enum import Enum
from typing import Optional


class RelationType(Enum):
    LOCATION = "LOCATION"  # ENT1 contains ENT2; NUMBER = current quantity (dynamic state)
    TYPE_OF  = "TYPE_OF"   # ENT1 belongs to category ENT2 (string code)
    SKILL    = "SKILL"     # ENT1 has skill ENT2 at level/capacity NUMBER
    BEHAVIOR = "BEHAVIOR"  # ENT1 (entity or category) has behavior ENT2; NUMBER = intensity/rate
    PRODUCE  = "PRODUCE"   # ENT1 produces ENT2 each tick; NUMBER = fixed yield OR LAMBDA = Poisson parameter
    TRIGGER  = "TRIGGER"   # ENT1 = speaker/subject, ENT2 = dialogue entity, NUMBER = hp threshold (>0 fire-once, 0=ambient, -1=resurrection), LAMBDA = sigma (threshold) or probability (ambient)
    EDGE     = "EDGE"      # ENT1 and ENT2 are adjacent ENVIs; NUMBER = distance/cost (0 = immediate); WAY = route type (road/sea/air/…); bidirectional by default


class Relation:
    def __init__(
        self,
        id: int,
        type: RelationType,
        ent1: str,
        ent2: Optional[str] = None,
        number: int = 1,
        lambda_: float = 0.0,
        hp: Optional[int] = None,
        way: Optional[str] = None,
        one_way: bool = False,
        deny: Optional[str] = None,
    ):
        self.id: int = id
        self.type: RelationType = type
        self.ent1: str = ent1
        self.ent2: Optional[str] = ent2  # None for unary relations
        self.number: int = number
        self.lambda_: float = lambda_    # Poisson λ for stochastic production
        self.hp: Optional[int] = hp      # LOCATION only: current freshness/durability of this stack (SUMS)
        self.way: Optional[str] = way    # EDGE only: route type (road, sea, air, …)
        self.one_way: bool = one_way     # EDGE only: if True, only ent1→ent2 is traversable
        self.deny: Optional[str] = deny  # EDGE only: TYPE_OF category string denied passage

    def __repr__(self) -> str:
        return f"Relation({self.type.value}, id={self.id}, {self.ent1!r} → {self.ent2!r}, n={self.number}, λ={self.lambda_})"
