# Lagringsformat och återställning

`const.py` definierar `STORAGE_VERSION = 1` och nyckeln
`blomster_maintenance.data`. `storage.py` skapar HA:s `Store(hass, version, key)`.
Datan finns i HA-konfigurationens `.storage/blomster_maintenance.data`, inuti
HA:s versionsomslag. `async_save` skriver ett objekt med `water` som objekt och
`items` som lista av objekt; varje item innehåller sin `events`-lista. Det finns
ingen SQL-tabell eller egen databas i integrationen. Recorder är en separat läskälla
för import av vattenhistorik, inte ägare av underhållsposterna.

Fältlistan nedan härleds från dataklasserna. ISO-datum/tider sparas som strängar;
performed_at och last_updated skapas med lokal tidszon i ISO-format. Konfigurationspostens
installationsdatum lagras separat även i Store. item_id identifierar ett objekt,
event_id är ett UUID i hexformat och identifierar historikposten inom objektet.

### MaintenanceEvent

| Fält | Python-typ | Standard vid ny post |
| --- | --- | --- |
| `event_id` | `str` | `krävs` |
| `performed_at` | `str` | `krävs` |
| `meter_value` | `float | None` | `None` |
| `meter_entity` | `str | None` | `None` |
| `meter_unit` | `str | None` | `None` |
| `note` | `str | None` | `None` |
| `cost` | `float | None` | `None` |

### MaintenanceItem

| Fält | Python-typ | Standard vid ny post |
| --- | --- | --- |
| `item_id` | `str` | `krävs` |
| `name` | `str` | `krävs` |
| `category` | `str | None` | `None` |
| `location` | `str | None` | `None` |
| `manufacturer` | `str | None` | `None` |
| `model` | `str | None` | `None` |
| `serial_number` | `str | None` | `None` |
| `installed_at` | `str | None` | `None` |
| `interval_type` | `str | None` | `None` |
| `interval_value` | `float | None` | `None` |
| `meter_entity` | `str | None` | `None` |
| `manual_url` | `str | None` | `None` |
| `receipt_url` | `str | None` | `None` |
| `image_url` | `str | None` | `None` |
| `warning_entities` | `list[str]` | `field(default_factory=list)` |
| `acknowledged_signature` | `str | None` | `None` |
| `events` | `list[MaintenanceEvent]` | `field(default_factory=list)` |

### WaterAccumulator

| Fält | Python-typ | Standard vid ny post |
| --- | --- | --- |
| `source_entity` | `str | None` | `None` |
| `installation_date` | `str | None` | `None` |
| `accumulated_liters` | `float` | `0.0` |
| `last_source_value` | `float | None` | `None` |
| `last_updated` | `str | None` | `None` |
| `baseline_established` | `bool` | `False` |
| `imported_from_recorder` | `bool` | `False` |

## Kompatibilitet

En tom eller saknad Store laddas som standardvärden och tom objektlista. Load ger
äldre vattenposter baseline_established utifrån om accumulated_liters är skilt från
noll och imported_from_recorder=False om flaggorna saknas. Äldre items får valfria
fältens standardvärden. Äldre events utan event_id får ett nytt UUID och cost=None
om kostnad saknas. Tilldelning av ID utlöser async_save vid laddning; nästa laddning
behåller samma ID och ska inte migrera igen.

Detta är normalisering inom lagringsversion1, inte en registrerad version-till-version-
migrering. Okända dataklassfält eller saknade obligatoriska fält kan få load att
misslyckas; integrationen filtrerar inte bort dem och återställer inte automatiskt
från korrupt fil. Inför framtida inkompatibla fält krävs uttrycklig Store-migrering,
fixtures från föregående version och test av upprepad laddning. Fälten får inte bara
bytas eller tas bort eftersom det skulle förlora historik/baslinje.

## Säker återställning

Ta en HA-backup med både integrationskonfigurationen och `.storage` före manuella
ändringar eller uppgradering. Stoppa HA innan `.storage` återställs så att en senare
async_save inte skriver över filen. Återställ HA:s hela versionsomslag för denna Store,
inte bara items-listan, och använd en integrationsversion som kan läsa formatet.
Starta HA och kontrollera konfigurerad vattenkälla, baslinje, total, objekt och historik.
Återställ Recorder separat om historikimport behövs; partiell Recorder-data ersätter
inte den sparade totalen. CI:s offline-fixtures verifierar normalisering och idempotens,
inte en verklig backup/restore på hemnets installation.

Källor: `const.py`, `storage.py::async_load/async_save`, `water.py::async_import_water_history`.
