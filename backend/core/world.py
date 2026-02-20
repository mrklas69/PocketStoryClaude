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
            # UNIQUE entity is only a container when capacity is explicitly set
            if parent.type == EntityType.UNIQUE and parent.capacity is None:
                raise ValueError(
                    f"UNIQUE '{parent.name}' has no capacity — not a container"
                )
            _OCCUPANT_TYPES = {EntityType.CHAR, EntityType.UNIQUE, EntityType.SUMS}
            if parent.capacity is not None and child.type in _OCCUPANT_TYPES:
                used = sum(
                    1 for e, _ in self.children(relation.ent1)
                    if e.type in _OCCUPANT_TYPES
                )
                if used >= parent.capacity:
                    raise ValueError(
                        f"'{parent.name}' is full ({used}/{parent.capacity} slots)"
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

    def _next_relation_id(self) -> int:
        return max(self.relations.keys(), default=0) + 1

    def location_of(self, entity_id: str) -> Entity | None:
        """Return the direct parent container of entity_id, or None if it is a root."""
        for r in self.relations.values():
            if r.type == RelationType.LOCATION and r.ent2 == entity_id:
                return self.entities.get(r.ent1)
        return None

    def remove(self, entity_id: str) -> None:
        """Remove entity and all relations that reference it.

        Children (entities located inside this one) become roots — they are not
        deleted, just no longer contained anywhere.
        """
        if entity_id not in self.entities:
            raise ValueError(f"Entity '{entity_id}' not found")
        to_delete = [
            rid for rid, r in self.relations.items()
            if r.ent1 == entity_id or r.ent2 == entity_id
        ]
        for rid in to_delete:
            del self.relations[rid]
        del self.entities[entity_id]

    def move(self, entity_id: str, new_container_id: str, amount: int | None = None) -> None:
        """Move entity to a new container.

        Rules:
        - Containment rules are enforced (see CONTAINMENT_RULES in entity.py).
        - UNIQUE acting as container requires capacity to be set.
        - For SUMS: amount is required.  Partial moves split the stack in place
          (source quantity reduced; target quantity increased or new relation created).
        - CHAR can be placed inside another CHAR (carry a companion or pet).
        - Capacity of the target is checked for UNIQUE and SUMS children.
        """
        entity = self.entities.get(entity_id)
        if entity is None:
            raise ValueError(f"Entity '{entity_id}' not found")
        new_container = self.entities.get(new_container_id)
        if new_container is None:
            raise ValueError(f"Container '{new_container_id}' not found")
        if entity_id == new_container_id:
            raise ValueError("Entity cannot contain itself")

        # Containment rule
        if not can_contain(new_container.type, entity.type):
            raise ValueError(
                f"{new_container.type.value} cannot contain {entity.type.value} "
                f"('{new_container.name}' ← '{entity.name}')"
            )
        if new_container.type == EntityType.UNIQUE and new_container.capacity is None:
            raise ValueError(f"UNIQUE '{new_container.name}' has no capacity — not a container")

        # Find existing source LOCATION relation
        source_rel = next(
            (r for r in self.relations.values()
             if r.type == RelationType.LOCATION and r.ent2 == entity_id),
            None,
        )

        if entity.type == EntityType.SUMS:
            if amount is None:
                raise ValueError(f"Moving SUMS '{entity.name}' requires an amount")
            src_qty = source_rel.number if source_rel is not None else 0
            if amount > src_qty:
                raise ValueError(
                    f"Cannot move {amount} × '{entity.name}' — only {src_qty} available"
                )
            # Reduce or remove source relation
            if source_rel is not None:
                if amount == src_qty:
                    del self.relations[source_rel.id]
                else:
                    source_rel.number -= amount
            # Merge into existing target relation, or create a new one
            target_rel = next(
                (r for r in self.relations.values()
                 if r.type == RelationType.LOCATION
                 and r.ent1 == new_container_id and r.ent2 == entity_id),
                None,
            )
            if target_rel is not None:
                target_rel.number += amount
            else:
                self.add_relation(Relation(
                    id=self._next_relation_id(),
                    type=RelationType.LOCATION,
                    ent1=new_container_id,
                    ent2=entity_id,
                    number=amount,
                ))

        else:
            # UNIQUE / CHAR / ENVI — simple single-location move
            # Capacity check: CHAR + UNIQUE + SUMS count as occupants; ENVI is structural
            _OCCUPANT_TYPES = {EntityType.CHAR, EntityType.UNIQUE, EntityType.SUMS}
            if new_container.capacity is not None and entity.type in _OCCUPANT_TYPES:
                used = sum(
                    1 for e, _ in self.children(new_container_id)
                    if e.type in _OCCUPANT_TYPES
                )
                if used >= new_container.capacity:
                    raise ValueError(
                        f"'{new_container.name}' is full ({used}/{new_container.capacity} slots)"
                    )
            if source_rel is not None:
                source_rel.ent1 = new_container_id
            else:
                self.add_relation(Relation(
                    id=self._next_relation_id(),
                    type=RelationType.LOCATION,
                    ent1=new_container_id,
                    ent2=entity_id,
                ))

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
    if e.nature is not None:
        d["nature"] = e.nature
    if e.karma is not None:
        d["karma"] = e.karma
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
        nature=d.get("nature"),
        karma=d.get("karma"),
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
