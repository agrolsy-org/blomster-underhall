# Regressionsinventering 2026-09-13

4 → 11 pytest-tester, alla gröna: flera mätarreset, nollor, fraktioner,
duplicerade värden, indata bevaras, tom historik och exakt toleransgräns.
Kör `python -m pytest tests -q` samt `python -m compileall -q custom_components`.
Befintlig PR-CI kör pytest, compileall, hassfest och HACS. Inga deploymentsteg tillkommer.

Detta är organisationens publika repo. Main skyddas nu med obligatoriska
GitHub Actions-checkar för tests, hassfest, hacs, secret-scan samt
Regressionstester genomförda, även för admins och med uppdaterad branch.
Den nya grinden kräver faktiskt success för alla tre valideringsjobben;
skipped/cancelled/failure godtas inte. Fork-jobben kör fortsatt inte PR-kod
på den beständiga runnern; en sådan PR behöver testas från en betrodd branch.

## Reproducerat beräkningsfel

Kör separat `python tests/known_defects/negative_initial_meter.py` (röd).
Första mätpunkten -1 följd av 8 ger faktisk total 9, medan negativa senare
mätpunkter ignoreras. Förväntat enligt befintligt regressionstest för negativa
värden: negativ mätpunkt ska inte öka förbrukningen, resultat 8.
Kodväg: accumulated_meter_total sätter previous till det första negativa värdet.
Risk: normal; fel importerad förbrukning kan påverka underhållsbehov/påminnelser.
Produktionskoden ändras inte. Reproduktionen ingår inte i den gröna standardsviten.

Kvarvarande luckor: HA-runtime/entities, storage/reminders och servicebehörigheter.
