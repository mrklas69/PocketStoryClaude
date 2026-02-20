from enum import Enum
from typing import Optional


class RelationType(Enum):
    LOCATION = "LOCATION"  # ENT1 contains ENT2; NUMBER = current quantity (dynamic state)
    SKILL    = "SKILL"     # ENT1 has skill ENT2 at level/capacity NUMBER
    TYPE_OF  = "TYPE_OF"   # ENT1 belongs to category ENT2 (string code)
    BEHAVIOR = "BEHAVIOR"  # ENT1 (entity or category) has behavior ENT2; NUMBER = intensity/rate
    PRODUCE  = "PRODUCE"   # ENT1 produces ENT2 each tick; NUMBER = fixed yield OR LAMBDA = Poisson parameter


class Relation:
    def __init__(
        self,
        id: int,
        type: RelationType,
        ent1: str,
        ent2: Optional[str] = None,
        number: int = 1,
        lambda_: float = 0.0,
    ):
        self.id: int = id
        self.type: RelationType = type
        self.ent1: str = ent1
        self.ent2: Optional[str] = ent2  # None for unary relations
        self.number: int = number
        self.lambda_: float = lambda_    # Poisson λ for stochastic production

    def __repr__(self) -> str:
        return f"Relation({self.type.value}, id={self.id}, {self.ent1!r} → {self.ent2!r}, n={self.number})"
