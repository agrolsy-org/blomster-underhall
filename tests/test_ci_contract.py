"""CI-kontrakt: publika PR:er får aldrig köra på privat beständig VM."""
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_public_ci_uses_hosted_runners_and_no_private_workflow():
    for name in ("validate.yml", "security-audit.yml", "code-review.yml"):
        content = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
        assert "runs-on: ubuntu-latest" in content
        assert "self-hosted" not in content
        assert "uses: agrolsy-org/wp-plugin-ci" not in content
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "blomster-underhall-ci" not in readme
    assert "ubuntu-latest" in readme
