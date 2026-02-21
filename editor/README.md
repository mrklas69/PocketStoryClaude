# PocketStory World Editor

Webový editor pro `worlds/*.json` soubory.

## Spuštění

Z kořenového adresáře projektu:

```bash
uvicorn editor.server:app --reload --port 8787
```

Pak otevři: **http://localhost:8787**

## Funkce

- Výběr světa z dropdownu
- Editace metadat světa (název, popis)
- Záložky dle typu: Entity, LOCATION, SKILL, TYPE_OF, BEHAVIOR, EDGE, PRODUCE, TRIGGER, CONSUME
- Fulltextové vyhledávání a řazení sloupců
- Klik na řádek (nebo ✏) → modální dialog s plným formulářem
- Duplikovat záznam (předvyplněná kopie)
- Smazat záznam
- Přidat nový záznam
- Uložit zpět do JSON souboru (PUT /worlds/{name})
- Export JSON (stažení souboru)
