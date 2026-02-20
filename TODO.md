# TODO — PocketStory

## Legend
- `[ ]` — not started
- `[~]` — in progress

Dokončené úkoly → [DONE.md](DONE.md) | Nápady → [IDEAS.md](IDEAS.md)

---

## Concept & Design

- `[~]` Define core game loop (what does the player actually do?)
- `[ ]` Define win/lose conditions (or is it endless?)
- `[ ]` Sketch basic UI concept

## Data Model

- `[ ]` Prototype inheritance: `World.resolve_attr(entity, attr)` — reads entity's own value; if `None`, walks TYPE_OF chain and returns first non-None value from archetype; enables sparse entity definitions
- `[ ]` RelationType: add CONSUME (recipe engine — vstupy → výstupy)

## Simulation

- `[~]` World simulation loop (tick-based) — BEHAVIOR + PRODUCE working; full Intent pipeline pending
- `[ ]` Intent dataclass (actor, action, target, weight)
- `[ ]` `tick()` full pipeline: collect → validate → resolve → execute → chain
- `[ ]` Intent generators per entity type (CHAR, ENVI, UNIQUE, SUMS)
- `[ ]` Conflict resolution via `rank` + skill check

## Core Features

- `[ ]` Player interactions

## Presentation

- `[ ]` **Web** — Three.js frontend
- `[ ]` **Engine** — Godot / Unity (future)

## Worlds

- `[ ]` `worlds/terrarium.json` — The Terrarium (ekosystém bez lidí, PRODUCE/CONSUME, predátor/kořist) — čeká na recipe engine

## Royal Chess — MVP

- `[ ]` Akce: hráč nebo jednoduchý chess engine skript

---

*Last updated: 2026-02-21 (TRIGGER done)*
