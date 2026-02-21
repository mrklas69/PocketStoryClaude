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

## 2026-02-20 (pokračování — World.move() + entropie + šachy)

**Duration:** ~3 hours
**With:** Claude (claude-sonnet-4-6)

Velký produktivní blok — od relokace entit přes entropii tří světů až po šachový prototyp.

**World.move() + CONTAINMENT_RULES:**
- `CONTAINMENT_RULES` doplněno: CHAR→CHAR (postava může nést jinou postavu; Freya bere koťátko)
- UNIQUE jako kontejner jen při `capacity != None` — bez kapacity = neskladný objekt, ne krabice
- `World._next_relation_id()` — max existujících id + 1 (fix: Relation vyžaduje id parametr)
- `World.location_of(entity_id)` — vrací přímého rodiče (ENVI nebo CHAR)
- `World.move(entity_id, new_container_id, amount?)` — validace containment, SUMS partial move + merge

**Bygul — koťátko Freyi:**
- Nová entita v `worlds/polar_night.json`: BYGUL (CHAR, hp:20/20)
- Pojmenování: Bygul = "včelí zlato" ze staré norštiny
- `LOCATION(FREYA, BYGUL)` — Freya nese koťátko
- `TYPE_OF(BYGUL, CAT)` + `TYPE_OF(BYGUL, ANIMAL)`

**tick.py — generalizace behaviors:**
- Původní `_get_behavior(world, entity_id, "DECAY")` — hardcoded jméno
- Nová `_collect_behaviors(world, entity_id) -> list[tuple[str, int]]`
- Tři zdroje behaviors: (1) entity-specific, (2) TYPE_OF cascade, (3) location-based (ENVI kde entita stojí)
- Všechny rates sečteny, jeden průchod; log zobrazuje jméno každého efektu
- Fix: `hp` nesmí překročit `hp_max` při recharge → `max(0, min(cap, hp - total_drain))`

**Entropie tří světů:**
- `polar_night.json`: HAROLD(90/100), INDRID(75/100), FREYA(100/100); `BEHAVIOR(HUMAN, HUNGER, 2)`, `BEHAVIOR(ANIMAL, HUNGER, 1)`
- `martian_saga.json`: `BEHAVIOR(ANDROID, BATTERY_DRAIN, 5)`, `BEHAVIOR(HUMAN, HUNGER, 3)`
- `math_universe.json`: hp přidáno konstantám (π, e, φ, i) a funkcím (sqrt, exp, sin, PRIME); behaviors: `PROOF_EROSION(3)`, `APPROXIMATION_DRIFT(2)`, `EXISTENCE_DOUBT(2)`, `DOMAIN_DRIFT(1)`, `OSCILLATION_LOSS(1)`, `SIEVE_EROSION(2)`
- Výsledek: π a e se erodují 5/tick, sin 2/tick, 0 a 1 jsou věčné (no HP)

**worlds/royal_chess.json — šachový testovací svět:**
- Prostory: BOARD, OFF_BOARD, HOME_BASE, DEEP_ENEMY, čtverce A1/A6/B3/C2/H8
- Figury: WHITE_QUEEN(90/90), WHITE_BISHOP_LIGHT(30/30), WHITE_H_ROOK(50/50), BLACK_H_PAWN(100/100); `rank` = hodnost figury
- Abstraktní statistiky jako SUMS: MOVE_COUNT(28), WHITE_LEGAL_MOVES(34), BLACK_THREATS(2)
- SKILL: MOVE_QUEEN, MOVE_BISHOP, MOVE_ROOK, MOVE_PAWN (budoucí topologie tahy)
- TYPE_OF hierachie: QUEEN/BISHOP/ROOK/PAWN → PIECE → WHITE/BLACK_PIECE

**GRAVEYARD mechanic:**
- `TYPE_OF(OFF_BOARD, GRAVEYARD)` — data-driven, generické
- `_in_graveyard(world, entity_id)` v tick.py
- Entita v GRAVEYARD ENVI: hp → 0 okamžitě, log: "captured — HP -> 0 [GRAVEYARD]"

