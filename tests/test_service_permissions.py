"""Regressionstester för tjänsternas adminspärr utan HA-installation."""

import asyncio
import importlib.util
from pathlib import Path
import sys
import types

import pytest

COMPONENT = Path(__file__).parents[1] / "custom_components/blomster_maintenance"


def load_permissions(monkeypatch):
    class Unauthorized(Exception):
        def __init__(self, **kwargs):
            self.details = kwargs

    class UnknownUser(Exception):
        def __init__(self, **kwargs):
            self.details = kwargs

    for name in ("homeassistant", "homeassistant.core", "homeassistant.exceptions"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    sys.modules["homeassistant.core"].HomeAssistant = object
    sys.modules["homeassistant.core"].ServiceCall = object
    sys.modules["homeassistant.exceptions"].Unauthorized = Unauthorized
    sys.modules["homeassistant.exceptions"].UnknownUser = UnknownUser

    spec = importlib.util.spec_from_file_location("permissions_fixture", COMPONENT / "permissions.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


class Auth:
    def __init__(self, user):
        self.user = user

    async def async_get_user(self, _user_id):
        return self.user


def call(user_id):
    return types.SimpleNamespace(context=types.SimpleNamespace(user_id=user_id))


def test_vanlig_anvandare_nekas(monkeypatch):
    permissions = load_permissions(monkeypatch)
    hass = types.SimpleNamespace(auth=Auth(types.SimpleNamespace(is_admin=False)))

    with pytest.raises(permissions.Unauthorized):
        asyncio.run(permissions.async_require_admin(hass, call("user-1")))


def test_administrator_tillats(monkeypatch):
    permissions = load_permissions(monkeypatch)
    hass = types.SimpleNamespace(auth=Auth(types.SimpleNamespace(is_admin=True)))

    asyncio.run(permissions.async_require_admin(hass, call("admin-1")))


def test_intern_automation_utan_anvandare_tillats(monkeypatch):
    permissions = load_permissions(monkeypatch)
    hass = types.SimpleNamespace(auth=Auth(None))

    asyncio.run(permissions.async_require_admin(hass, call(None)))


def test_okand_anvandare_nekas(monkeypatch):
    permissions = load_permissions(monkeypatch)
    hass = types.SimpleNamespace(auth=Auth(None))

    with pytest.raises(permissions.UnknownUser):
        asyncio.run(permissions.async_require_admin(hass, call("missing")))
