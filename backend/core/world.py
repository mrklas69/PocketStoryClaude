import json
from pathlib import Path

from .entity import Entity, EntityType, can_contain
from .relation import Relation, RelationType


class World:
    def __init__(self, name: str, description: str = ""):
        self.name: str = name
        self.description: str = description
        self.entities: dict[str, Entity] = {}
        self.relations: dict[int, Relation] = {}

    # ── Entity management ───────────────────────────────────────────────────

    def add_entity(self, entity: Entity) -> Entity:
        if entity.id in self.entities:
            raise ValueError(f"Entity id '{entity.id}' already exists in world")
        self.entities[entity.id] = entity
        return entity

    def add_relation(self, relation: Relation) -> Relation:
        # Uniqueness: (type, ent1, ent2)
        for r in self.relations.values():
            if r.type == relation.type and r.ent1 == relation.ent1 and r.ent2 == relation.ent2:
                raise ValueError(
                    f"Relation ({relation.type.value}, {relation.ent1!r}, {relation.ent2!r}) already exists"
                )
        # Validate LOCATION containment
        if relation.type == RelationType.LOCATION:
            parent = self.entities.get(relation.ent1)
            child  = self.entities.get(relation.ent2)
            if parent is None:
                raise ValueError(f"Entity '{relation.ent1}' not found")
            if child is None:
                raise ValueError(f"Entity '{relation.ent2}' not found")
            if not can_contain(parent.type, child.type):
                raise ValueError(
                    f"{parent.type.value} cannot contain {child.type.value} "
                    f"('{parent.name}' -> '{child.name}')"
                )
            if parent.capacity is not None and child.type in {EntityType.UNIQUE, EntityType.SUMS}:
                used = sum(
                    1 for e, _ in self.children(relation.ent1)
                    if e.type in {EntityType.UNIQUE, EntityType.SUMS}
                )
                if used >= parent.capacity:
                    raise ValueError(
                        f"'{parent.name}' is full ({used}/{parent.capacity} item slots)"
                    )
        self.relations[relation.id] = relation
        return relation

    def children(self, parent_id: str) -> list[tuple[Entity, int]]:
        result = []
        for r in self.relations.values():
            if r.type == RelationType.LOCATION and r.ent1 == parent_id:
                entity = self.entities.get(r.ent2)
                if entity:
                    result.append((entity, r.number))
        return result

    def roots(self) -> list[Entity]:
        in_location = {r.ent2 for r in self.relations.values() if r.type == RelationType.LOCATION}
        return [e for e in self.entities.values() if e.id not in in_location]

    def get(self, entity_id: str) -> Entity | None:
        return self.entities.get(entity_id)

    # ── Serialization ───────────────────────────────────────────────────────

    def save(self, path: str | Path) -> None:
        data = {
            "name": self.name,
            "description": self.description,
            "entities":  [_entity_to_dict(e)  for e in self.entities.values()],
            "relations": [_relation_to_dict(r) for r in self.relations.values()],
        }
        Path(path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "World":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        world = cls(data["name"], data.get("description", ""))

        ids = [e["id"] for e in data["entities"]]
        if len(ids) != len(set(ids)):
            raise ValueError("World file contains duplicate entity IDs")

        for ed in data["entities"]:
            entity = _dict_to_entity(ed)
            world.entities[entity.id] = entity

        for rd in data.get("relations", []):
            relation = _dict_to_relation(rd)
            world.relations[relation.id] = relation

        return world

    def __repr__(self) -> str:
        return f"World(name={self.name!r}, entities={len(self.entities)}, relations={len(self.relations)})"


# ── Helpers ─────────────────────────────────────────────────────────────────

def _entity_to_dict(e: Entity) -> dict:
    d: dict = {"id": e.id, "name": e.name, "type": e.type.value}
    if e.description is not None:
        d["description"] = e.description
    if e.number != 1:
        d["number"] = e.number
    if e.capacity is not None:
        d["capacity"] = e.capacity
    if e.rank != 1:
        d["rank"] = e.rank
    if e.hp is not None:
        d["hp"] = e.hp
    if e.hp_max is not None:
        d["hp_max"] = e.hp_max
    return d


def _dict_to_entity(d: dict) -> Entity:
    return Entity(
        id=d["id"],
        name=d["name"],
        type=EntityType(d["type"]),
        description=d.get("description"),
        number=d.get("number", 1),
        capacity=d.get("capacity"),
        rank=d.get("rank", 1),
        hp=d.get("hp"),
        hp_max=d.get("hp_max"),
    )


def _relation_to_dict(r: Relation) -> dict:
    d: dict = {"id": r.id, "type": r.type.value, "ent1": r.ent1}
    if r.ent2 is not None:
        d["ent2"] = r.ent2
    if r.number != 1:
        d["number"] = r.number
    return d


def _dict_to_relation(d: dict) -> Relation:
    return Relation(
        id=d["id"],
        type=RelationType(d["type"]),
        ent1=d["ent1"],
        ent2=d.get("ent2"),
        number=d.get("number", 1),
    )
