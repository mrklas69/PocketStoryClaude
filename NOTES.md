Vysvětlení:
    Engine = HW + firmware + ovladače
    Svět.json = SW

# Úrovně enginu PocketStory

## Verze 1.0 (Kontrola světa)
- Umí načíst, zkontrolovat, uložit strukturu světa (soubor JSON).
- Vypíše do konzole název, popis a další údaje hlavičky struktury. Načte počet Entit a Relací, zkontroluje správnost definice (dodržení pravidel). Umí vypsat statistiky (např. prostředí, postavy, unikáty a součtovatelné, definované typy relací), zjištěné chyby a varování.

## Verze 2.0 (Prostor a čas)
- K předešlé verzi přidává prostředí a čas jako hlavní metriky světa.
- V přívětivé konzoli (barvy, emoji) umí zobrazit stromovou hierarchii prostředí a kontejnerů. U postav zobrazuje RANK a progress bar hodnoty HP.
- Podporuje parametry Tick a Delay pro znázornění dynamiky světa.
- Konzole obsahuje také okno pro výpis událostí.

## Verze ??? (Pokročilá konzole)
- Konzole obsahuje příkazový řádek, kde lze psát příkazy a simulaci řídit př. TASK(KING_HEROLD, FEED, BYGUL).


