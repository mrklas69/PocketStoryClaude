# SHOW — PocketStory

Vzdělávací/osvětová série PocketStory.
**Mládeži, přestaňte hry konzumovat — pojďte je tvořit!**
Dnes stačí jen kreativita a nápady. O zbytek se postará AI.

---

## Seznam epizod

1. Záměry projektu, komu je určen, obsah kapitol
2. Modelování
3. PocketWorld = Entity
4. PocketWorld = Relace
5. Vizualizace světa
6. Čas
7. Generátory, Kolektory, Transformátory

---

### 1. Záměry projektu

- Komu je série určena (mládež, začínající programátoři, hráči co chtějí tvořit)
- Co se naučíš: modelování, Python, simulace, základy herního designu
- Ukázka výsledku: živý svět v konzoli → web → engine

---

### 2. Modelování

- **Svět vs. popis světa** — mapa není území
- **Matematický vesmír** — svět je matematická struktura (objekty + vztahy + pravidla)
- Teorie, že žijeme v simulaci (Bostrom, Tegmark) — jako motivační hook
- Prostor, Čas, Událost/Jev jako základní pojmy
- **Simulace/Hra = datová struktura + pravidla**
- Důležité pojmy: třída, instance, dědičnost, rozhraní (abstraktní třídy)
- Ukázky a příklady ze světa kolem nás

---

### 3. PocketWorld = Entity

- Třídy, dědičnost, druhy entit v PocketStory
- **ENVIronment** — prostředí, kontejnery (místnost, batoh, svět)
- **CHARacter** — postavy, NPC, autonomní agenti
- **UNIQUE** — unikátní předměty (Haroldův meč, klíč od trezoru)
- **SUMS** — součtovatelné položky, zdroje (73 mincí, 5 rajčat)
- **Pravidla jsou dvojího druhu:**
  - *Natvrdo v kódu* (CONTAINMENT_RULES) — postava nemůže obsahovat prostředí; UNIQUE nemůže obsahovat nic
  - *Měkká, deklarativní* — definovaná jako relace (viz ep. 4); př. rajčata se kazí, lidé hladovějí

---

### 4. PocketWorld = Relace

- **Matematický základ** — unární, binární relace; multigraf s typovanými hranami
- Každá relace: `(id, type, ent1, ent2, number)`

| Typ | Význam | Příklad |
|-----|--------|---------|
| **LOCATION** | ENT1 obsahuje ENT2 v množství NUMBER | Skleník obsahuje 5 rajčat |
| **SKILL** | ENT1 umí ENT2 na úrovni NUMBER | Iris umí hydroponiku (8), Pec zná recept na chléb |
| **TYPE_OF** | ENT1 patří do kategorie ENT2 | Rajčata jsou PERISHABLE_FOOD, Iris je HUMAN |
| **BEHAVIOR** | ENT1 má chování ENT2 s intenzitou NUMBER | PERISHABLE_FOOD se kazí rychlostí 8/tick |
| **PRODUCE** | ENT1 produkuje N kusů ENT2 per tick | Skleník produkuje 3 rajčata |
| **CONSUME** | ENT1 spotřebuje N kusů ENT2 per tick | Recept na chléb spotřebuje 2 mouky |

- **Hierarchie vzniká přirozeně** z LOCATION relací — žádný `parent_id` v objektu
- **SKILL se používá dvakrát**: postava umí dovednost / stanice zná recept → stejná relace, jiný kontext
- **TYPE_OF jako taxonomie**: kategorie nad entitami (Jídlo, Zbraně, Suroviny, Kazící se, Magické...)

---

### 5. Vizualizace světa

- Entity a relace = uzly a hrany grafu s atributy
- Vizualizace matematické struktury
- **Úroveň 1 — barevná konzole** (rich, refreshující se obrazovka) — hotovo!
- **Úroveň 2 — webový prohlížeč** (Three.js, jednoduché polygony)
- **Úroveň 3 — herní engine** (Godot / Unity, vykreslené objekty)

---

### 6. Čas

