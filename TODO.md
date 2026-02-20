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
- `[x]` **Data Model** — `World.move(entity, container, amount?)` — relocate entity; SUMS partial move + merge; CHAR can carry CHAR
- `[x]` **Data Model** — `World.location_of(entity)` — return direct parent container
- `[x]` **Data Model** — CONTAINMENT_RULES: CHAR→CHAR allowed; UNIQUE→UNIQUE+SUMS allowed (capacity required)
- `[x]` **Data Model** — `World.remove()` — remove entity + its relations
- `[?]` **Data Model** — `proto_id` for SUMS (mergeable stacks) — revisit after move/remove
- `[ ]` **Data Model** — Prototype inheritance: `World.resolve_attr(entity, attr)` — reads entity's own value; if `None`, walks TYPE_OF chain and returns first non-None value from archetype; enables sparse entity definitions (instance overrides only what differs from archetype)
- `[x]` **Simulation** — `backend/sim/tick.py` — BEHAVIOR engine: všechny typy behaviors, tři zdroje (entity-specific, TYPE_OF cascade, location-based), hp_max cap, GRAVEYARD instant kill
- `[ ]` **Simulation** — `tick()`: PRODUCE/CONSUME processing (recipe engine)
- `[ ]` **Simulation** — Intent dataclass (actor, action, target, weight)
- `[ ]` **Simulation** — `tick()` full pipeline: collect → validate → resolve → execute → chain
- `[ ]` **Simulation** — Intent generators per entity type (CHAR, ENVI, UNIQUE, SUMS)
- `[ ]` **Simulation** — Conflict resolution via `rank` + skill check
- `[x]` **Presentation: Console** — `console.py` — live `rich.Live` dashboard, HP bars, tick log, `--ticks`/`--delay`/`--full` CLI args; entity type colours (blue/cyan/magenta/white); short/full mode
- `[ ]` **Presentation: Web** — Three.js frontend
- `[ ]` **Presentation: Engine** — Godot / Unity (future)

## Core Features

- `[~]` World simulation loop (tick-based) — DECAY working; full Intent pipeline pending
- `[ ]` Player interactions
- `[x]` Save / load — `World.save()` / `World.load()` for JSON

## Worlds

- `[x]` `worlds/polar_night.json` — Chronicle of the Polar Night Dynasty (narativ, hierarchie prostorů, CHAR→CHAR, Wildfire Oil)
- `[x]` `worlds/math_universe.json` — Mathematical Universe (abstraktní entity, kategoriální entropie)
- `[x]` `worlds/royal_chess.json` — Royal Chess Fragment (mechanika, capacity, location TYPE_OF cascade, Endurance Chess)
- `[x]` `worlds/genesis.json` — Genesis (Bůh + padlý anděl Felix; creation story; Felix cyklicky klesá na 0 a Bůh ho vzkřísí)
- `[ ]` `worlds/terrarium.json` — The Terrarium (ekosystém bez lidí, PRODUCE/CONSUME, predátor/kořist) — čeká na recipe engine

## Royal Chess — MVP

- `[x]` Pravidla: standardní FIDE (mat, pat, opakování, remíza dohodou)
- `[x]` Braní: přesun figury na pole soupeře (standard)
- `[x]` Čas: tick-based; hráč čeká na tah soupeře → ticky využívá výrobou/sběrem
- `[ ]` Akce: hráč nebo jednoduchý chess engine skript
- `[x]` Dynamit: náhodně se objeví na políčku, nelze vyrábět

## Royal Chess — budoucí iterace

- `[?]` Jednoduchý chess engine (minimax nebo pravidlový skript pro NPC tahy)
- `[?]` Výrobní ekonomika: šípy, recyklace slonoviny, seno pro koně — výroba čeká na PRODUCE/CONSUME
- `[?]` Pravidla spawnu dynamitu (frekvence, podmínky, maximální počet na šachovnici)
- `[?]` Formační bonusy (figury blízko u sebe = nižší entropie)
- `[?]` Domácí čtverec: každá figura zná svůj home square, vzdálenost od home = entropie
- `[?]` Fog of War: hráč vidí jen políčka, kam dohlédnou jeho figury (každý typ figury = jiný dosah výhledu)

## Side projects

- `[?]` **Awakened Chess** — standalone projekt; figury znají svůj domácí čtverec, vzdálenost = entropie, formační bonusy; engine PocketStory je unese přirozeně

## Planned attributes

- `[x]` **Entity** — `nature: Optional[int]` — innate essence/charge (-10000 dark ↔ +10000 light); None = neutral
  - Any entity type: Freya's kitten = +90, Edgar's cursed sword = -85, a coin = None
  - Changes rarely (cursed, blessed); can spread via BEHAVIOR (CURSED → KARMA_DRAIN on carrier)
- `[x]` **Entity (CHAR only)** — `karma: Optional[int]` — accumulated consequence of actions; None = N/A
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
