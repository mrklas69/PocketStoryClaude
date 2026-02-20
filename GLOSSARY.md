# GLOSSARY — PocketStory

Kanonické názvosloví projektu. Při nejasnosti platí tato definice.

---

## Entity

### Strukturální typ (`EntityType`)
Jak s entitou zachází **engine** — containment pravidla, kapacita, stackování.
Definováno jako Python enum `EntityType` v `backend/core/entity.py`.

| Hodnota  | Popis |
|----------|-------|
| `ENVI`   | Prostředí / kontejner (místnost, pole, oblast). Pasivní, bez HP (zpravidla). |
| `CHAR`   | Postava / aktér. Má HP, rank, může nést předměty. |
| `UNIQUE` | Unikátní předmět nebo archetype. Kapacita povinná, pokud nese jiné entity. |
| `SUMS`   | Součtovatelná hromada (šípy, zlato…). Má `number`, nemá individuální identitu. |

### Kategorie / archetype (TYPE_OF)
Co entita **je** v příběhu nebo herní mechanice.
Vyjádřeno relací `TYPE_OF(instance, kategorie)` v JSON světě.
Kategorie může, ale nemusí být reálná entita (UNIQUE bez LOCATION = čistý archetype).

Příklady: `PAWN`, `ROOK`, `RECIPE`, `GAME_STAT`, `PIECE`

> **Pravidlo:** Nikdy neříkáme "typ entity" o kategorii a naopak.
> Správně: "Pěšec je `CHAR` strukturálního typu a kategorie `PAWN`."

---

## Relace

| Typ          | Význam |
|--------------|--------|
| `LOCATION`   | Entita se fyzicky nachází v kontejneru. |
| `TYPE_OF`    | Entita patří do kategorie / dědí z archetypu. |
| `SKILL`      | Entita umí provádět akci nebo pohyb. |
| `BEHAVIOR`   | Pasivní efekt na stav entity (HP změny, decay…). |
| `PRODUCE`    | Entita (recept) produkuje výstup. *(plánováno)* |
| `CONSUME`    | Entita (recept) spotřebovává vstup. *(plánováno)* |

---

## Ostatní pojmy

| Pojem        | Definice |
|--------------|----------|
| **tick**     | Základní časová jednotka simulace. Jedna iterace enginu. |
| **rank**     | Síla / priorita entity při řešení konfliktů. |
| **nature**   | Vrozenná morální esence entity (−10000 tmavá ↔ +10000 světlá). `None` = neutrální. |
| **karma**    | Nakumulované důsledky jednání CHAR entity. Dynamická, mění se každý tick/událost. |
| **decay**    | Přirozený pokles HP způsobený BEHAVIOR relacemi. |
| **archetype entity** | UNIQUE entita bez LOCATION, jejíž `id` je cílem TYPE_OF relací. Slouží jako sdílená definice kategorie (popis, pravidla). |
| **prototype inheritance** | Mechanismus rozlišení atributů: engine čte hodnotu nejprve z entity samotné; pokud je `None`, jde po TYPE_OF řetězci a vezme první nalezenou hodnotu z archetypu. Umožňuje psát instance "řídce" — uvádět jen odchylky od archetypu. Analogie: JavaScript prototype chain, CSS cascade. |

---

*Last updated: 2026-02-20*
