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

- `[~]` World simulation loop (tick-based) — BEHAVIOR + PRODUCE + Intent(EAT/MOVE) working; validate/resolve/chain pending
- `[ ]` Intent `control="rand"` brain (probabilistický, z dostupných akcí)
- `[ ]` Intent `control="player"` CLI stub (vypíše možnosti, čeká na vstup)
- `[ ]` Intent validate + resolve fáze (rank-based conflict resolution)
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

*Last updated: 2026-02-21 (Intent EAT/MOVE + control attr done)*