**Location-based BEHAVIOR (třetí zdroj):**
- `BEHAVIOR(HOME_BASE, RECHARGE, -5)` — záporné číslo = léčení; figury doma regenerují
- `BEHAVIOR(DEEP_ENEMY, TERRITORIAL_STRAIN, 4)` — figury na soupeřově území se opotřebovávají
- `TYPE_OF(HOME_BASE, SAFE_ZONE)`, `TYPE_OF(DEEP_ENEMY, HAZARD_ZONE)` — sémantické tagy

**Koncept: Endurance Chess:**
- Figury se opotřebovávají v boji a v soupeřově území
- Musí se vrátit domů dobít — jinak vyhasnou
- "Budou to bláznivé šachy!" — nová varianta šachů jako emergentní vlastnost systému

**Git:**
- Repo inicializováno, `.gitignore` vytvořen (excluduje .venv/, temp/, __pycache__, *.pyc)
- Pushnut na GitHub: https://github.com/mrklas69/PocketStoryClaude

**Opravené bugy:**
1. `UnicodeEncodeError` — znak `→` v logu na Windows cp1250 → nahrazen `->`
2. `Relation()` bez `id` parametru → přidán `_next_relation_id()`
3. Duplicitní `id=1` v royal_chess.json → opraveno na id=13, 14
4. `hp` překračoval `hp_max` při recharge → přidán cap: `min(cap, hp - total_drain)`

**Next session:** PRODUCE/CONSUME + recipe engine; World.remove(); martian_saga expansion (KITCHEN, CHARGING_STATION)

---

## 2026-02-20 (pokračování — Royal Chess design + konzole)

**Duration:** ~2 hours
**With:** Claude (claude-sonnet-4-6)

Refaktoring prezentační vrstvy + design Royal Chess herní mechaniky.

**console.py (náhrada za demo.py):**
- Přejmenování: `demo.py` → `console.py`
- Nové barvy entit (red/yellow/green rezervovány pro ERR/WARN/OK):
  - ENVI = blue, CHAR = cyan, UNIQUE = magenta, SUMS = white
- Odstraněn výpis capacity z labelu
- Přidán přepínač `--full`: zobrazuje rank, nature, karma
- `_signed(n)` helper: kladná čísla dostávají prefix `+`

**entity.py + world.py — nové atributy:**
- `nature: Optional[int]` — morální/esenciální náboj (-10000 dark ↔ +10000 light); None = neutral
- `karma: Optional[int]` — naakumulované důsledky akcí (CHAR only v praxi); None = N/A
- Serializace: obojí omítnuto z JSON při None (defaultní)

**world.py — `World.remove()`:**
- Odstraní entitu + všechny relace kde `ent1 == id` nebo `ent2 == id`
- Děti entity se stávají rooty (osiřelé, ne smazané)

**worlds/royal_chess.json — opravy + rozšíření:**
- Opraveny JSON chyby (chybějící čárky, trailing commas) po ručním editaci
- Přidána všechna chybějící políčka šachovnice (bylo 8, přidáno 56 → 64 celkem)
- Opraven F4: chyběl `"type": "ENVI"`
- Reorganizace souboru: OFF_BOARD → políčka a1-h8 → figury → zdroje → relace

**Design session: Royal Chess herní mechanika (MVP):**
- Pravidla šachu: standardní FIDE (mat, pat, opakování, remíza dohodou)
- Braní: přesun figury na pole soupeře (standard)
- Čas: tick-based; hráč čeká na soupeřův tah → v té době probíhá výroba/sběr zdrojů
- Akce: hráč nebo skript; plánován jednoduchý chess engine
- Dynamit: náhodně se objeví na políčku šachovnice, nelze vyrábět

**Rozhodnutí: zjednodušujeme!**
- Zastavujeme vrstvení nápadů; prioritou je dokumentace + stabilizace základu
- Nápady pro další iterace zaznamenány do TODO.md místo okamžité implementace

**Next session:** PRODUCE/CONSUME + recipe engine; nebo konzolový chess prototype

---

## 2026-02-20 (pokračování — Royal Chess rebuild + archetypes + dokumentace)

