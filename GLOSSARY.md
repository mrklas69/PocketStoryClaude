# GLOSSARY — PocketStory

Kanonické názvosloví projektu. Při nejasnosti platí tato definice.

---

## Entity

### Strukturální typ (`EntityType`)
Jak s entitou zachází **engine** — containment pravidla, kapacita, stackování.
Definováno jako Python enum `EntityType` v `backend/core/entity.py`.

| Hodnota  | Popis |
|----------|-------|
| `CHAR`   | Postava / aktér. Má HP, rank, může nést předměty. |
| `ENVI`   | Prostředí / kontejner (místnost, pole, oblast). Pasivní, bez HP (zpravidla). |
| `UNIQUE` | Unikátní předmět nebo archetype. Kapacita povinná, pokud nese jiné entity. |
| `SUMS`   | Součtovatelná hromada (šípy, zlato…). `number` = aktuální počet v dané hromadě (uložen v LOCATION relaci). HP (čerstvost/trvanlivost) se také uchovává per-hromada na LOCATION relaci, ne na entitě. |

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
| `LOCATION`   | Entita se fyzicky nachází v kontejneru. `number` = množství (SUMS). `hp` = čerstvost/trvanlivost dané hromady (SUMS only). |
| `TYPE_OF`    | Entita patří do kategorie / dědí z archetypu. `ent2` = CamelCase plural (např. `FallenAngels`, `Indivisibles`). |
| `SKILL`      | Entita umí provádět akci nebo pohyb. |
| `BEHAVIOR`   | Pasivní efekt na stav entity (HP změny, decay…). Kladné číslo = drain, záporné = heal. |
| `PRODUCE`    | Entita vytváří nové itemy. `lambda > 0` = Poisson stochastický; `lambda == 0` = deterministický. `ent1` = UNIQUE archetype → type-based (random prázdné ENVI). |
| `CONSUME`    | Entita spotřebovává itemy a aplikuje efekt. *(zatím neimplementováno)* |
| `RECIPE`     | Transformační recept: vstupy + energie → výstupy. *(zatím neimplementováno)* |
| `TRIGGER`    | Dialogová linka nebo událost vázaná na podmínku. `ent1` = mluvčí/subjekt, `ent2` = dialogová UNIQUE entita (text v `description`). `number`: `> 0` = HP threshold (fire-once, normální CDF); `0` = ambient (Bernoulli, λ = pravděpodobnost/tick); `-1` = resurrekt (hp → hp_max, arc se resetuje). Fire-once stav v `meta.vars["triggers_fired"]`. |

---

## Intent systém

| Pojem | Definice |
|-------|----------|
| **Intent** | Záměr CHAR entity provést akci v daném ticku. Ephemeral Python objekt — vzniká a zaniká v rámci jednoho `tick()`. Pole: `actor_id`, `action`, `target_id`, `amount`, `weight`. |
| **action** | String identifikátor akce: `"EAT"`, `"MOVE"`, `"PICK"`, … |
| **weight** | Urgence záměru: `0.0` = nízká, `1.0` = kritická. Odvozuje se z potřeby (např. `1 - hp/hp_max`). |
| **control** | Atribut CHAR entity. Určuje, kdo nebo co generuje intenty. `null` (pasivní, default) → žádné intenty; `"survival"` → data-driven přežití; `"player"` → vstup hráče (stub); `"rand"` → náhodná akce (stub); `"remote:url"` → externí zdroj (stub). |
| **survival brain** | Funkce pro `control="survival"`. Spustí se při `hp < 80 % hp_max`. Priorita: 1) EAT ze svého inventáře (SUMS s `hp_max > 0`), 2) MOVE k léčivému ENVI (negativní BEHAVIOR). Data-driven — nepotřebuje znát konkrétní svět. |
| **Intent pipeline** | Pořadí v `tick()`: PRODUCE → SUMS HP → BEHAVIOR → collect intents → execute intents → TRIGGER. |

---

## Ostatní pojmy

| Pojem        | Definice |
|--------------|----------|
| **tick**     | Základní časová jednotka simulace. Jedna iterace enginu. |
| **rank**     | Síla / priorita entity při řešení konfliktů. |
| **nature**   | Vrozenná morální esence entity (−10000 tmavá ↔ +10000 světlá). `None` = neutrální. |
| **karma**    | Nakumulované důsledky jednání CHAR entity. Dynamická, mění se každý tick/gebeurtenost. |
| **decay**    | Přirozený pokles HP způsobený BEHAVIOR relacemi. |
| **archetype entity** | UNIQUE entita bez LOCATION, jejíž `id` je cílem TYPE_OF relací. Slouží jako sdílená definice kategorie (popis, pravidla). |
| **prototype inheritance** | Mechanismus rozlišení atributů: engine čte hodnotu nejprve z entity samotné; pokud je `None`, jde po TYPE_OF řetězci a vezme první nalezenou hodnotu z archetypu. Umožňuje psát instance "řídce" — uvádět jen odchylky od archetypu. Analogie: JavaScript prototype chain, CSS cascade. |
| **PRODUCER** | Entita (typicky ENVI), která během ticku automaticky vytváří nové itemy. Např. Jablečný sad produkuje 3 jablka/tick. Vyjádřeno relací `PRODUCE(entity, item, number)`. |
| **CONSUMER** | Entita (typicky CHAR), která spotřebovává itemy a aplikuje efekt (zvýšení HP, získání skillů, atd.). Vyjádřeno relací `CONSUME(entity, item, effect)`. |
| **TRANSFORMER** | Entita (typicky ENVI), která provádí recept: přijímá dohodnuté vstupy + energii a vytváří výstupy. Např. Kamenná pec: 1 mouka + 0.5 voda + 400 kJ → 1 chléb. Vyjádřeno relací `RECIPE` s názorem vstupů, výstupů a energetických požadavků. |

---

*Last updated: 2026-02-21 (TRIGGER added)*
