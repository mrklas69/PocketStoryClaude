# PocketStory

A pocket-sized simulated world — somewhere between a Tamagotchi and a strategy game.

## Concept

PocketStory is a small, self-contained simulated world where the player nurtures, shapes,
and observes a living story unfolding in their pocket. Think Tamagotchi meets light strategy.

## Status

> Early concept phase. Ideas being gathered.

## Architecture

The project is strictly layered:

1. **Data Model** — pure Python classes, no dependencies (entities, world state)
2. **Simulation** — game logic, world updates, event system
3. **Presentation** — swappable, multiple targets planned:
   - Console (Python `rich` library)
   - Web browser (Three.js)
   - Game engine (Godot / Unity / Unreal — future)

## Tech Stack

- **Backend:** Python + FastAPI
- **Persistence:** SQLite
- **Frontend (web):** HTML + vanilla JS + Three.js
- **Frontend (console):** Python `rich`

## Getting Started

> TBD

---

## Project docs

| File | Purpose |
|---|---|
| [TODO.md](TODO.md) | Active tasks |
| [IDEAS.md](IDEAS.md) | Raw ideas, not yet tasks |
| [DONE.md](DONE.md) | Archive of completed work |
| [GLOSSARY.md](GLOSSARY.md) | Canonical terminology |
| [DIARY.md](DIARY.md) | Session log |