**Duration:** ~4 hours
**With:** Claude (claude-sonnet-4-6)

Rozsáhlá session zaměřená na úklid, dokumentaci a rozšíření datového modelu.

**worlds/royal_chess.json — kompletní přestavba:**
- Vygenerováno skriptem: všech 32 figur na správných startovních pozicích, 64 políček s HP 100/100
- Figury: HP 100/100 (F-pěšci 80/100), rank dle hodnoty figury (King=10..Pawn=1)
- Přidáno 7 archetype entit: PIECE, KING, QUEEN, ROOK, KNIGHT, ARCHER, PAWN
- Midgame pozice zachovány: WHITE_QUEEN@d1, WHITE_H_ROOK@h8, BLACK_H_PAWN@a6, BLACK_H_ROOK@OFF_BOARD
- Výsledek: 109 entit, 164 relací

**Archetype pattern (pro všechny světy):**
- Archetype = UNIQUE entita bez LOCATION; její id odpovídá ent2 cíli TYPE_OF relací
- `_archetype_desc(world, entity_id)` v console.py — entity.description → TYPE_OF archetype.description → None
- `--full` mód: UNIQUE rooty skryty (jsou metadata, ne herní objekty)
- Přidány archetypové entity do **polar_night** (HUMAN, ROYALTY, WEAPON, MAGICAL) a **math_universe** (IRRATIONAL, OPERATION, TRANSCENDENTAL, ALGEBRAIC)

**WorldManifest + WorldMeta (backend/core/world.py):**
- `WorldManifest`: author, created, version, lore — statická metadata světa
- `WorldMeta`: tick, turn, vars — runtime stav (key-value vars pro world-specific proměnné)
- Všechny 4 světy mají vyplněný manifest s lore textem
- `--full` mód konzole zobrazuje cyan manifest panel nahoře: autor, datum, verze, lore, live stats

**Dokumentace — velký úklid:**
- `GLOSSARY.md` vytvořen — kanonické názvosloví: EntityType vs. kategorie, prototype inheritance, všechny pojmy
- `IDEAS.md` vytvořen — volný zápisník nápadů (15 položek, organizováno dle kategorií)
- `DONE.md` vytvořen — archiv hotových úkolů přesunutých z TODO.md
- `TODO.md` zeštíhleno: z 106 řádků na 42, jen aktivní úkoly (`[ ]` a `[~]`)
- `CLAUDE.md` aktualizováno: seznam 7 řídících dokumentů, nový workflow pipeline
- `README.md` aktualizováno: tabulka doc indexu
- `MEMORY.md` aktualizováno: nová struktura docs, archetypové entity, prototype inheritance

**Pořadí EntityType sjednoceno na CHAR, ENVI, UNIQUE, SUMS** (enum, TYPE_STYLE, stats, GLOSSARY)

**Odstraněno:** `generate_world.py` (starý prototype, dead code), dočasné skripty `_gen_chess.py`, `_add_archetypes.py` atd.

**Konceptuální diskuse:**
- ENTITY + RELATION = dvě tabulky stačí; WORLD metadata = třetí tabulka
- Prototype inheritance: `World.resolve_attr(entity, attr)` — čte vlastní hodnotu → TYPE_OF archetype → None; zaznamenáno do TODO + GLOSSARY
- WorldMeta.vars = key-value store pro world-specific proměnné

**Git push:** commit `0e1043d` — vše pushnutý na GitHub

**Next session:** PRODUCE/CONSUME RelationType + recipe engine v tick.py; nebo World.resolve_attr() (prototype inheritance)

---

## 2026-02-19 (design review + nový svět Genesis)

**Duration:** ~1 hour
**With:** Claude (claude-sonnet-4-6)

Celkový přehled projektu po offline práci. Žádný nový kód — čistě design a dokumentace.

**Srovnávací tabulka světů (z offline ODS → přeformátovaná do MD):**
- Přehled čtyř světů: Polar Night, Royal Chess, Genesis, Math Universe
- Každý svět má unikátní mechaniku: RPG sága / endurance chess / creation story / obrácená entropie

