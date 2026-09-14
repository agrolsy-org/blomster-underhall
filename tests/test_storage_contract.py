"""Lagringstester utan HA-installation eller verklig .storage."""
import asyncio
import ast
import copy
import importlib.util
from pathlib import Path
import sys
import types

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components/blomster_maintenance"


def load_storage(monkeypatch, raw):
    class FakeStore:
        def __class_getitem__(cls, _):
            return cls
        def __init__(self, hass, version, key):
            self.version, self.key = version, key
            self.raw, self.saves = copy.deepcopy(raw), 0
        async def async_load(self):
            return copy.deepcopy(self.raw)
        async def async_save(self, raw):
            self.raw = copy.deepcopy(raw)
            self.saves += 1
    for name in ("homeassistant", "homeassistant.core", "homeassistant.helpers", "homeassistant.helpers.storage"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    sys.modules["homeassistant.core"].HomeAssistant = object
    sys.modules["homeassistant.helpers.storage"].Store = FakeStore
    package = types.ModuleType("storage_fixture")
    package.__path__ = [str(COMPONENT)]
    monkeypatch.setitem(sys.modules, "storage_fixture", package)
    for name in ("const", "storage"):
        spec = importlib.util.spec_from_file_location("storage_fixture." + name, COMPONENT / (name + ".py"))
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
    return module.MaintenanceStore(object())


def test_legacy_event_migration_is_saved_once_and_keeps_id(monkeypatch):
    store = load_storage(monkeypatch, {"water": {"accumulated_liters": 25}, "items": [{
        "item_id": "filter", "name": "Filter", "events": [{"performed_at": "2026-01-01T12:00:00+01:00"}]
    }]})
    asyncio.run(store.async_load())
    event_id = store.items["filter"].events[0].event_id
    assert len(event_id) == 32 and store._store.saves == 1
    assert store.items["filter"].events[0].cost is None
    assert store.water.baseline_established and not store.water.imported_from_recorder
    asyncio.run(store.async_load())
    assert store.items["filter"].events[0].event_id == event_id
    assert store._store.saves == 1


def test_store_round_trip_preserves_all_data_and_version(monkeypatch):
    store = load_storage(monkeypatch, None)
    asyncio.run(store.async_load())
    assert store._store.key == "blomster_maintenance.data" and store._store.version == 1
    asyncio.run(store.async_configure_item("filter", "Filter", interval_type="months", interval_value=6))
    event = asyncio.run(store.async_record("filter", "Filter", 42.0, "sensor.water", "L", "Byte", 99.0))
    saved = copy.deepcopy(store._store.raw)
    asyncio.run(store.async_load())
    asyncio.run(store.async_save())
    assert store._store.raw == saved
    assert store.items["filter"].events[0].event_id == event.event_id
    assert set(saved) == {"water", "items"}


def test_storage_docs_cover_every_dataclass_field():
    source = ast.parse((COMPONENT / "storage.py").read_text(encoding="utf-8"))
    docs = (ROOT / "docs/storage.md").read_text(encoding="utf-8")
    for node in source.body:
        if isinstance(node, ast.ClassDef) and node.name in {"MaintenanceItem", "MaintenanceEvent", "WaterAccumulator"}:
            section = docs.split("### " + node.name + "\n", 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
            actual = {n.target.id for n in node.body if isinstance(n, ast.AnnAssign)}
            documented = {line.split("`")[1] for line in section.splitlines() if line.startswith("| `")}
            assert documented == actual
