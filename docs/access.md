# Åtkomst och tjänstekontrakt

Standarddashboarden skapas i `frontend.py` med `require_admin: False`; även
`async_register_built_in_panel` använder `require_admin=False`. Inloggade vanliga
HA-användare ska alltså kunna se panelen. Panelens synlighet är inte en behörighetsgrind
för dess tjänster. Befintliga dashboards behåller sina egna inställningar.

Integrationens sex tjänster registreras med `hass.services.async_register` i
`__init__.py`. De har ingen egen kontroll av `call.context.user_id`, adminstatus eller
entitetsbehörighet. De är därför inte adminbegränsade eller ett separat skrivskydd för
läsanvändare. HA:s autentisering för webb-/WebSocket-anrop finns kvar; lokala automationer
kan också anropa tjänster utan användarkontext. Döljning av knappar eller sidebar ändrar
inte denna gräns. Detta är nuvarande delade hushållskontrakt, inte en garanti om separata
roller. Använd inte integrationen för data som måste isoleras mellan HA-användare.

HA:s [officiella behörighetsdokumentation](https://developers.home-assistant.io/docs/auth_permissions/)
beskriver att egna tjänstehanterare behöver uttryckliga kontroller om admin- eller
entitetsbegränsning önskas. Ingen sådan rolländring införs av denna dokumentationsfix.

| Tjänst i blomster_maintenance | Invariant/effekt |
| --- | --- |
| set_water_baseline | Icke-negativa liter; sparar aktuell mätare, etablerar baslinje och rensar importflaggan. |
| configure_item | item_id/name krävs; tillåtna intervall och icke-negativt värde valideras; skapar eller uppdaterar objekt. |
| record_maintenance | item_id/name krävs; valfri kostnad är icke-negativ. Konfigurerad/angiven mätare måste vara tillgänglig och numerisk. Sparar UUID-post; valfritt tjänstesvar item_id/event_id. |
| delete_maintenance | item_id/event_id krävs; saknad post ger HomeAssistantError, annars sparas borttagningen. |
| import_water_history | Inga argument; ofullständig Recorder-historik ger HomeAssistantError, ingen partiell total sparas. |
| acknowledge_maintenance | item_id krävs och aktuellt problem måste finnas; sparar problemsignatur. |

Källor: `__init__.py` (scheman och registrering), `storage.py` (mutationer),
`frontend.py` (dashboard/panel), `services.yaml` (HA:s tjänstebeskrivningar).
