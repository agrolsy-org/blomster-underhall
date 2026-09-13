# Regressionsinventering 2026-09-13

4 → 11 pytest-tester, alla gröna: flera mätarreset, nollor, fraktioner,
duplicerade värden, indata bevaras, tom historik och exakt toleransgräns.
Kör `python -m pytest tests -q` samt `python -m compileall -q custom_components`.
Befintlig PR-CI kör pytest, compileall, hassfest och HACS. Inga deploymentsteg tillkommer.

## Reproducerat beräkningsfel

Kör separat `python tests/known_defects/negative_initial_meter.py` (röd).
Första mätpunkten -1 följd av 8 ger faktisk total 9, medan negativa senare
mätpunkter ignoreras. Förväntat enligt befintligt regressionstest för negativa
värden: negativ mätpunkt ska inte öka förbrukningen, resultat 8.
Kodväg: accumulated_meter_total sätter previous till det första negativa värdet.
Risk: normal; fel importerad förbrukning kan påverka underhållsbehov/påminnelser.
Produktionskoden ändras inte. Reproduktionen ingår inte i den gröna standardsviten.

Kvarvarande luckor: HA-runtime/entities, storage/reminders och servicebehörigheter.
