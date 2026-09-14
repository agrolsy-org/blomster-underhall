"""Kör workflowets riktiga JavaScript med offline-API-fixtures."""
import json
from pathlib import Path
import subprocess
import textwrap
import pytest

ROOT = Path(__file__).parents[1]
SHA = "a" * 40
SCRIPT = textwrap.dedent((ROOT / ".github/workflows/code-review.yml").read_text(encoding="utf-8").split("script: |\n", 1)[1])
HARNESS = r'''const fs = require("fs");
const fixture = JSON.parse(fs.readFileSync(0, "utf8"));
const pr = {number: 1, state: 'open', draft: false, base: {ref: 'main'}, head: {sha: fixture.sha}, html_url: 'https://example.test/pr/1'};
const context = {repo: {owner: 'fixture', repo: 'public'}, eventName: fixture.event || 'pull_request_target', payload: fixture.nonPr ? {issue: {number: 2}} : {pull_request: {number: 1}}};
let gets = 0;
const statuses = [];
const get = async () => ({data: {...pr, head: {sha: ++gets > 1 ? fixture.currentSha || fixture.sha : fixture.sha}}});
const github = {rest: {pulls: {get, list: 'pulls'}, issues: {listComments: 'comments'}, repos: {getCollaboratorPermissionLevel: async ({username}) => ({data: {permission: fixture.permissions?.[username] || 'read'}}), createCommitStatus: async s => statuses.push(s)}}, paginate: async what => what === 'comments' ? fixture.comments : [pr]};
(async () => { await (async () => { SCRIPT_PLACEHOLDER })();
process.stdout.write(JSON.stringify(statuses)); })().catch(e => {console.error(e); process.exit(1)});
'''


def run_gate(comments, **kwargs):
    result = subprocess.run(["node", "-e", HARNESS.replace("SCRIPT_PLACEHOLDER", SCRIPT)],
        input=json.dumps({"sha": SHA, "comments": comments, "permissions": {"maintainer": "write"}, **kwargs}), text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


def comment(sha=SHA, association="OWNER"):
    return {"body": "Granskad faktisk diff.\n<!-- manual-review:" + sha + " -->", "author_association": association, "user": {"login": "maintainer" if association == "OWNER" else "reader", "type": "User"}, "html_url": "https://example.test/review"}


def test_current_maintainer_review_passes():
    statuses = run_gate([comment()])
    assert statuses[0]["state"] == "success" and statuses[0]["sha"] == SHA


@pytest.mark.parametrize("comments", [[], [comment("b" * 40)], [comment(association="NONE")], [comment(association="CONTRIBUTOR")]])
def test_missing_stale_or_untrusted_review_does_not_pass(comments):
    assert run_gate(comments)[0]["state"] == "pending"


def test_new_push_during_check_does_not_stamp_old_commit():
    assert run_gate([comment()], currentSha="c" * 40) == []


def test_regular_issue_comment_is_ignored():
    assert run_gate([comment()], event="issue_comment", nonPr=True) == []


def test_org_member_with_read_permission_cannot_approve():
    assert run_gate([comment(association="MEMBER")])[0]["state"] == "pending"


def test_bot_cannot_supply_manual_review():
    c = comment()
    c["user"]["type"] = "Bot"
    assert run_gate([c])[0]["state"] == "pending"
