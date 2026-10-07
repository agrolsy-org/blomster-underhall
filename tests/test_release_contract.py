"""Release-kontrakt: manifestets version ska stämma med cache-URL och dokumentation."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
COMPONENT = ROOT / "custom_components/blomster_maintenance"


def manifest_version() -> str:
    return json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))["version"]


def test_card_cache_version_matches_manifest():
    frontend = (COMPONENT / "frontend.py").read_text(encoding="utf-8")
    match = re.search(r'CARD_URL = ".*\?v=([^"]+)"', frontend)
    assert match, "CARD_URL saknar ?v=-version"
    assert match.group(1) == manifest_version()


def test_documentation_claims_match_manifest():
    version = manifest_version()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Version {version} hanterar" in readme
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    assert f"Avstämd mot integration {version}." in architecture
