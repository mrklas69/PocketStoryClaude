# DONE — PocketStory

Archiv dokončených úkolů. Přesunuto z TODO.md.

---

## Data Model

- `World.resolve_attr(entity, attr)` — prototype inheritance: BFS po TYPE_OF řetězci; vrátí první non-None hodnotu z archetypu; umožňuje sparse entity definitions

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

## Data Model

- `Relation.hp: Optional[int]` — per-stack HP for SUMS entities (freshness/durability on LOCATION relation)

## Simulation

- `backend/sim/engine.py` (dříve `tick.py`) — BEHAVIOR engine + PRODUCE mechanic
- BEHAVIOR engine: všechny typy behaviors, čtyři zdroje (entity-specific, TYPE_OF cascade, location-direct, location-TYPE_OF), hp_max cap, GRAVEYARD instant kill
- PRODUCE mechanic: Poisson stochastický (`lambda > 0`) i deterministický pevný výnos (`lambda == 0`); type-based production (UNIQUE archetype jako producent → random prázdné ENVI)
- SUMS HP per LOCATION: `_process_sums_hp()` drainuje behaviors per-stack; wipe (hp=0) smaže LOCATION relaci; PRODUCE blend = vážený průměr HP

## Presentation: Console

- `console.py` — live `rich.Live` dashboard, HP bars, tick log, `--ticks`/`--delay`/`--full` CLI args
- Entity type colours (blue/cyan/magenta/white); short/full mode; UNIQUE tag zkrácen na `UNI`
- Archetype description lookup via TYPE_OF chain (`_archetype_desc`)
- UNIQUE archetype roots hidden in normal mode, visible in `--full` mode
- HP display: default = barevný progress bar `#####.....`; `--full` = barevný zlomek `50/100`
- `_hp_colour()` helper sdílený pro bar i zlomek (green > 50 % / yellow > 25 % / red)
- SUMS HP čteno z LOCATION relace (ne z entity) — `add_children()` předává `loc_hp`
- Root label `PocketWorld` při více rootech

## Core Features

- Save / load — `World.save()` / `World.load()` for JSON

## Worlds

- `worlds/nord.json` — Chronicle of the Polar Night Dynasty (narativ, hierarchie prostorů, CHAR→CHAR, Wildfire Oil, PRODUCE dřeva)
- `worlds/math.json` — Mathematical Universe (abstraktní entity, kategoriální entropie, deterministický PRODUCE primů, SUMS HP per LOCATION)
- `worlds/chess.json` — Royal Chess (32 figur, 64 políček, 7 archetypů figur, HP systém, type-based PRODUCE šípů na prázdná políčka)
- `worlds/genesis.json` — Genesis (Bůh + padlý anděl Felix + PRIMITIVO_ES víno; PRODUCE λ=0.05; creation story; TRIGGER dialogy + resurrekt)

## Royal Chess — MVP design decisions

- Pravidla: standardní FIDE (mat, pat, opakování, remíza dohodou)
- Braní: přesun figury na pole soupeře (standard)
- Čas: tick-based; hráč čeká na tah soupeře → ticky využívá výrobou/sběrem
- Dynamit: náhodně se objeví na políčku, nelze vyrábět

## Simulation (continued)

- `control="rand"` brain — `_rand_brain()`: každý tick vybere náhodné dosažitelné ENVI přes EDGE (respektuje `one_way`, `deny`); INDRID, FREYA, BYGUL v nord.json
- EDGE system: `RelationType.EDGE` + atributy `way`, `one_way`, `deny`; `_edge_allows()` + `_actor_categories()` helpers; nahrazuje PASSAGE; king-move chess (210 EDGEs); EDGE chain math; genesis deny FallenAngels
- TRIGGER mechanic: `RelationType.TRIGGER` + `_process_triggers()` — tři módy:
  - HP-threshold fire-once (number > 0): normální CDF Phi((threshold−hp)/sigma); fired IDs v meta.vars["triggers_fired"]
  - Ambient repeatable (number == 0): Bernoulli p = lambda_ per tick
  - Resurrection (number == -1): hp → hp_max, arc se resetuje (fired IDs vymazány pro daný subjekt)

## Documentation

- `GLOSSARY.md` — kanonické názvosloví projektu (EntityType vs kategorie, prototype inheritance, TRIGGER)
- Archetype entities přidány do všech světů (nord, math, chess)

---

*Last updated: 2026-02-21 (TRIGGER)*
