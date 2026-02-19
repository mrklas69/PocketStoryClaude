# Epizoda 2 — Modelování
## Skript + stage directions

**Délka:** ~8 minut
**Průvodce:** Claude (ženský hlas)
**Jazyk:** česky

---

### ÚVOD (0:00 – 0:45)

```
[00:00] HLAS:      Hele, mám pro tebe otázku. Co mají společného míč, smartphone,
                   odmocnina ze dvou a zkumavka s chemikálií?
        OBRAZOVKA: Tmavé pozadí. Postupně se zprava objevují čtyři předměty:
                   fotbalový míč, smartphone, symbol √2, skleněná zkumavka
                   s modrou kapalinou. Každý předmět přiletí z jiného rohu.
        TITULEK:   (žádný)

[00:10] HLAS:      Na první pohled nic. Různé světy, různé obory.
                   Ale zkus se na ně podívat očima programátora.
        OBRAZOVKA: Předměty zůstávají na obrazovce. Pod každým se rozsvítí
                   otazník.
        TITULEK:   (žádný)

[00:17] HLAS:      Každý z nich má vlastnosti. A každý z nich něco dělá.
                   Jinými slovy — každý je objekt.
        OBRAZOVKA: Otazníky se změní na nápis [OBJEKT]. Všechny čtyři najednou.
        TITULEK:   OBJEKT

[00:25] HLAS:      Ahoj, já jsem Claude. A v téhle sérii se naučíme, jak se
                   programuje svět. Nejen hra — svět. Jakýkoliv.
        OBRAZOVKA: Logo PocketStory. Pod ním: „Epizoda 2 — Modelování"
        TITULEK:   PocketStory — Epizoda 2: Modelování
```

---

### ČÁST 1 — Svět vs. popis světa (0:45 – 2:00)

```
[00:45] HLAS:      Než začneme programovat, musíme se dohodnout na jedné věci.
                   Svět a popis světa nejsou totéž.
        OBRAZOVKA: Fotografie lesa. Vedle ní mapa téhož lesa.
        TITULEK:   svět ≠ popis světa

[00:55] HLAS:      Mapa není les. Je to model lesa. Zjednodušení, které nám pomáhá
                   se v lese orientovat — ale stromy nerostou na papíře.
        OBRAZOVKA: Šipka z fotografie lesa na mapu. Na mapě se zvýrazní
                   jeden strom, pak druhý — ale na fotografii jich jsou stovky.
        TITULEK:   model = zjednodušení reality

[01:08] HLAS:      Každý program je model. Když píšeš hru, neprogramuješ skutečný
                   meč — programuješ jeho model. Číslo pro poškození, číslo pro
                   váhu, jméno. To je všechno, co hra potřebuje vědět.
        OBRAZOVKA: Skutečný středověký meč (fotografie). Vedle něj textové pole:
                     Frostbite
                     poškození: 45
                     váha: 2.3 kg
                     magický: ano
        TITULEK:   model meče v PocketStory

[01:25] HLAS:      A to je osvobozující. Protože model si navrhneme sami.
                   My rozhodujeme, co je důležité. Fyzik modeluje hmotnost a rychlost.
                   Spisovatel modeluje charakter a motivaci. A my? My modelujeme svět,
                   ve kterém chceme, aby se něco dělo.
        OBRAZOVKA: Tři sloupce vedle sebe:
                   FYZIK: [hmotnost] [rychlost] [teplota]
                   SPISOVATEL: [charakter] [motivace] [konflikt]
                   MY: [entita] [relace] [čas]
        TITULEK:   (žádný)
```

---

### ČÁST 2 — Matematický vesmír (2:00 – 3:30)

