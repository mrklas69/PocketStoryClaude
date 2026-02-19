# DIARY — PocketStory

Chronological development log. Each session records date, duration, and what happened.

---

## 2026-02-18

**Duration:** ~30 min
**With:** Claude (claude-haiku-4-5)

Project started. Established the basic concept:
- PocketStory — a small simulated world, Tamagotchi meets light strategy
- Created initial project documents: README.md, CLAUDE.md, TODO.md, DIARY.md
- Agreed on workflow: Czech for conversation, English for code
- TODO.md structured with status markers and categories

**Next session:** Define the core game loop and what lives in the world.

**Architecture decision:**
Strict separation of three layers:
- Data Model (pure Python classes)
- Simulation (game logic)
- Presentation (console → web → game engine)

Tech stack confirmed: Python + FastAPI + SQLite + Three.js + rich (console)

**Entity type system (theatrical metaphor):**
- ENVI   = Kulisy   — environment, container (room, bag, world)
- CHAR   = Herci    — character (player/NPC, no distinction yet)
- ITEM   = Rekvizity — item, two subtypes: UNIQUE (Harold's shield) / SUM (12 apples)
- RULES = Scénář   — skill / ability / perk (Fishing, Cooking, Forester...)

**Entity base attributes:** id, name, description, type, number (SUM only),
capacity (ENVI only), parent_id (tree structure)

---

## 2026-02-19

**Duration:** ~2 hours
**With:** Claude (claude-haiku-4-5)

Second session. From concept to first running code:
- Defined entity type system with theatrical metaphor (ENVI/CHAR/ITEM/RULES)
- Designed Entity base class with id, name, description, type, number, capacity, parent_id
- ENVI as universal container — recursive tree structure (world → village → character → items)
- ITEM as parent concept for UNIQUE (Harold's Heavy Shield) and SUM (12 apples)
- RULES = skills/abilities (Fishing, Cooking...) — the theatrical "script" a character can learn
- Created backend/core/entity.py — Entity class + EntityType enum
- Set up Python venv (.venv), installed rich + fastapi
- Wrote demo.py — renders world tree in console via rich

First working demo: Harold in Green Valley with his shield, apples, and fishing skill.

**Next session:** World class (entity tree manager).

---

## 2026-02-19 (pokračování)

**Duration:** ~1 hour
**With:** Claude (claude-sonnet-4-5)

Continued from previous context window. World class finished and polished:
- Implemented `World` class: `add()`, `children()`, `roots()`, `get()`, `save()`, `load()`
- `load()` validates duplicate IDs; skips containment check (trust the file)
- Switched entity IDs from UUID to human-readable strings (BASE, MARTIAN, CHEST...)
- JSON serialization: nullable/default fields now omitted — `description`, `capacity`, `parent_id` if None; `number` if == 1
- Demo world `worlds/martian_saga.json` — The Saga of the Little Martian; COINS (SUMS, n=73) added to illustrate stackable resources

**Architecture decisions:**
- `World.add()` enforces containment rules; `World.load()` trusts the file (no re-validation)
- Human-readable IDs make world files hand-editable without tooling

**Next session:** Console presentation layer (rich tree view of a loaded world).

---

## 2026-02-20

**Duration:** ~2 hours
**With:** Claude (claude-sonnet-4-6)

Major architecture redesign — from parent_id tree to Relation system:

**Removed:**
- `EntityType.RULES` — skills/abilities no longer live as entities
- `parent_id` from `Entity` — hierarchy now expressed via LOCATION relation

**New: `Relation` class** (`backend/core/relation.py`)
- Fields: `id` (int, autoincrement), `type` (RelationType), `ent1` (str), `ent2` (Optional[str]), `number` (int = 1)
- `ent2` is Optional — reserved for future unary relations
- Unique key: `(type, ent1, ent2)`

**RelationType enum** (3 types so far):
- `LOCATION` — ENT1 contains ENT2 in quantity NUMBER (replaces parent_id + SUMS.number for counts)
- `SKILL` — ENT1 has skill/ability ENT2 at level NUMBER (replaces RULES entities)
- `TYPE_OF` — ENT1 belongs to category ENT2 (string code: WEAPON, HUMAN, ANDROID, KEY, CURRENCY...)

**Updated `World` class:**
- `add_entity()` + `add_relation()` replace old `add()`
- `children(parent_id)` returns `list[tuple[Entity, int]]` — count from LOCATION relation
- `roots()` — entities not referenced as ENT2 in any LOCATION relation
- `load()` / `save()` handle both `entities` and `relations` sections

**Demo world `martian_saga.json`** regenerated with full relation system.
New character: **Dr. Iris Chen** (HUMAN, GREENHOUSE) — astrobiologist, has FLAMETHROWER_OP skill.
ID ranges: 1–99 LOCATION, 100–199 SKILL, 200–299 TYPE_OF.

**Next session:** `World.move()`, `World.remove()`, and game loop design.

**Additional — same session (continued, simulation design):**
- `rank: int` added to Entity design (conflict resolution — neutral term, won't clash with other future attributes)
- Tick loop architecture decided: `collect_intents → validate → resolve → execute → chain`
- Intents = temporary Python objects in simulation layer (not stored as relations)
- All four entity types generate intents (ENVI, CHAR, UNIQUE, SUMS)
  - SUMS: decay/growth (tomatoes rot, forest generates wood)
  - CHAR: autonomous behavior chains (hungry → FIND → MOVE → PICK → EAT)
  - UNIQUE: rare but valid (cursed crown influences owner, bomb ticks down)
  - ENVI: environment as active agent (INTEGERS wants to eliminate irrational players)
- Conflict resolution: `rank` attribute + relevant SKILL check of both actors
- GOAP-style chaining: successful execute() can spawn new intents for next tick

**Additional — same session (continued):**
- `TYPE_OF` added to RelationType; `ent2` made Optional (unary relations ready)
- `ITEM_TYPES` constant and `is_item()` method removed (unused)
- Capacity logic refined: counts only UNIQUE + SUMS children; CHAR and ENVI are free
- Two new demo worlds created:
  - `worlds/polar_night.json` — Kingdom of the Polar Night (King Harold, Queen Indrid, Princess Freya)
  - `worlds/math_universe.json` — Mathematical Universe (number set hierarchy as LOCATION, functions as CHAR, constants as UNIQUE, mathematical properties as TYPE_OF/SKILL)
- All three worlds render correctly via `demo.py`

---

## 2026-02-20 (pokračování — simulation layer)

**Duration:** ~1 hour
**With:** Claude (claude-sonnet-4-6)

First working simulation: tomatoes decay in real time.

**Entity changes (`backend/core/entity.py`):**
- Added `rank: int = 1` — conflict resolution weight (higher rank wins intent disputes)
- Added `hp: Optional[int] = None` — current health / freshness / durability
- Added `hp_max: Optional[int] = None` — maximum HP (None = entity has no HP concept)

**New RelationType (`backend/core/relation.py`):**
- `BEHAVIOR` — ENT1 (entity id or category string) has behavior ENT2 (name); NUMBER = intensity/rate per tick
- Example: `BEHAVIOR(PERISHABLE_FOOD, DECAY, 8)` — anything of category PERISHABLE_FOOD loses 8 HP per tick

**World serialization (`backend/core/world.py`):**
- `_entity_to_dict` / `_dict_to_entity` extended for `rank`, `hp`, `hp_max`
- Fields omitted from JSON when at default value (`rank` if 1, `hp`/`hp_max` if None)

**New: `backend/sim/tick.py`** — first simulation engine:
- `_get_behavior(world, entity_id, behavior_name)` — resolves behavior intensity via:
  1. Entity-specific BEHAVIOR relation (override)
  2. Inherited via TYPE_OF categories (fallback cascade)
- `tick(world) -> list[str]` — applies all BEHAVIOR effects; currently implements DECAY (reduces hp by rate, clamps to 0); returns human-readable log messages

**Demo world `worlds/martian_saga.json` updated:**
- `MARTIAN`: hp=80, hp_max=100
- `IRIS`: hp=100, hp_max=100
- New entity `TOMATOES` (SUMS, hp=100, hp_max=100) — 5 units in Iris's inventory
- `TYPE_OF(TOMATOES, PERISHABLE_FOOD)` — categorizes tomatoes
- `BEHAVIOR(PERISHABLE_FOOD, DECAY, 8)` — all PERISHABLE_FOOD loses 8 HP/tick
- Relation ID ranges extended: 300+ = BEHAVIOR

**`demo.py` — live dashboard (`rich.Live`):**
- No more scrolling blocks — display refreshes in place each tick
- World Panel: bordered rich tree with tick counter in title
- Event Log Panel: rolling log of last 8 events with tick numbers
- CLI: `--ticks N`, `--delay S` (seconds between ticks)
- HP bar: `[####......]` coloured green/yellow/red based on ratio

**Result:** Running `demo.py --ticks 15 --delay 0.5` shows tomatoes decaying
from 100 HP to 0 over 13 ticks with `[SPOILED]` marker at the end.

**Next session:** `World.move()`, `World.remove()`, then Intent system.

---

## 2026-02-20 (pokračování — resource flow design)

**Duration:** ~30 min
**With:** Claude (claude-sonnet-4-6)

Design session — no code written, architecture decisions for next implementation step.

**Planned world expansion (martian_saga):**
- Add KITCHEN (ENVI) + CHARGING_STATION (ENVI inside KITCHEN)
- Iris stays in GREENHOUSE with tomatoes but no eating → dies of hunger (passive demo)
- Martian stays in STORAGE (not near charger) → drains to 0

**New BEHAVIOR patterns:**
- `BEHAVIOR(HUMAN, HUNGER, 3)` — passive HP drain per tick via TYPE_OF cascade
- `BEHAVIOR(ANDROID, BATTERY_DRAIN, 5)` — same for robots
- `BEHAVIOR(CHARGING_STATION, RECHARGE, 15)` — environment behavior: applies to ANDROID children

**New RelationTypes decided: PRODUCE + CONSUME**
- `PRODUCE(source, item_id, rate)` — source produces N units of item per tick
- `CONSUME(source, item_id, amount)` — source requires N units of item to operate
- Generator = only PRODUCE (e.g. greenhouse grows tomatoes without inputs)
- Sink = only CONSUME
- Transformer/crafter = both (e.g. oven: flour + water → bread)

**Recipe = Entity (key architectural decision):**
- A recipe is a UNIQUE entity (TYPE_OF RECIPE)
- `CONSUME(BREAD_RECIPE, FLOUR, 2)` + `CONSUME(BREAD_RECIPE, WATER, 1)` + `PRODUCE(BREAD_RECIPE, BREAD, 1)`
- `SKILL(OVEN, BREAD_RECIPE, 1)` — oven knows this recipe
- Solves disambiguation: multiple recipes on one station are separate entities, no ambiguity
- Same `SKILL` relation type reused — station knows recipes the same way a character knows abilities

**HP restore from eating (Option B chosen):**
- No `PRODUCE(_ACTOR_HP, ...)` pseudo-entity needed
- Engine convention: consuming a PERISHABLE_FOOD item restores `hp_max / 4` HP to the actor
- `hp_max` doubles as nutritional value — one attribute, two roles

**Design principle confirmed:** Entity + Relation is sufficient for the full model.
The graph is expressive enough that new game concepts map to new relation types,
not new Python classes. Complexity of the world ≠ complexity of the code.

**Next session:** Implement PRODUCE/CONSUME in RelationType + recipe engine in tick.py + martian_saga expansion.

---

## 2026-02-19 (závěr)

**Duration:** ~30 min
**With:** Claude (claude-sonnet-4-5)

Design discussion and refinements:
- `demo.py` rewritten — loads world from JSON file (`World.load()`), recursive rich tree rendering, path as CLI argument (default: `worlds/martian_saga.json`)
- Capacity enforcement added to `World.add()`: capacity = number of direct children (slots); SUMS `number` is irrelevant for slot counting
- `World.load()` intentionally skips capacity check (trust the file)

**Design discussions:**
- **`move()` / `remove()`** — identified as missing operations needed for any game action; deferred to next session
- **SUMS prototype/instance** — when a character transfers stackable items, simulation must know both piles are the same "kind" to merge them; current model has no shared identity for SUMS. Decision: add optional `proto_id` field to Entity; two SUMS with same `proto_id` are mergeable. Deferred to next session.

**Next session:** `World.move()`, `World.remove()`, and `proto_id` for SUMS.

---