- **Herní cyklus (tick loop)**: collect intents → validate → resolve → execute → chain
- **HP, HP_MAX** — kondice entit (entropie, stárnutí, hladovění, vybíjení baterií...)
- **BEHAVIOR + TYPE_OF cascade**: entita zdědí chování z kategorie; přímá relace má přednost
- Pohyb = změna LOCATION relace
  - Aktivní (postava umí MOVE)
  - Pasivní (předmět lze sebrat / odhodit)
- Demo: rajčata se kazí v reálném čase, HP bar živě klesá

---

### 7. Generátory, Kolektory, Transformátory

- **Generátor** — produkuje entity bez vstupů: `PRODUCE(GREENHOUSE, TOMATOES, 3)`
- **Kolektor / Sink** — spotřebovává entity: `CONSUME(BIN, TRASH, 10)`
- **Transformátor / Crafting** — CONSUME vstupů + PRODUCE výstupů
- **Recept je entita** (UNIQUE, TYPE_OF RECIPE):
  ```
  CONSUME(BREAD_RECIPE, FLOUR, 2)
  CONSUME(BREAD_RECIPE, WATER, 1)
  PRODUCE(BREAD_RECIPE, BREAD,  1)
  SKILL(OVEN, BREAD_RECIPE, 1)      ← pec zná recept
  SKILL(CAMPFIRE, BREAD_RECIPE, 1)  ← i táborák zná recept
  ```
- Proč recept jako entita? → řeší disambiguaci (pec s deseti recepty, mouka ve třech z nich)
- Demo: skleník pěstuje rajčata, Iris hladoví, Marťan vybíjí baterie

---

---

## Produkce

### Role

| Role | Kdo |
|------|-----|
| Průvodce / moderátor | Claude (ženský hlas, sympatická kolegyně) |
| Screenshoty / screencast | autor projektu |
| AI hlas | ElevenLabs / NotebookLM / Descript |
| Střih | CapCut / DaVinci Resolve |

### Workflow epizody

1. **Skript** — Claude napíše mluvený text + stage directions (co je vidět na obrazovce)
2. **Screenshoty / screencast** — autor nahraje nebo exportuje vizuály z projektu
3. **Hlasový záznam** — ElevenLabs/NotebookLM vygeneruje ženský hlas ze skriptu
4. **Střih** — spojení hlasu, screenshotů, titulků
5. **Přepis** — autor pošle Claude podrobné titulky (mluvené slovo + popis obrazovky)
6. **Zpětná vazba** — Claude přečte přepis, zkontroluje obsah, navrhne úpravy

### Formát přepisu pro zpětnou vazbu

Plný textový přepis — přístupný pro neslyšící i nevidomé.
Každý časový blok obsahuje tři řádky:

```
[MM:SS] HLAS:     přesně co bylo řečeno
        OBRAZOVKA: podrobný popis vizuálu (co je vidět, co se pohybuje, co přibývá)
        TITULEK:   text zobrazený na obrazovce (nadpisy, zvýrazněná slova, kód)
```

Příklad:
```
[00:12] HLAS:      Představ si, že chceš naprogramovat svět. Jaký je nejmenší stavební kámen?
        OBRAZOVKA: Prázdná tmavá plocha. Postupně se zleva objevují čtyři předměty:
                   míč, smartphone, odmocnina ze dvou (√2), zkumavka s modrou kapalinou.
        TITULEK:   (žádný)

[00:20] HLAS:      Míč je kulatý, odráží se, má hmotnost. Smartphone svítí, přehrává hudbu.
                   Odmocnina ze dvou existuje jen jako číslo — žádnou hmotnost nemá.
                   A zkumavka? Ta reaguje s jinými látkami.
        OBRAZOVKA: U každého předmětu se rozsvítí popisky jeho vlastností:
                   míč → [kulatý] [hmotnost: 0.4 kg] [odrazivost: 0.8]
                   smartphone → [svítí] [baterie: 73 %] [přehrává: ano]
                   √2 → [hodnota: 1.4142...] [iracionální: ano]
                   zkumavka → [objem: 10 ml] [reaktivní: ano]
        TITULEK:   vlastnosti = atributy
```

*Soubor pro plánování série — průběžně doplňován.*