**Nový svět: `worlds/genesis.json`**
- Bůh (věčný, bez HP, rank 100) + Felix (padlý anděl, hp 50/100, rank 7)
- COSMOS → HEAVEN (Bůh) + EARTH (Felix)
- Felix: `BEHAVIOR(FALLEN_ANGEL, DESPAIR, 5)` + `BEHAVIOR(MORTAL_REALM, EMPTINESS, 2)` = 7 HP/tick drain
- Bůh má SKILL: CREATE/DESTROY/TRANSFORM/SEPARATE — vše na úrovni 100
- Design insight: Felix@hp=0 → Bůh ho vzkřísí (CREATE na existující entitě = reset HP) = podmínka pro spuštění dalšího aktu

**Úpravy `worlds/royal_chess.json`:**
- BISHOP → ARCHER přejmenováno všude (entita, SKILL, TYPE_OF) — kulturní závislost anglofonního "bishop"
- PIECE_BOX (ENVI) odstraněn

---

## 2026-02-19 (závěr — offline práce)

**Duration:** ~7 hours
**With:** Sám (offline)

Dva samostatné dokumenty — práce bez AI, čistá lidská přemýšlecí fáze.

**NOTES.md — zamyšlení nad úrovněmi prototypů enginu:**
- Přemýšlení o tom, co vlastně chceme mít za výsledek v různých fázích projektu
- Definice úrovní prototypu: co je "hotový" engine pro demo, pro show, pro hru

**PocketStory-srovnávací tabulka světů.ods — přehled čtyř demo světů:**
- Vytvořena tabulková dokumentace všech čtyř aktuálních světů:
  - `martian_saga` — Sága malého Marťana
  - `polar_night` — Království Polární noci
  - `math_universe` — Matematický vesmír
  - `royal_chess` — Šachový testovací svět
- Srovnání: počty entit, typy, relace, behaviors, klíčové mechaniky
- Přehled sloužící jako základ pro rozhodnutí, který svět rozvíjet dál

**Poznámka k datumu:** Záznam dopsán zpětně 2026-02-19 — offline bloky jsou součástí stejného pracovního dne.

---

## 2026-02-21

**Duration:** ~2 hours
**With:** Claude (claude-sonnet-4-6)

Simulation engine rozšíření + HP per LOCATION + console polish.

**tick.py → engine.py (přejmenování):**
- `backend/sim/tick.py` → `backend/sim/engine.py` — konzistentnější název

**PRODUCE mechanic dokončena:**
- RelationType `PRODUCE` přidán: `lambda > 0` = Poisson stochastický, `lambda == 0` = deterministický pevný výnos
- Poisson algorimtus (Knuth) s `max_yield = number`
- Type-based PRODUCE: `ent1` = UNIQUE archetype → engine najde všechna ENVI toho TYPE_OF, vyloučí obsazená (CHAR child), vybere náhodné prázdné
- Condition: `producer is None or producer.type == EntityType.UNIQUE` → type-based branch
- Oprava: ChessSquares jako UNIQUE entita způsobila, že se type-based větev nevstoupila → fix podmínky
- `worlds/royal_chess.json`: ChessSquares archetype + 64 TYPE_OF relací + PRODUCE(ChessSquares, ARROWS, λ=0.1, n=16)
- `worlds/polar_night.json`: PRODUCE(FOREST, WOOD, λ=0.3, n=4) — stochastická produkce dřeva
- `worlds/math_universe.json`: PRODUCE(NATURALS, PRIME, n=1) — deterministické +1 prime/tick

**Genesis cleanup:**
- Odstraněn COSMOS (obal nebyl potřeba), GOD zůstává v HEAVEN, FELIX na EARTH
- Přidán PRIMITIVO_ES (SUMS) — italské Primitivo víno od Gianfranco Fino
- PRODUCE(EARTH, PRIMITIVO_ES, λ=0.05, n=2) — cca jednou za 20 ticků 1–2 lahve

