# IDEAS — PocketStory

Volný zápisník nápadů. Sem patří vše, co ještě není task — nápady, úvahy, možnosti.
Zralé nápady se přesouvají do TODO.md jako konkrétní úkoly.

---

## Concept & Design

1. Name — confirm "PocketStory" or choose alternative

## Data Model

2. `proto_id` for SUMS (mergeable stacks) — revisit after move/remove

## Simulation

3. TRIGGER relation type — reactive rules: "checkmate → guard reaction"
4. FRIDGE / environment context modifying DECAY rate (needs ENT3 in Relation)

## Presentation

5. Procedural story generation
6. Moods / personality traits for entities
7. Seasonal events
8. **Dialogue/Communication System** — Entities can speak (monologue, dialog, broadcast):
   - **Tier 1 (80%):** Template engine — `dialogs.yaml` with random templates per event/emotion
   - **Tier 2 (20%):** AI on-demand — contextualized prompt to LLM for special situations (optional)
   - **Tier 3:** Caching — entity.dialog_history to avoid repetition
   - **Audiences:** SELF (monologue), WORLD (broadcast), PLAYER (direct address)
   - **Log:** inverted chat-like console display (new messages at top, scrollable history)

## Infrastructure

9. **World Package System** — Each world can have custom dependencies:
   - **Assety:** icon, thumbnails (`world/assets/`)
   - **Python hooks:** entry points for custom logic (`world/hooks/engine.py`, `world/hooks/intents.py`)
   - **Dependencies:** pip packages listed in `requirements.txt`
   - **External APIs:** registered in `world.yaml` with env var references
   - **Manifest file:** `world.yaml` declares author, version, hooks, python deps, api endpoints
   - Dynamic world loading: engine reads manifest, imports hooks module, resolves deps

## Worlds

10. `worlds/terrarium.json` (ekosystém bez lidí, PRODUCE/CONSUME, predátor/kořist) — čeká na recipe engine *(přesunout do TODO až bude engine hotový)*

## Royal Chess — future iterations

11. Jednoduchý chess engine — minimax nebo pravidlový skript pro NPC tahy
12. Výrobní ekonomika: šípy, recyklace slonoviny, seno pro koně — čeká na PRODUCE/CONSUME
13. Pravidla spawnu dynamitu (frekvence, podmínky, max počet na šachovnici)
14. Formační bonusy (figury blízko u sebe = nižší entropie)
15. Domácí čtverec: každá figura zná svůj home square, vzdálenost od home = entropie
16. Fog of War: hráč vidí jen políčka, kam dohlédnou jeho figury (každý typ = jiný dosah)

## SHOW — klíčové koncepty pro scénář

18. **HP je univerzální, fyzika každého světa je v datech** *(ep. 7 nebo 8)*
    - HP = jednotná míra "zdraví" čehokoliv: čerstvost rajčete, energie baterie, víra anděla, platnost důkazu, kondice šachové figury
    - Co HP ničí a léčí je výhradně v BEHAVIOR relacích + TYPE_OF kaskádě — žádný hardcode v enginu
    - Survival brain CHARu nepotřebuje vědět nic o konkrétním světě: hledá ENVI s léčivým BEHAVIOR pro svoji kategorii
    - Pěšec → HOME_BASE; Harold → jídlo; Felix → nic (záměr); √2 → správné ENVI v Math Universe
    - Stejný kód, jiná data = jiná fyzika světa. To je pointa celé architektury.

## Side Projects

17. **Awakened Chess** — standalone projekt; figury znají svůj home square, vzdálenost = entropie, formační bonusy; engine PocketStory je unese přirozeně

---

*Last updated: 2026-02-20*
