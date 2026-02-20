# DONE — PocketStory

Archiv dokončených úkolů. Přesunuto z TODO.md.

---

## Concept & Design

- Define the "world" — what lives in it? entities, relations, intents

## Tech

- Choose platform → web (+ console for dev, engine later)
- Choose tech stack → Python + FastAPI + SQLite + Three.js
- Set up project structure (backend / frontend / core / sim)
- Set up Python virtual environment
- Install FastAPI, rich

## Data Model

- Entity class + EntityType enum (ENVI, CHAR, UNIQUE, SUMS)
- Entity attributes: id, name, description, type, number, capacity, rank, hp, hp_max
- Entity attributes: `nature: Optional[int]` — innate essence/charge (−10000 dark ↔ +10000 light)
- Entity attributes: `karma: Optional[int]` — accumulated consequence of actions (CHAR only)
- Relation class + RelationType (LOCATION, SKILL, TYPE_OF, BEHAVIOR)
- World class (entity + relation manager, load/save JSON)
- `World.move(entity, container, amount?)` — relocate entity; SUMS partial move + merge; CHAR can carry CHAR
- `World.location_of(entity)` — return direct parent container
- CONTAINMENT_RULES: CHAR→CHAR allowed; UNIQUE→UNIQUE+SUMS allowed (capacity required)
- `World.remove()` — remove entity + its relations

## Simulation

- `backend/sim/tick.py` — BEHAVIOR engine: všechny typy behaviors, tři zdroje (entity-specific, TYPE_OF cascade, location-based), hp_max cap, GRAVEYARD instant kill

## Presentation: Console

- `console.py` — live `rich.Live` dashboard, HP bars, tick log, `--ticks`/`--delay`/`--full` CLI args
- Entity type colours (blue/cyan/magenta/white); short/full mode
- Archetype description lookup via TYPE_OF chain (`_archetype_desc`)
- UNIQUE archetype roots hidden in normal mode, visible in `--full` mode

## Core Features

- Save / load — `World.save()` / `World.load()` for JSON

## Worlds

- `worlds/polar_night.json` — Chronicle of the Polar Night Dynasty (narativ, hierarchie prostorů, CHAR→CHAR, Wildfire Oil)
- `worlds/math_universe.json` — Mathematical Universe (abstraktní entity, kategoriální entropie)
- `worlds/royal_chess.json` — Royal Chess (32 figur, 64 políček, 7 archetypů figur, HP systém)
- `worlds/genesis.json` — Genesis (Bůh + padlý anděl Felix; creation story; Felix cyklicky klesá na 0 a Bůh ho vzkřísí)

## Royal Chess — MVP design decisions

- Pravidla: standardní FIDE (mat, pat, opakování, remíza dohodou)
- Braní: přesun figury na pole soupeře (standard)
- Čas: tick-based; hráč čeká na tah soupeře → ticky využívá výrobou/sběrem
- Dynamit: náhodně se objeví na políčku, nelze vyrábět

## Documentation

- `GLOSSARY.md` — kanonické názvosloví projektu (EntityType vs kategorie, prototype inheritance)
- Archetype entities přidány do všech světů (polar_night, math_universe, royal_chess)

---

*Last updated: 2026-02-20*