**HP per LOCATION pro SUMS entity (architektonická změna):**
- `entity.hp` u SUMS zrušeno; `entity.hp_max` zůstává jako typová vlastnost (výchozí čerstvost)
- `Relation.hp` — aktuální čerstvost konkrétní hromady (per-stack)
- Nová funkce `_process_sums_hp(world)` v engine.py: iteruje LOCATION relace s hp, drainuje behaviors, při hp=0 **smaže relaci** (žádný ghost záznam)
- `_process_produce()` rozšíření: nový stack startuje s `hp = item.hp_max`; merge do existující hromady = vážený průměr HP `(n_old × hp_old + n_new × hp_max) / (n_old + n_new)`
- `_collect_behaviors()` rozšíření: volitelný `location_id` parameter pro SUMS per-stack lookup
- Entity loop: SUMS entity přeskočeny (`continue`), zpracovány výše
- `worlds/math_universe.json`: hp přesunuto z PRIME entity do LOCATION(NATURALS, PRIME)
- `console.py` `add_children()`: SUMS položky čtou `loc_hp` z LOCATION relace, předávají do `label()`

**Console polish:**
- `UNIQUE` tag zkrácen na `UNI`
- HP bar bug fix: `[colour][bar][/]` → `[colour]{bar}[/]` — Rich interpretoval `[bar]` jako markup tag a tiše ho zahazoval
- Zobrazení HP split: default mód = barevný progress bar `#####.....`, `--full` mód = barevný zlomek `50/100`
- `_hp_colour()` helper — sdílená logika barvy pro bar i zlomek
- Root `PocketWorld` místo `World` při více rootech

**Git commits (6):**
- `b314360` — SUMS per-LOCATION HP + Genesis cleanup
- `b5aca9d` — delete LOCATION relation on SUMS wipe
- `bfe0063` — fix HP display for SUMS in console
- `6fec597` — UNI label
- `44c3a33` — hp bar rendering fix
- `72f6346` — bar/fraction split
- `2c0bed1` — colored fraction in --full
- `270a4dc` — PocketWorld root label

**Next session:** Intent system; nebo World.resolve_attr() prototype inheritance; nebo konzolový chess prototype

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

## 2026-02-21 (pokračování — TRIGGER + dialog Felixe a Boha)

**Duration:** ~2 hours
**With:** Claude (claude-sonnet-4-6)

Implementace dialogového systému + úklid konzole.

**TRIGGER mechanic (nový RelationType):**
- `RelationType.TRIGGER`: `ent1` = mluvčí/subjekt, `ent2` = dialogová UNIQUE entita (text v `description`), `number` = mód, `lambda_` = sigma nebo pravděpodobnost
- Tři módy:
  - `number > 0` — HP-threshold, fire-once: spustí se když `ent1.hp <= number`; pravděpodobnost = normální CDF `Φ((threshold − hp) / sigma)`; fired IDs v `meta.vars["triggers_fired"]`
  - `number == 0` — ambient, opakovatelný: Bernoulli `p = lambda_` per tick, bez HP podmínky
  - `number == -1` — resurrekt: spustí se při `hp == 0`, resetuje `hp → hp_max`, vymaže fired IDs pro daný subjekt (arc se opakuje v příštím životě)
- `_get_dialogue(world, entity_id)` — přečte description z dialogové UNIQUE entity
- `_process_triggers(world)` — voláno na konci `tick()` (po behavior loopu)

**worlds/genesis.json — dialogy Felixe a Boha:**
- 11 nových UNIQUE dialogových entit (bez LOCATION = archetype / dialogue script)
- Felix: 4 threshold linky (HP 45/30/15/5 se sigma 8/5/4/2), 1 resurrekt, 3 ambient
- Bůh: 3 ambient linky (`lambda = 0.02` každá)
- Resurrekt scéna: `"Felix: [barely a whisper] Is this...? / God: Now. Let us begin."`
- Felix drainuje 7 HP/tick (DESPAIR 5 + EMPTINESS 2), první arc ~8 ticků

**Výsledek v logu (ukázka 24 ticků):**
```
[tick  3] Felix: "I miss making stars..."  [HP 29 <= 45]
[tick  5] Felix: "Maybe He was right..."  [HP 15 <= 15]
[tick  8] Felix: HP 1 -> 0  [DEAD]
[tick  8] [RESURRECT] Felix 0 -> 100 HP | "Felix: Is this...? / God: Now. Let us begin."
[tick 17] God: "Patience is not a virtue when you invented time."
[tick 17] Felix: "I miss making stars..."  — druhý arc
```