```
[02:00] HLAS:      Teď přijde trochu filosofie. Ale neboj — bude krátká.
        OBRAZOVKA: Hvězdná obloha. Ticho. Pak se pomalu rozsvítí matematické
                   symboly mezi hvězdami: +, π, √, ∞
        TITULEK:   (žádný)

[02:08] HLAS:      Fyzik Max Tegmark tvrdí, že vesmír není jen popsatelný
                   matematikou — on sám je matematická struktura.
                   Že na nejhlubší úrovni jsou elektrony, fotony, gravitace —
                   jen vztahy mezi čísly.
        OBRAZOVKA: Portrét Maxe Tegmarka (nebo stylizovaná ilustrace vědce).
                   Za ním rovnice. Pak se rovnice rozloží na uzly a hrany grafu.
        TITULEK:   Max Tegmark: „Náš vesmír je matematická struktura."

[02:25] HLAS:      A pak je tady Nick Bostrom s ještě odvážnější myšlenkou:
                   a co kdybychom my sami byli v simulaci? Co kdyby někdo
                   někde spouštěl program, ve kterém žijeme?
        OBRAZOVKA: Stylizovaná matice čísel, pak přechod na obraz reality —
                   město, lidé, příroda. Efekt „rozpad na pixely a zpět".
        TITULEK:   Simulační hypotéza — Bostrom (2003)

[02:42] HLAS:      Nevíme, jestli je to pravda. Ale víme jedno: když my
                   programujeme simulaci, pracujeme přesně takhle.
                   Vytváříme matematickou strukturu. Objekty. Vztahy. Pravidla.
        OBRAZOVKA: Přechod z hvězdné oblohy na terminál s demo.py.
                   Na terminálu se vykreslí strom světa PocketStory.
        TITULEK:   náš program = matematická struktura
```

---

### ČÁST 3 — Třída a instance (3:30 – 5:15)

```
[03:30] HLAS:      Dobře. Zpátky k těm čtyřem předmětům.
        OBRAZOVKA: Znovu se objeví míč, smartphone, √2, zkumavka.
        TITULEK:   (žádný)

[03:35] HLAS:      Míč má vlastnosti: tvar, hmotnost, odrazivost.
                   A umí něco dělat: odrazit se, kutálet se.
        OBRAZOVKA: U míče se rozsvítí tabulka:
                     === Míč ===
                     tvar: koule
                     hmotnost: 0.4 kg
                     odrazivost: 0.8
                     --- umí: ---
                     odrazit_se()
                     kutálet_se()
        TITULEK:   atributy + metody = objekt

[03:50] HLAS:      Ale pozor — tohle není konkrétní míč. Tohle je třída.
                   Šablona. Popis toho, co každý míč má a umí.
        OBRAZOVKA: Nad tabulkou se objeví nápis „třída Míč".
                   Pod ní se vykreslí tři konkrétní míče:
                   červený (0.3 kg), modrý (0.5 kg), fotbalový (0.43 kg).
        TITULEK:   třída = šablona   instance = konkrétní objekt

[04:05] HLAS:      Konkrétní míč — ten červený v tělocvičně, ten fotbalový
                   na hřišti — to jsou instance třídy. Každá má stejnou
                   strukturu, ale jiné hodnoty.
        OBRAZOVKA: Šipky z „třída Míč" na každý konkrétní míč.
                   U každého míče bliknou jeho konkrétní hodnoty.
        TITULEK:   třída Míč → instance: červený míč, fotbalový míč, ...

[04:20] HLAS:      A teď to samé pro odmocninu ze dvou.
                   √2 má hodnotu. Je iracionální — to znamená, že její
                   desetinný rozvoj nikdy nekončí a neopakuje se.
                   Ale žádnou hmotnost nemá. Neodrazí se.
        OBRAZOVKA: Tabulka vedle √2:
                     === Číslo ===
                     hodnota: 1.41421356...
                     iracionální: ano
                     transcendentní: ne
                     --- umí: ---
                     sečíst_se(jiné_číslo)
                     umocnit_se(exponent)
        TITULEK:   třída Číslo

[04:38] HLAS:      Jiná třída. Jiné vlastnosti, jiné metody. Ale pořád objekt.
                   Matematický objekt — žije jen v abstraktním světě, ale
                   modelujeme ho úplně stejně.
        OBRAZOVKA: Vedle sebe: třída Míč a třída Číslo. Jsou různé,
                   ale mají stejnou strukturu (tabulka atributů + tabulka metod).
        TITULEK:   různé třídy, stejný princip

[04:52] HLAS:      A tohle je klíčový insight celé série.
                   Prostředí, postava, předmět, číslo, pravidlo hry —
                   všechno jsou objekty. Všechno má atributy a metody.
                   A všechno žije v jednom světě.
        OBRAZOVKA: Čtyři předměty (míč, smartphone, √2, zkumavka) se
                   přeskupí do jednoho kruhu. Uprostřed kruhu: OBJEKT.
        TITULEK:   vše je objekt
```

---

### ČÁST 4 — Simulace = struktura + pravidla (5:15 – 6:45)

