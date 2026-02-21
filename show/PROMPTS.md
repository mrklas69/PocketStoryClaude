# PROMPTS.md — Prompty pro Claude (SHOW série)

Sbírka opakovaně použitelných promptů pro Claude v kontextu vzdělávací série PocketStory.

---

## 1. Skript epizody

```
Napiš skript pro epizodu č. [N] série PocketStory s názvem "[NÁZEV]".

Kontext:
- Cílové publikum: mládež, začínající programátoři, hráči co chtějí tvořit
- Průvodce: Claude — ženský hlas, sympatická kolegyně, neformální tón
- Délka epizody: cca [X] minut

Osnova epizody (z SHOW.md):
[VLOŽ OBSAH PŘÍSLUŠNÉ SEKCE Z SHOW.md]

Formát výstupu — každý blok obsahuje:
- HLAS: mluvený text průvodce (přirozený, hovorový, bez zbytečných odborných klišé)
- OBRAZOVKA: co je vidět (popis akce, kódu, vizuálu — pro střiháče)
- TITULEK: text zobrazený na obrazovce (pokud je relevantní)

Příklad formátu:
[00:00] HLAS:      ...
        OBRAZOVKA: ...
        TITULEK:   ...
```

---

## 2. Zpětná vazba na přepis epizody

```
Přečti přepis epizody č. [N] série PocketStory a zkontroluj ho.

Zaměř se na:
1. Věcná správnost — souhlasí mluvený obsah s tím, co je v kódu / SHOW.md / GLOSSARY.md?
2. Tok vyprávění — je logická návaznost? Chybí přechody nebo vysvětlení?
3. Jazyk — je tón přiměřený cílovému publiku (mládež, začátečníci)?
4. Délka — jsou některé části zbytečně dlouhé nebo naopak příliš stručné?
5. Konzistence — odpovídají termíny GLOSSARYu projektu?

Výstup: strukturovaný seznam poznámek + konkrétní návrhy přepisů (ne jen "zlepšit").

Přepis epizody:
[VLOŽ PŘEPIS]
```

---

## 3. Kontrola konzistence termínů

```
Zkontroluj následující text vůči GLOSSARY.md projektu PocketStory.
Označ každý termín, který:
- používá nesprávný název (např. "postava" místo CHAR, "hromada" místo SUMS)
- chybí v GLOSSARYu a měl by tam být přidán
- je použit nekonzistentně v různých částech textu

Text ke kontrole:
[VLOŽ TEXT]
```

---

## 4. Návrh vizuálů pro epizodu

```
Na základě skriptu epizody č. [N] navrhni seznam vizuálních momentů vhodných pro screenshot nebo screencast.

Pro každý vizuál uveď:
- Časová značka (odhadovaná)
- Co přesně zobrazit (konzole, kód, diagram, animace?)
- Zda jde o statický screenshot nebo živou ukázku (screencast)
- Případné anotace / popisky přímo v záznamu

Skript epizody:
[VLOŽ SKRIPT]
```

---

*Soubor průběžně rozšiřován podle potřeb produkce.*
