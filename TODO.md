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

- `[ ]` RelationType: add CONSUME (recipe engine — vstupy → výstupy)

## Simulation

- `[~]` World simulation loop (tick-based) — BEHAVIOR + PRODUCE + Intent(EAT/MOVE) + EDGE working; validate/resolve/chain pending
- `[ ]` Intent `control="player"` CLI stub (vypíše možnosti, čeká na vstup)
- `[ ]` Intent validate + resolve fáze (rank-based conflict resolution)
- `[ ]` Conflict resolution via `rank` + skill check

## Core Features

- `[ ]` Player interactions

## Console UI

- `[ ]` **Přepracovat layout** — log zabírá celou výšku, dialogy a projevy postav zanikají; rozdělit plochu na: panel světa | log | panel dialogů/postav
- `[ ]` **Panel postav / dialogů** — samostatná oblast pro TRIGGER výstupy (dialogy, monology); posouvat se nesmí — vždy viditelné
- `[ ]` **Player input area** — vyhrazené místo pro budoucí hráčský vstup (příkazy, volby)
- `[ ]` **Log filtry / barvy** — odlišit MOVE, EAT, TRIGGER, PRODUCE; možnost skrýt kategorie

## Presentation

- `[ ]` **Web editor PocketWorld** — editace JSON světů přes prohlížeč
  - záložky dle typu relace (LOCATION, SKILL, BEHAVIOR, EDGE, PRODUCE, TRIGGER, TYPE_OF)
  - tabulka s řazením a fulltextovým vyhledáváním
  - přidání záznamu jako předvyplněná kopie existujícího řádku
  - inline editace (klik → edit, Enter → uložit)
  - export → world JSON
- `[ ]` **Web** — Three.js frontend (vizualizace světa)
- `[ ]` **Engine** — Godot / Unity (future)

## Worlds

- `[ ]` `worlds/terrarium.json` — The Terrarium (ekosystém bez lidí, PRODUCE/CONSUME, predátor/kořist) — čeká na recipe engine

## Royal Chess — MVP

- `[ ]` Akce: hráč nebo jednoduchý chess engine skript

---

*Last updated: 2026-02-21 (rand brain; EDGE nord fixes; Console UI + Web editor TODOs)*
