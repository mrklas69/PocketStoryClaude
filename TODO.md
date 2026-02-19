# TODO — PocketStory

## Legend
- `[ ]` — not started
- `[~]` — in progress
- `[x]` — done
- `[?]` — idea / under consideration

---

## Concept & Design

- `[~]` Define core game loop (what does the player actually do?)
- `[x]` Define the "world" — what lives in it? entities, relations, intents
- `[ ]` Define win/lose conditions (or is it endless?)
- `[ ]` Sketch basic UI concept
- `[?]` Name — confirm "PocketStory" or choose alternative

## Tech

- `[x]` Choose platform → web (+ console for dev, engine later)
- `[x]` Choose tech stack → Python + FastAPI + SQLite + Three.js
- `[x]` Set up project structure (backend / frontend / core / sim)
- `[x]` Set up Python virtual environment
- `[x]` Install FastAPI, rich

## Architecture Layers

- `[x]` **Data Model** — Entity class + EntityType enum (ENVI, CHAR, UNIQUE, SUMS)
- `[x]` **Data Model** — Entity attributes: id, name, description, type, number, capacity, rank, hp, hp_max
- `[x]` **Data Model** — Relation class + RelationType (LOCATION, SKILL, TYPE_OF, BEHAVIOR)
- `[ ]` **Data Model** — RelationType: add PRODUCE + CONSUME
- `[x]` **Data Model** — World class (entity + relation manager, load/save JSON)
- `[ ]` **Data Model** — `World.move()` — relocate entity (change LOCATION relation)
- `[ ]` **Data Model** — `World.remove()` — remove entity + its relations
- `[?]` **Data Model** — `proto_id` for SUMS (mergeable stacks) — revisit after move/remove
- `[x]` **Simulation** — `backend/sim/tick.py` — DECAY behavior via BEHAVIOR + TYPE_OF cascade
- `[ ]` **Simulation** — `tick()`: PRODUCE/CONSUME processing (recipe engine)
- `[ ]` **Simulation** — Intent dataclass (actor, action, target, weight)
- `[ ]` **Simulation** — `tick()` full pipeline: collect → validate → resolve → execute → chain
- `[ ]` **Simulation** — Intent generators per entity type (CHAR, ENVI, UNIQUE, SUMS)
- `[ ]` **Simulation** — Conflict resolution via `rank` + skill check
- `[x]` **Presentation: Console** — `demo.py` — live `rich.Live` dashboard, HP bars, tick log, `--ticks`/`--delay` CLI args
- `[ ]` **Presentation: Web** — Three.js frontend
- `[ ]` **Presentation: Engine** — Godot / Unity (future)

## Core Features

- `[~]` World simulation loop (tick-based) — DECAY working; full Intent pipeline pending
- `[ ]` Player interactions
- `[x]` Save / load — `World.save()` / `World.load()` for JSON

## Next session — martian_saga expansion

- `[ ]` Add KITCHEN (ENVI) + CHARGING_STATION (ENVI inside KITCHEN) to martian_saga.json
- `[ ]` Add BEHAVIOR(HUMAN, HUNGER, 3) and BEHAVIOR(ANDROID, BATTERY_DRAIN, 5)
- `[ ]` Add BEHAVIOR(CHARGING_STATION, RECHARGE, 15) — env behavior, applies to ANDROID children
- `[ ]` Add GROW_TOMATOES recipe entity: PRODUCE(_, TOMATOES, 3), SKILL(GREENHOUSE, GROW_TOMATOES)
- `[ ]` Add EAT_TOMATO recipe entity: CONSUME(_, TOMATOES, 1), restores hp_max/4 HP to actor
- `[ ]` Iris in GREENHOUSE (has tomatoes, no eating → dies of hunger)
- `[ ]` Martian in STORAGE (not in KITCHEN → drains to 0)

## Planned attributes

- `[ ]` **Entity** — `nature: Optional[int]` — innate essence/charge (-100 dark ↔ +100 light); None = neutral
  - Any entity type: Freya's kitten = +90, Edgar's cursed sword = -85, a coin = None
  - Changes rarely (cursed, blessed); can spread via BEHAVIOR (CURSED → KARMA_DRAIN on carrier)
- `[ ]` **Entity (CHAR only)** — `karma: Optional[int]` — accumulated consequence of actions; None = N/A
  - Dynamic: grows/shrinks through deeds each tick or event
  - Interacts with nature: high-nature char gains karma faster; cursed item drains carrier's karma
  - Affects: conflict resolution odds, world reactions, story outcomes

## Nice to Have

- `[?]` Procedural story generation
- `[?]` Moods / personality traits for entities
- `[?]` Seasonal events
- `[?]` TRIGGER relation type (reactive rules: "checkmate → guard reaction")
- `[?]` FRIDGE / environment context modifying DECAY rate (needs ENT3 in Relation)

---

*Last updated: 2026-02-20*
