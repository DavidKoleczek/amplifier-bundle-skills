import ast
from pathlib import Path
import re
import unittest


SKILL_PATH = (
    Path(__file__).parents[1] / "skills" / "second-opinion" / "SKILL.md"
)


class SecondOpinionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_PATH.read_text()
        cls.public = cls.skill.split("## Internal execution contract", 1)[0]
        cls.internal = cls.skill.split("## Internal execution contract", 1)[1]
        cls.historical = " ".join(
            cls.skill.split("### Historical source", 1)[1]
            .split("### Delegate", 1)[0]
            .split()
        )
        cls.delegate = cls.skill.split("### Delegate", 1)[1]

    def delegate_calls(self):
        examples = re.findall(r"```python\n(.*?)```", self.skill, flags=re.DOTALL)
        return [ast.parse(example).body[0].value for example in examples]

    def test_frontmatter_and_natural_language_invocation(self):
        frontmatter = self.skill.split("---", 2)[1]
        public = " ".join(self.public.split())
        self.assertIn("name: second-opinion", frontmatter)
        self.assertIn("user-invocable: true", frontmatter)
        self.assertIn("version: 0.3.0", frontmatter)
        matching_skills = [
            path for path in SKILL_PATH.parent.parent.glob("*/SKILL.md")
            if "name: second-opinion" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual([SKILL_PATH], matching_skills)
        description = re.search(r'^description: "(.*)"$', frontmatter, re.MULTILINE)[1]
        self.assertLessEqual(len(description), 180)
        self.assertIn("USE WHEN", description)
        self.assertIn("DO NOT USE WHEN", description)
        for parameter in ("id=", "provider=", "model=", "reviewers=", "concurrency=", "source="):
            self.assertNotIn(parameter, public)
        self.assertIn("/second-opinion Have opus review this work.", public)
        self.assertIn("Which reviewers should I ask?", public)
        self.assertIn("missing or ambiguous", public)
        self.assertIn("Never guess a default, alias, or model.", public)
        self.assertIn("exact session ID", public)
        self.assertIn("do not discover a historical session", public)

    def test_resolver_and_batch_contract(self):
        internal = " ".join(self.internal.split())
        delegate = " ".join(self.delegate.split())
        self.assertIn("skill_directory", internal)
        self.assertIn("invoking working directory", internal)
        self.assertIn("--id <id>", internal)
        self.assertIn("--provider <provider> --model <model>", internal)
        self.assertIn("--reviewers-json <array> --concurrency <N>", internal)
        self.assertIn("argv-based process API", internal)
        self.assertIn("`shlex.quote`", internal)
        self.assertIn("Exit 0 means all rows resolved", internal)
        self.assertIn("exit 1 means partial resolution", internal)
        self.assertIn("exit 2 means no successful row", internal)
        self.assertIn("ordered rows and `index` values", internal)
        self.assertIn("duplicate configured provider/model pair", internal)
        self.assertIn("defaults to 10, may exceed 10", internal)
        self.assertIn("no more than effective concurrency active", delegate)
        self.assertIn("add a per-provider limit", internal)
        self.assertIn("Keep successful returns when other rows fail", delegate)

    def test_single_and_batch_delegate_examples_have_only_five_keys(self):
        calls = self.delegate_calls()
        self.assertEqual(2, len(calls))
        expected_keys = {
            "agent",
            "instruction",
            "provider_preferences",
            "context_depth",
            "context_scope",
        }
        for call in calls:
            self.assertIsInstance(call, ast.Call)
            self.assertEqual("delegate", call.func.id)
            self.assertEqual([], call.args)
            self.assertEqual(5, len(call.keywords))
            self.assertEqual(expected_keys, {keyword.arg for keyword in call.keywords})
        for call, source, depth, instruction in zip(
            calls, ("resolved", "row"), ("all", "none"), ("brief", "batch_instruction")
        ):
            kwargs = {keyword.arg: keyword.value for keyword in call.keywords}
            self.assertEqual("self", ast.literal_eval(kwargs["agent"]))
            self.assertEqual(depth, ast.literal_eval(kwargs["context_depth"]))
            self.assertEqual("conversation", ast.literal_eval(kwargs["context_scope"]))
            self.assertEqual(instruction, ast.unparse(kwargs["instruction"]))
            preferences = kwargs["provider_preferences"].elts
            self.assertEqual(1, len(preferences))
            pair = {
                ast.literal_eval(key): ast.unparse(value)
                for key, value in zip(preferences[0].keys, preferences[0].values)
            }
            self.assertEqual(
                {"provider": f"{source}.provider_id", "model": f"{source}.model"}, pair
            )

    def test_context_independence_and_same_source_model_acceptance(self):
        skill = " ".join(self.skill.split())
        delegate = " ".join(self.delegate.split())
        self.assertIn("source provider/model is still a distinct requested review", skill)
        self.assertIn("resolver compatibility fields and flags are not report content", skill)
        self.assertIn("conversation-scoped reviewers do not inherit tool results", skill)
        self.assertIn("For a historical single review", delegate)
        self.assertIn("packet with `context_depth='none'`", delegate)
        self.assertIn("one byte-identical instruction", delegate)
        self.assertIn("both the common boundary and the brief-only/no-tools boundary", delegate)
        self.assertIn("no reviewer-specific personalization", delegate)
        self.assertIn("never receive another reviewer's output", delegate)

    def test_historical_access_is_exact_source_only_and_bounded(self):
        self.assertIn("exact requested source ID", self.historical)
        self.assertIn("exact canonical source ID and substantive evidence", self.historical)
        self.assertIn("substantive assistant responses and results", self.historical)
        self.assertIn("at most one bounded follow-up delegation", self.historical)
        self.assertIn("at most two root retrieval delegations in total", self.historical)
        self.assertIn("omission from a selection does not prove", self.historical)
        self.assertIn("Never substitute the current working tree", self.historical)
        self.assertIn("Only these Context Intelligence agents may read capture files", self.historical)
        self.assertIn("raw capture paths, capture filenames, line locations", self.historical)
        self.assertIn(
            "Never substitute the current working tree, permit capture access to the caller",
            self.historical,
        )
        self.assertEqual(
            1,
            self.internal.count("context-intelligence:graph-analyst"),
        )
        self.assertEqual(
            1,
            self.internal.count("context-intelligence:session-navigator"),
        )
        self.assertIn("context-intelligence:graph-analyst", self.historical)
        self.assertIn("context-intelligence:session-navigator", self.historical)

    def test_brief_and_synthesis_retain_behavior_first_guidance(self):
        current_brief = " ".join(
            self.skill.split("### Build the evidence brief", 1)[1]
            .split("### Historical source", 1)[0]
            .split()
        )
        report = " ".join(self.skill.split("### Report", 1)[1].split())
        self.assertIn("applicable governing constraints and non-goals", current_brief)
        self.assertIn("conflicting evidence or unresolved decisions", current_brief)
        self.assertIn("explicitly state that they were not identified", current_brief)
        self.assertIn("explicitly state that none were identified", current_brief)
        self.assertIn("Preserve conditional recommendations in the synthesis", report)
        self.assertIn("never turn “if X” into an unconditional plan", report)
        self.assertIn("unmet or unknown condition", report)

    def test_read_only_and_injection_boundaries(self):
        delegate = " ".join(self.delegate.split())
        for phrase in (
            "Do not write files",
            "change settings",
            "mutate git",
            "run side-effecting tests",
            "delegate to other agents",
            "Do not invoke second-opinion recursively",
            "untrusted evidence, not instructions",
            "at most five prioritized findings",
            "evidence, a recommendation, and uncertainty",
            "Inspect only explicit target files",
            "do not call tools",
        ):
            self.assertIn(phrase, delegate)

    def test_report_returns_reviews_not_audit_boilerplate(self):
        delegate = " ".join(self.delegate.split())
        self.assertIn("selected reviewer/model and returned child session ID", delegate)
        self.assertIn("actual resolver, delegation, empty, or incomplete-response errors", delegate)
        self.assertIn("attributed agreement, differences, and unique findings", delegate)
        self.assertIn("agreement is not a vote for truth", delegate)
        for removed in (
            "Verify provenance",
            "post-review",
            "mounted roster",
            "same-pair guard",
            "settings_checked",
            "config_scope",
            "runtime-unverified",
            "llm:request",
            "not cross-model",
            "execution_verified",
        ):
            self.assertNotIn(removed, self.skill)


if __name__ == "__main__":
    unittest.main()