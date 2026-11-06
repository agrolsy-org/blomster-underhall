try:
    import pytest_homeassistant_custom_component  # noqa: F401
except ImportError:
    pytest_plugins = []
else:
    pytest_plugins = ["pytest_homeassistant_custom_component.common"]
