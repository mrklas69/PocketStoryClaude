# PROMPTS.md — Prompty pro Claude (vývoj projektu)

Sbírka opakovaně použitelných promptů pro Claude při práci na PocketStory.
Zavolej volacím znakem (např. `BEGIN!`) — Claude spustí příslušný prompt.

Viz také: [show/PROMPTS.md](show/PROMPTS.md) — prompty pro vzdělávací sérii SHOW.

---

## BEGIN!  —  Zahájení sezení

```
Zahajujeme nové pracovní sezení na PocketStory.
Přečti si prosím:
- TODO.md — co je rozděláno nebo čeká
- DIARY.md — kontext z posledního sezení
- GLOSSARY.md — aktuální terminologie

Pak mi stručně shrň: kde jsme skončili, co nás čeká, a navrhni, čím začneme.
```

---

## THINK!  —  Brainstorming

```
Chci probrat nápad / problém: [POPIS]

Zatím nekóduj. Cílem tohoto sezení je přemýšlet a strukturovat myšlenky.

Zaměř se na:
1. Jak to zapadá do stávající architektury (datový model → simulace → prezentace)?
2. Jaké jsou možné přístupy a jejich kompromisy?
3. Jaká jsou rizika, edge cases, nebo věci, které nevíme?
4. Pokud jde o herní mechaniku: musí být vyjádřitelná pomocí stávajícího modelu
   (Entity + Relace). Pokud ne, navrhni minimální rozšíření.
   Preferuj emergentní chování z jednoduchých pravidel před naprogramovaným výsledkem.
5. Pokud jde o nový svět: jaké entity, prostředí, mechaniky a příběh?

Na konci mi navrhni, co zapsat:
- do IDEAS.md — pokud je nápad ještě nezralý
- do TODO.md — pokud je připravený k realizaci
```

---

## AUDIT!  —  Audit kódu a terminologie

```
Proveď hloubkový audit zdrojového kódu projektu PocketStory.
Přečti relevantní soubory sám — neaudituj naslepo.

Zaměř se na:

1. **Terminologie a pojmenování**
   - Jsou názvy v kódu (třídy, metody, proměnné, JSON klíče) konzistentní s GLOSSARY.md?
   - Míchají se konvence pojmenování (snake_case, CamelCase, SCREAMING_SNAKE) bez důvodu?
   - Jsou kategorie TYPE_OF důsledně v CamelCase plural (FallenAngels, Indivisibles…)?
   - Pokud najdeš nový nebo nedefinovaný termín, navrhni jeho doplnění do GLOSSARY.md.

2. **Architektura a vrstvení**
   - Je logika správně rozdělena mezi vrstvy (model / simulace / prezentace)?
   - Jsou podobné věci řešeny podobně? Kde jsou disproporce nebo nekonzistence?
   - Jsou JSON světy strukturovány konzistentně?

3. **Kvalita kódu**
   - Nepoužívané funkce, třídy, proměnné, importy (mrtvý kód).
   - Zakomentovaný kód, debug výpisy, dočasné hacky.
   - Over-engineering — zbytečná komplexita pro aktuální potřeby?
   - Co by zkušený vývojář označil jako "code smell"?

4. **Soulad se zadáním**
   - Odpovídá implementace konceptu z README.md a GLOSSARY.md?
   - Nezanesli jsme předpoklady, které jsou v rozporu s původním záměrem?

5. **Porovnání s běžnou praxí**
   - Kde se odchylujeme od konvencí Pythonu, game devu nebo datového modelování?
   - Je odchylka záměrná a odůvodněná, nebo náhodná?

Výstup: seřazený seznam nálezů s prioritou (kritické / doporučené / kosmetické)
a konkrétními návrhy oprav. Neopravuj nic bez mého odsouhlasení.
```

---

## DOCS!  —  Konsolidace dokumentace

```
Proveď komplexní revizi veškeré dokumentace projektu PocketStory.
Přečti všechny .md soubory v projektu (root i podsložky).

Zaměř se na:

1. **Úplnost a aktuálnost**
   - Odpovídá obsah dokumentů aktuálnímu stavu kódu a rozhodnutí?
   - Chybí v GLOSSARY.md termíny, které jsou zavedené v kódu nebo SHOW sérii?
   - Je README.md stále přesný popis projektu?

2. **Konzistence napříč dokumenty**
   - Jsou stejné pojmy používány stejně v README, GLOSSARY, TODO, DIARY, SHOW.md?
   - Odkazují dokumenty navzájem správně (broken links, zastaralé sekce)?
   - Je DONE.md konzistentní s tím, co TODO.md označuje jako hotové?

3. **Jazyková korektura**
   - Překlepy, gramatika, interpunkce (v češtině i angličtině).
   - Anglické názvy v kódu a identifikátorech — jsou správně napsané?

4. **Struktura a čitelnost**
   - Jsou dokumenty přehledně členěné? Kde chybí nadpisy nebo jsou redundantní sekce?
   - Je DIARY.md chronologicky konzistentní?

Výstup: seřazený seznam nálezů s konkrétními návrhy oprav.
Neopravuj nic bez mého odsouhlasení.
```

---

## END!  —  Ukončení sezení

```
Uzavíráme dnešní sezení na PocketStory. Proveď prosím tyhle kroky:

1. **Dokumentace**
   - Přesuň dokončené úkoly z TODO.md do DONE.md (pokud jsme to ještě neudělali).
   - Zkontroluj, zda TODO.md odráží aktuální stav (`[ ]` / `[~]`).
   - Doplň nebo uprav GLOSSARY.md, pokud jsme dnes zavedli nové termíny.
   - Přidej záznam do DIARY.md — datum jako nadpis, odrážky s klíčovými rozhodnutími
     a hotovými věcmi, sekce "Příště" s tím, co zůstalo nedokončené.

2. **Kód**
   - Zkontroluj, zda nezůstaly debug výpisy, commented-out bloky nebo TODO komentáře v kódu.

3. **Git**
   - Navrhni commit message pro dnešní práci (stručná, výstižná).
   - Proveď commit a push na remote (main).

Co jsme dnes udělali:
[STRUČNÝ VÝČET — nebo nech Claude, ať si to sám shrne z konverzace]
```

---

---

## Spouštěcí znaky — konzole

Krátké zkratky — Claude vypíše příkaz do chatu, uživatel ho spustí ve svém terminálu.
(Nespouštět přes Bash tool — Rich animace potřebuje živý terminál.)

| Znak | Příkaz |
|------|--------|
| `CHESS!` | `python console.py worlds/chess.json --full --ticks 20 --delay 0.5` |
| `NORD!` | `python console.py worlds/nord.json --full --ticks 20 --delay 0.5` |
| `MATH!` | `python console.py worlds/math.json --full --ticks 20 --delay 0.5` |
| `GENESIS!` | `python console.py worlds/genesis.json --full --ticks 30 --delay 0.3` |

*Soubor průběžně rozšiřován.*