```
[05:15] HLAS:      Simulace je víc než seznam objektů.
                   Objekty existují v prostoru a čase. A dějí se jim věci.
        OBRAZOVKA: Míč leží nehybně. Pak přijde ruka (animace) a kopne do něj.
                   Míč se odrazí od zdi.
        TITULEK:   (žádný)

[05:25] HLAS:      Aby se míč odrazil správně, potřebujeme pravidla.
                   Zákon odrazu. Gravitaci. Tření.
                   Bez pravidel jsou objekty jen mrtvá data.
        OBRAZOVKA: Míč se pohybuje. Kolem něj se zobrazí rovnice:
                   F = m·a, úhel dopadu = úhel odrazu.
        TITULEK:   pravidla = zákony simulace

[05:40] HLAS:      V naší hře pravidla říkají:
                   postava nemůže obsahovat místnost.
                   Rajčata se kazí.
                   Hladová postava ztrácí zdraví.
                   To jsou zákony našeho světa.
        OBRAZOVKA: Tři pravidla se vypíší jedno po druhém jako kód:
                   CONTAINMENT: CHAR nemůže obsahovat ENVI
                   BEHAVIOR(PERISHABLE_FOOD, DECAY, 8)
                   BEHAVIOR(HUMAN, HUNGER, 3)
        TITULEK:   zákony PocketStory

[05:58] HLAS:      Simulace je tedy: objekty plus pravidla.
                   Data plus logika. Struktura plus chování.
        OBRAZOVKA: Rovnice uprostřed obrazovky:
                   SIMULACE = OBJEKTY + PRAVIDLA
        TITULEK:   SIMULACE = OBJEKTY + PRAVIDLA

[06:10] HLAS:      A v PocketStory jsou objekty reprezentovány jako entity
                   a pravidla jako relace. Za chvíli uvidíš jak — ale to
                   nechám na epizodu tři a čtyři.
        OBRAZOVKA: Rychlý preview: strom entit v konzoli (demo.py output).
                   Barevné ENVI, CHAR, UNIQUE, SUMS uzly.
        TITULEK:   příště: Entity a Relace
```

---

### ZÁVĚR (6:45 – 8:00)

```
[06:45] HLAS:      Takže co jsme se dneska naučili?
        OBRAZOVKA: Prázdná obrazovka. Jeden po druhém se vypíší body.
        TITULEK:   (žádný)

[06:50] HLAS:      Za prvé — svět je matematická struktura. Objekty,
                   vztahy, pravidla.
        OBRAZOVKA: Bod 1: „svět = matematická struktura"
        TITULEK:   1. svět = matematická struktura

[06:58] HLAS:      Za druhé — třída je šablona. Instance je konkrétní objekt.
                   Míč, číslo, postava — všechno jsou instance nějaké třídy.
        OBRAZOVKA: Bod 2: „třída → instance"
        TITULEK:   2. třída → instance

[07:08] HLAS:      Za třetí — simulace potřebuje objekty i pravidla.
                   Data bez logiky jsou mrtvá. Logika bez dat je prázdná.
        OBRAZOVKA: Bod 3: „simulace = objekty + pravidla"
        TITULEK:   3. simulace = objekty + pravidla

[07:18] HLAS:      V příští epizodě se podíváme na čtyři druhy entit,
                   ze kterých se skládá každý svět v PocketStory.
                   A ukážeme si, jak je zapsat v Pythonu.
        OBRAZOVKA: Animace: z bodu 3 vyroste strom PocketStory světa.
                   Uzly se obarvují: modrá (ENVI), zelená (CHAR),
                   žlutá (UNIQUE), fialová (SUMS).
        TITULEK:   příště: ENVI · CHAR · UNIQUE · SUMS

[07:35] HLAS:      Já jsem Claude. Uvidíme se příště.
        OBRAZOVKA: Logo PocketStory. Fade to black.
        TITULEK:   PocketStory · github: [odkaz]
```

---

## Poznámky pro produkci

- **Hudba:** instrumentální, klidná, mírně elektronická — hraje v pozadí celou epizodu
- **Tempo hlasu:** pomalé a zřetelné, pauzy po klíčových větách
- **Animace:** minimalistické — texty přilétají, nevybuchují; preferuj plynulé přechody
- **Kód v terminálu:** skutečný výstup z `demo.py`, ne mockup
- **Délka:** cílová 8 minut; dá se zkrátit vynecháním části 2 (simulační hypotéza) na ~6 min
