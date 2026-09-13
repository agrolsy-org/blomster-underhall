"""Separat reproduktion: en negativ första mätpunkt räknas in i förbrukningen."""
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

spec = spec_from_file_location('negative_meter_repro', Path(__file__).parents[2] / 'custom_components/blomster_maintenance/calculations.py')
assert spec and spec.loader
module = module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
start = datetime(2026, 9, 13, tzinfo=timezone.utc)
result = module.accumulated_meter_total([module.MeterSample(-1, start), module.MeterSample(8, start + timedelta(hours=1))])
assert result == 8, f'Negativ första mätpunkt ska ignoreras; förväntat 8, faktiskt {result}'
