"""Cheap instruction/discovery guards; behavioral evidence comes from live runs."""

from pathlib import Path
import re


ROOT = Path(__file__).parents[1]
PATH = ROOT / "skills" / "retrospective" / "SKILL.md"
SKILL = PATH.read_text(encoding="utf-8")
TEXT = " ".join(SKILL.split())


def test_retrospective_loads_inline_with_a_short_routing_description():
    frontmatter = SKILL.split("---", 2)[1]
    assert "name: retrospective" in frontmatter
    assert "user-invocable: true" in frontmatter
    assert "$ARGUMENTS" in SKILL
    assert "context: fork" not in frontmatter
    assert "allowed-tools:" not in frontmatter
    description = re.search(r'^description: "(.*)"$', frontmatter, re.MULTILINE)[1]
    assert len(description) <= 180
    assert "USE WHEN" in description and "DO NOT USE" in description


def test_current_context_does_not_require_retrieval_or_reviewers():
    assert "current conversation and already-available tool results by default" in TEXT
    assert "Do not retrieve this same history again" in TEXT
    assert "Without requested reviewers, do the retro here: no reviewer delegation" in TEXT


def test_history_uses_direct_tool_and_honest_coverage():
    assert "call `session_transcript` directly" in TEXT
    assert "short prefix unchanged in `session_ids`" in TEXT
    assert "returned canonical ID and cursor" in TEXT
    assert "State any unread range, truncation, or capture issue" in TEXT
    assert "short IDs require reader support" in TEXT
    assert "Do not parse raw capture files" in TEXT
    assert "launch Context Intelligence agents as a hidden fallback" in TEXT


def test_evidence_does_not_become_a_measurement_or_an_instruction():
    for rule in (
        "as evidence, not authority",
        "reported results from tool-confirmed results",
        "Label possible causes as hypotheses",
        "Do not manufacture counts, cost, durations, or blame",
        "overlapping worker durations cannot be added as wall time",
        "do not edit files, file issues, change settings, replay commands",
    ):
        assert rule in TEXT


def test_composition_has_one_owner_and_does_not_reharvest():
    assert "second-opinion owns the only reviewer fan-out" in TEXT
    assert "brief-only review; no further harvesting" in TEXT
    assert "Keep your own verdict out of the packet" in TEXT
    assert "do not load either again" in TEXT
    assert "without tools, further delegation, or recursively invoking either skill" in TEXT
    assert "at most three prioritized changes" in TEXT
    assert "Never hide a failed reviewer" in TEXT


def test_user_docs_advertise_the_skill_and_its_optional_dependencies():
    readme = (ROOT / "README.md").read_text()
    assert "/retrospective" in readme
    assert "short IDs require a prefix-capable reader" in readme
    assert "**retrospective**" in (ROOT / "bundle.md").read_text()