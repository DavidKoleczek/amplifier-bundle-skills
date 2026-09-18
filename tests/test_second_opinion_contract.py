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
        cls.historical = " ".join(
            cls.skill.split("### Historical source", 1)[1]
            .split("## Delegate exactly one reviewer", 1)[0]
            .split()
        )
        cls.report = " ".join(
            cls.skill.split("## Report returned metadata and findings", 1)[1].split()
        )
        cls.batch = " ".join(
            cls.skill.split("## Multiple reviewers", 1)[1]
            .split("## Report returned metadata and findings", 1)[0]
            .split()
        )
        cls.batch_delegate = cls.skill.split("## Multiple reviewers", 1)[
            1
        ].split("```python", 1)[1].split("```", 1)[0]

    def test_only_skill_frontmatter_uses_new_invocable_name(self):
        matching_skills = [
            path
            for path in SKILL_PATH.parent.parent.glob("*/SKILL.md")
            if "name: second-opinion" in path.read_text(encoding="utf-8")
        ]
        self.assertEqual([SKILL_PATH], matching_skills)
        frontmatter = self.skill.split("---", 2)[1]
        self.assertIn("name: second-opinion", frontmatter)
        self.assertIn("user-invocable: true", frontmatter)
        self.assertNotIn("review-current-session", self.skill)

    def test_description_is_routing_complete_and_fits_the_render_cap(self):
        description = (
            "Independent review of current work or a past session. USE WHEN a "
            "user wants a second opinion. DO NOT USE WHEN ordinary code review "
            "is wanted — use code-review."
        )
        frontmatter = self.skill.split("---", 2)[1]
        self.assertIn(f'description: "{description}"', frontmatter)
        self.assertLessEqual(len(description), 180)
        self.assertTrue(description.startswith("Independent review"))
        self.assertIn("USE WHEN", description)
        self.assertIn("DO NOT USE WHEN", description)
        self.assertIn("code-review", description)

    def test_public_usage_is_natural_language_before_internal_contract(self):
        self.assertLess(
            self.skill.index("## Usage"),
            self.skill.index("## Internal execution contract"),
        )
        for example in (
            "/second-opinion Have opus review this work.",
            "/second-opinion Have astra, fable, and Gemini Flash review this work independently.",
            "/second-opinion Ask astra to review the design decisions from session <session ID>.",
            "/second-opinion Use the reviewers we named, with up to twenty running at once.",
        ):
            self.assertIn(example, self.public)
        self.assertIn("illustrative, not verified aliases", self.public)
        self.assertIn("Which reviewers should I ask?", self.public)
        self.assertIn("Never ask the user for JSON", " ".join(self.public.split()))
        for structured_parameter in (
            "review-current-session",
            "id=",
            "provider=",
            "model=",
            "reviewers=",
            "concurrency=",
            "source=",
        ):
            self.assertNotIn(structured_parameter, self.public)

    def test_internal_contract_retains_normalization_and_source_rules(self):
        internal = self.skill.split("## Internal execution contract", 1)[1]
        self.assertIn(
            "Normalize a human reviewer list into the existing selector shapes.", internal
        )
        self.assertIn(
            "For one chosen reviewer, use the legacy single-review path", internal
        )
        self.assertIn(
            "For multiple chosen reviewers, use the batch path: no conversation",
            internal,
        )
        self.assertIn("The source is current unless the user requests an older session.", internal)
        self.assertIn("defaults to 10, may exceed 10", internal)

    def test_historical_harvest_limits_capture_access_to_caller_and_source(self):
        self.assertIn("the exact caller ID and source ID here", self.historical)
        self.assertNotIn("exact returned reviewer child ID", self.historical)
        self.assertNotIn("post-review provenance", self.historical)
        self.assertIn("Only these Context Intelligence agents may parse session captures", self.historical)

    def test_historical_harvest_requires_substantive_evidence(self):
        self.assertIn(
            "bounded, paginated, task-relevant semantic projection", self.historical
        )
        self.assertIn("substantive assistant response or tool result", self.historical)
        self.assertIn("Lifecycle/status-only evidence is inadequate", self.historical)
        self.assertIn("bounded follow-up extraction", self.historical)
        self.assertIn("not evidence that the source omitted it", self.historical)

    def test_historical_brief_separates_evidence_from_capture_references(self):
        self.assertIn("Build the reviewer brief anew", self.historical)
        self.assertIn("only H-labels, substantive excerpts, and coverage gaps", self.historical)
        self.assertIn("capture filenames, line locations", self.historical)
        self.assertIn("mapping in the parent", self.historical)

    def test_report_uses_delegation_metadata_without_claiming_actual_routing(self):
        self.assertIn(
            "returned delegation's routing preferences from `provider_routing`",
            self.report,
        )
        self.assertIn("its `metadata.llm_calls` value when present", self.report)
        self.assertIn("`provider_routing` echoes the requested preferences", self.report)
        self.assertIn("does not observe which model answered", self.report)
        self.assertIn("actual provider, model, account, and instance execution", self.report)
        self.assertIn("not independently audited", self.report)

    def test_report_handles_missing_metadata_without_post_review_work(self):
        self.assertIn('report it as "not reported."', self.report)
        self.assertIn(
            "Do not retry the reviewer or start provenance work solely because metadata is missing.",
            self.report,
        )
        self.assertNotIn("context-intelligence:graph-analyst", self.report)
        self.assertNotIn("llm:request", self.report)

    def test_report_settings_scope_is_not_runtime_routing_scope(self):
        self.assertIn("retained resolver result", self.report)
        self.assertIn("`config_scope`", self.report)
        self.assertIn("not `provider:resolve.scope`", self.report)

    def test_batch_command_defaults_to_ten_and_allows_larger_positive_concurrency(self):
        self.assertIn("Ten reviews may run at once by default", self.public)
        self.assertIn(
            "ask for a larger positive number when you want more than ten",
            self.public,
        )
        self.assertIn("default 10", self.batch)
        self.assertIn("may exceed 10", " ".join(self.skill.split()))
        self.assertIn("positive integer", " ".join(self.skill.split()))
        self.assertIn(
            "neither a reviewer-count cap nor a per-provider cap",
            " ".join(self.skill.split()),
        )

    def test_batch_resolves_ordered_rows_once_and_continues_partial_successes(self):
        self.assertIn(
            'python3 "<skill_directory>/scripts/resolve_provider.py" --reviewers-json',
            self.batch,
        )
        self.assertIn("--concurrency N", self.batch)
        self.assertIn("load the provider list once", self.batch)
        self.assertIn("ordered `reviewers` rows and their `index` values", self.batch)
        self.assertIn("Exit 0 means all resolved", self.batch)
        self.assertIn("exit 1 means partial resolution and continues with only successful rows", self.batch)
        self.assertIn("exit 2 means none resolved or a global error and stops", self.batch)
        self.assertIn("known live-roster absence is a row error", self.batch)
        self.assertIn("duplicate resolved provider/model pair is a row error", self.batch)
        self.assertIn("Preserve every row error", self.batch)

    def test_batch_passes_safe_json_and_assigns_shared_citation_labels(self):
        self.assertIn("argv-based process API", self.batch)
        self.assertIn("`shlex.quote` to every dynamic argument", self.batch)
        self.assertIn("never paste unescaped selector JSON", self.batch)
        self.assertIn("Assign stable H-labels", self.batch)
        self.assertIn("for both current and historical batch sources", self.batch)
        self.assertIn(
            "do not first run the legacy single-selector resolver",
            " ".join(self.skill.split()),
        )

    def test_batch_delegations_are_identical_no_tools_and_exactly_five_keys(self):
        self.assertIn("byte-identical instruction string", self.batch)
        self.assertIn("do not personalize it with a reviewer name, requested provider, or", self.batch)
        self.assertIn("brief-only/no-tools boundary", self.batch)
        self.assertIn("do not call any tools", self.batch)
        self.assertIn("This applies to both current and historical batch sources", self.batch)
        self.assertEqual(
            [
                "agent",
                "instruction",
                "provider_preferences",
                "context_depth",
                "context_scope",
            ],
            re.findall(r"^\s{4}([a-z_]+)=", self.batch_delegate, flags=re.MULTILINE),
        )
        self.assertIn("agent='self'", self.batch_delegate)
        self.assertIn("context_depth='none'", self.batch_delegate)
        self.assertIn("context_scope='conversation'", self.batch_delegate)
        self.assertNotIn("model_role", self.batch_delegate)
        self.assertNotIn("role=", self.batch_delegate)

    def test_batch_builds_one_substantive_packet_and_preserves_legacy_single_flow(self):
        self.assertIn("one frozen common brief exactly once", self.batch)
        self.assertIn("explicitly allowed target contents and bounded read-only command results", self.batch)
        self.assertIn("make the brief substantive", self.batch)
        self.assertIn("Context Intelligence harvest exactly once", self.batch)
        self.assertIn("all source-work and CI-only restrictions", self.batch)
        self.assertIn("capture access remains limited to the caller and source", self.batch)
        single = " ".join(
            self.skill.split("## Delegate exactly one reviewer", 1)[1]
            .split("## Multiple reviewers", 1)[0]
            .split()
        )
        self.assertIn("context_depth='all'", single)
        self.assertIn("Inspect only the explicit target files", single)
        self.assertIn(
            "ask for a different selector",
            " ".join(self.skill.split()),
        )

    def test_batch_fanout_and_reported_metadata_preserve_member_attribution(self):
        self.assertIn("at most the effective concurrency active at once", self.batch)
        self.assertIn("parallel delegation calls and no per-provider throttle", self.batch)
        self.assertIn("Reviewers never receive another reviewer's response", self.batch)
        self.assertIn("Preserve successful returns when other rows fail", self.batch)
        self.assertIn("streaming is unavailable", self.batch)
        self.assertIn("delegation-reported routing preferences", self.batch)
        self.assertIn("available LLM-call count", self.batch)
        self.assertIn("separately identifiable by resolver index", self.report)
        self.assertIn("attributed agreement, unique findings, and disagreements", self.report)
        self.assertIn("agreement is not majority truth", self.report)


if __name__ == "__main__":
    unittest.main()