**Console úpravy:**
- UNIQUE rooty vždy skryté ze stromu (i v `--full` — bylo jen v normálním módu)
- Stats v `--full` rozděleny: umístěné UNIQUE → `UNIQUE: N`; archetype/dialogue (bez LOCATION) → `arch: N`; příklad genesis: `CHAR: 2  ENVI: 2  SUMS: 1  arch: 11`
- Dialogové řádky v event logu: `reverse` styling pro řádky s uvozovkami nebo `[RESURRECT]` — vizuálně vyčnívají nad dim HP eventy

**Git commits:**
- `a0dd573` — TRIGGER system + genesis dialogy + console arch stats + always hide UNIQUE roots
- `f6c2409` — reverse video pro dialogue lines v event logu

**Next session:** Intent system; World.resolve_attr() prototype inheritance; konzolový chess prototype

---

## 2026-02-21 (pokračování — PROMPTS + Intent systém)

**Duration:** ~3 hours
**With:** Claude (claude-sonnet-4-6)

Organizační práce + první implementace Intent systému.

**Nové soubory:**
- `PROMPTS.md` — 5 kmenových promptů s volacími znaky: BEGIN!, THINK!, AUDIT!, DOCS!, END! + spouštěcí znaky konzole (CHESS!, POLAR!, MARS!, MATH!, GENESIS!)
- `show/PROMPTS.md` — 4 prompty pro produkci SHOW série (SCRIPT!, FEEDBACK!, TERMS!, VISUALS!)

**World.resolve_attr() — prototype inheritance:**
- BFS průchod TYPE_OF řetězcem; vrátí první non-None hodnotu z archetypu
- `WHITE_A_PAWN.description = None` → resolved z `Pawns` archetypu ✓
- Přesunuto do DONE.md

**Intent systém — design (dlouhá diskuse):**
- Klíčové rozhodnutí: `control: str | None` atribut na CHAR — kdo/co generuje intenty
- `null` = pasivní (default); `"survival"` = data-driven; `"player"` / `"rand"` / `"remote:url"` = stuby
- `control=null` elegantně řeší: šachové figury, Šípková Růženka, pasivní NPC — žádný extra atribut
- MOVE = defaultní schopnost CHAR; SKILL specializuje topologii pohybu (MOVE_PAWN, MOVE_QUEEN)
- Survival brain = data-driven: hledá léčivé BEHAVIOR v dostupných ENVI — funguje pro pěšce i Felixe i √2
- Design insight do IDEAS.md: "HP je univerzální, fyzika světa je v datech"

**Intent systém — implementace:**
- `Intent` dataclass: `actor_id, action, target_id, amount, weight`
- `_survival_brain()`: EAT (inventář) → MOVE (léčivé ENVI) při `hp < 80 % hp_max`
- `_find_food_in_inventory()`: SUMS s `hp_max > 0` v přímém inventáři
- `_find_healing_envi()`: ENVI sourozenec s negativní BEHAVIOR pro kategorii entity
- `_collect_intents()`: dispatch dle `entity.control` (match/case)
- `_execute_intents()`: EAT (−1 kus, +hp_max//4 HP), MOVE (world.move())
- Pipeline zapojená do `tick()`: po BEHAVIOR, před TRIGGER

**Demo — polar_night.json:**
- Harold: `control="survival"`, inventář + 5× Venison (`hp_max=100`)
- Výsledek: Harold jí na ticku 6 (+25 HP, x4 zbývá), pak na ticku 17 (+25 HP, x3 zbývá)
- Ostatní světy: genesis, royal_chess, math_universe — všechny OK ✓

**Aktualizace GLOSSARY.md:** sekce Intent systém (Intent, action, weight, control, survival brain, pipeline)

**Next session:** `control="rand"` (probabilistický brain); MOVE k léčivému ENVI test; `"player"` CLI stub
