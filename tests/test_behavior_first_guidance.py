"""Behavior-first documentation and deterministic council scaffold tests."""

import re
from pathlib import Path

import yaml


REPO = Path(__file__).parents[1]
README = (REPO / "README.md").read_text(encoding="utf-8")
BUNDLE = (REPO / "bundle.md").read_text(encoding="utf-8")
COUNCIL_SKILL = (REPO / "skills" / "councilify" / "SKILL.md").read_text(encoding="utf-8")
ORCHESTRATOR_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "council-orchestrator.SKILL.md.tmpl"
).read_text(encoding="utf-8")
ROOT_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "bundle.md.tmpl"
).read_text(encoding="utf-8")
BEHAVIOR_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "behavior.yaml.tmpl"
).read_text(encoding="utf-8")
HERE_ORCHESTRATOR_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "council-here-orchestrator.SKILL.md.tmpl"
).read_text(encoding="utf-8")
NATIVE_LENS_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "council-native-lens.SKILL.md.tmpl"
).read_text(encoding="utf-8")
AWARENESS_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "awareness.md.tmpl"
).read_text(encoding="utf-8")
MODULE_README = (REPO / "modules" / "tool-skills" / "README.md").read_text(
    encoding="utf-8"
)

SKILLS_BEHAVIOR_URI = (
    "git+https://github.com/microsoft/amplifier-bundle-skills@main"
    "#subdirectory=behaviors/skills.yaml"
)
ANCHORS_URI = (
    "git+https://github.com/microsoft/amplifier-foundation@main"
    "#subdirectory=bundles/anchors/bundle.md"
)
COUNCIL_FIXTURE = {
    "{{DOMAIN}}": "product",
    "{{DOMAIN_TITLE}}": "Product",
    "{{LENS_COUNT}}": "5",
    "{{REUSED_LENS_BEHAVIOR_INCLUDES}}": "",
}
ROOT_ARTIFACT = Path("bundle.md")
BEHAVIOR_ARTIFACT = Path("behaviors/product-council-behavior.yaml")
LEGACY_ROOT_INCLUDES = [
    {"bundle": "git+https://github.com/microsoft/amplifier-foundation@main"},
    {"bundle": "skills:behaviors/skills"},
]
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
HTML_COMMENT = re.compile(r"<!--.*?-->\s*", re.DOTALL)
FIXTURE_DOMAIN = "architecture"
FIXTURE_TITLE = "Architecture"
FIXTURE_README_FIELDS = {
    "{{BEHAVIOR_URI}}": (
        "git+https://github.com/example-org/amplifier-bundle-architecture-council@main"
        "#subdirectory=behaviors/architecture-council-behavior.yaml"
    )
}
FIXTURE_LENSES = {
    "purpose": {
        "title": "Purpose Keeper",
        "question": "Does this architecture serve the stated outcome without adding machinery that does not earn its keep?",
        "grounding": "the architecture decision record's stated outcome",
        "territory": "it tests whether every structural choice serves that outcome",
        "tone": "outcome-led, plain-spoken, intolerant of ornamental complexity",
        "disallowed": "treating implementation feasibility as the primary question (that is feasibility's lens)",
        "style": "Name the outcome, then identify the component that does or does not serve it.",
        "behaviors": (
            ("Trace choices to outcomes", "Connect each major component to a stated user or business outcome."),
            ("Challenge ornamental structure", "Flag abstractions that have no named consumer or outcome."),
            ("Protect the decision boundary", "Keep a useful constraint when removing it would defeat the stated purpose."),
        ),
        "siblings": (
            ("coherence", "Coherence owns internal consistency; purpose owns whether the consistent design is worth building."),
            ("feasibility", "Feasibility owns delivery risk; purpose owns outcome fit."),
        ),
        "example_verdict": "CONCERN",
        "example_finding": "The event bus has no consumer tied to the stated deployment outcome, so its added operating cost is not yet justified.",
    },
    "coherence": {
        "title": "Coherence Guardian",
        "question": "Do the architecture's boundaries, data flow, and operational assumptions tell one consistent story?",
        "grounding": "the architecture decision record's stated boundaries and data flow",
        "territory": "it tests whether the parts agree instead of merely looking plausible in isolation",
        "tone": "systematic, connective, alert to seams",
        "disallowed": "ranking business outcomes (that is purpose's lens)",
        "style": "Follow one flow end to end and name the first boundary where the stated model stops agreeing with itself.",
        "behaviors": (
            ("Trace end-to-end flows", "Follow control and data paths across each stated boundary."),
            ("Compare assumptions", "Surface incompatible consistency, ownership, or failure assumptions."),
            ("Name seam failures", "Turn a vague mismatch into a concrete boundary and consequence."),
        ),
        "siblings": (
            ("purpose", "Purpose owns outcome fit; coherence owns agreement among the chosen parts."),
            ("feasibility", "Feasibility owns delivery constraints; coherence owns whether the design model is internally consistent."),
        ),
        "example_verdict": "CONCERN",
        "example_finding": "The API claims synchronous confirmation while the persistence path is asynchronous, so the stated success semantics disagree across the boundary.",
    },
    "feasibility": {
        "title": "Feasibility Examiner",
        "question": "Can this architecture be delivered, operated, and recovered within the stated constraints?",
        "grounding": "the architecture decision record's delivery and operating constraints",
        "territory": "it tests the practical path from design to reliable operation",
        "tone": "concrete, risk-aware, unsentimental about operational cost",
        "disallowed": "redefining the desired outcome (that is purpose's lens)",
        "style": "Name the prerequisite, operating burden, or recovery path that makes a claimed capability credible or not.",
        "behaviors": (
            ("Test delivery prerequisites", "Identify dependencies, staffing, and migration work required before rollout."),
            ("Price operational burden", "Make monitoring, incident response, and maintenance obligations explicit."),
            ("Exercise recovery", "Ask how the system returns to a safe state after its named failure modes."),
        ),
        "siblings": (
            ("purpose", "Purpose owns what outcome matters; feasibility owns whether the route to it is viable."),
            ("coherence", "Coherence owns internal consistency; feasibility owns delivery and operational constraints."),
        ),
        "example_verdict": "CONCERN",
        "example_finding": "The rollback plan depends on dual writes, but no reconciliation procedure is specified for a partially completed migration.",
    },
}


def render_template(template: str, fields: dict[str, str]) -> str:
    """Render a template with its explicit fixture fields only."""
    return _render_explicit_fields(_without_html_author_comments(template), fields)


def frontmatter(text: str) -> dict:
    _, yaml_text, _ = text.split("---", 2)
    parsed = yaml.safe_load(yaml_text)
    assert isinstance(parsed, dict)
    return parsed


def section(text: str, start: str, end: str) -> str:
    """Return the text between two known documentation headings."""
    return text.split(start, 1)[1].split(end, 1)[0]


def fenced_blocks(text: str, language: str) -> list[str]:
    """Return fenced blocks of one language without their fence markers."""
    return re.findall(rf"```{language}\n(.*?)```", text, re.DOTALL)


def includes_fragment(block: str) -> list[str]:
    """Parse a documented includes-list fragment as YAML."""
    parsed = yaml.safe_load(f"includes:\n{block}")
    assert isinstance(parsed, dict)
    return [entry["bundle"] for entry in parsed["includes"]]


def _replace_once(text: str, old: str, new: str) -> str:
    """Replace one known template fragment, rejecting stale or duplicated source."""
    assert text.count(old) == 1, f"expected exactly one template fragment: {old!r}"
    return text.replace(old, new, 1)


def _without_html_author_comments(template: str) -> str:
    """Remove source-template author instructions before producing an artifact."""
    rendered = HTML_COMMENT.sub("", template)
    assert "<!--" not in rendered
    assert "-->" not in rendered
    return rendered


def _render_explicit_fields(template: str, fields: dict[str, str]) -> str:
    """Render only explicitly mapped fields and reject missing or stale mappings."""
    placeholders = set(PLACEHOLDER.findall(template))
    missing = placeholders - fields.keys()
    unused = fields.keys() - placeholders
    assert not missing, f"missing fixture values for: {sorted(missing)}"
    assert not unused, f"fixture values do not occur in template: {sorted(unused)}"
    rendered = template
    for placeholder in placeholders:
        rendered = rendered.replace(placeholder, fields[placeholder])
    assert "{{" not in rendered
    assert "}}" not in rendered
    return rendered


def _fixture_roster() -> dict[str, str]:
    """Return the shared bench and location note for both council entry points."""
    return {
        "bench": """**The bench is exactly 3 native lenses — all are mandatory.**

- **purpose** — "Does this architecture serve the stated outcome without adding machinery that does not earn its keep?"
- **coherence** — "Do the architecture's boundaries, data flow, and operational assumptions tell one consistent story?"
- **feasibility** — "Can this architecture be delivered, operated, and recovered within the stated constraints?"

Record all three as included in the roster manifest.""",
        "locations": (
            "> **Where each lens lives.** `purpose`, `coherence`, and `feasibility` "
            "are skills in **this** bundle (load by name). All bench lenses are native "
            "to this bundle; no reused-lens dependency is required."
        ),
    }


def _normalized_roster_section(text: str) -> str:
    """Return the rendered shared bench and location note with normalized whitespace."""
    start = text.index("**The bench is exactly")
    end = text.index("required.", start) + len("required.")
    return " ".join(text[start:end].split())


def _product_root_fields() -> dict[str, str]:
    return {
        "{{DOMAIN}}": COUNCIL_FIXTURE["{{DOMAIN}}"],
        "{{DOMAIN_TITLE}}": COUNCIL_FIXTURE["{{DOMAIN_TITLE}}"],
        "{{LENS_COUNT}}": COUNCIL_FIXTURE["{{LENS_COUNT}}"],
    }


def _product_behavior_fields() -> dict[str, str]:
    return {
        **_product_root_fields(),
        "{{REUSED_LENS_BEHAVIOR_INCLUDES}}": COUNCIL_FIXTURE[
            "{{REUSED_LENS_BEHAVIOR_INCLUDES}}"
        ],
    }


def render_fixture_council_orchestrator() -> str:
    """Render the forked orchestrator template for the fixed native-lens bench."""
    template = _without_html_author_comments(ORCHESTRATOR_TEMPLATE)
    roster = _fixture_roster()
    roster_start = "**Mandatory core**"
    prefix, remainder = template.split(roster_start, 1)
    _, suffix = remainder.split("\n---\n\n## Phase 2:", 1)
    template = f"{prefix}{roster['bench']}\n\n{roster['locations']}\n\n---\n\n## Phase 2:{suffix}"

    phase_two_start = "## Phase 2: Existing-{{TARGET_NOUN}} Handling"
    phase_three_start = "## Phase 3: Round 1 — Cold, Independent Fan-Out"
    prefix, remainder = template.split(phase_two_start, 1)
    _, suffix = remainder.split(phase_three_start, 1)
    template = f"{prefix}## Phase 2: Round 1 — Cold, Independent Fan-Out{suffix}"
    template = _replace_once(
        template,
        "review <target> (plus the {{PREDIGEST_ARTIFACT_NAME}}\nif provided) AS THAT PERSONA",
        "review <target> AS THAT PERSONA",
    )
    template = _replace_once(template, "## Phase 4: Debate-to-Consensus Loop", "## Phase 3: Debate-to-Consensus Loop")
    template = _replace_once(template, "skip to Phase 5 (synthesis)", "skip to Phase 4 (synthesis)")
    template = _replace_once(template, "## Phase 5: Synthesize", "## Phase 4: Synthesize")

    return _render_explicit_fields(
        template,
        {
            "{{DOMAIN}}": FIXTURE_DOMAIN,
            "{{DOMAIN_TITLE}}": FIXTURE_TITLE,
            "{{LENS_COUNT}}": "3",
            "{{TARGET_CLASS_DESCRIPTION}}": (
                "An architecture decision record, proposal, or design document is a real external target"
            ),
            "{{TARGET_EXAMPLES}}": (
                "- an architecture decision record\n"
                "- a service-boundary proposal\n"
                "- a system design document"
            ),
            "{{USAGE_EXAMPLES}}": (
                "  /architecture-council docs/architecture-decision.md\n"
                "  /architecture-council \"Review the proposed event pipeline\""
            ),
            "{{lens-a}}": "purpose",
            "{{lens-b}}": "coherence",
            "{{lens}}": "a lens",
            "{{reused\nlens}}": "reused lens",
            "{{owning bundle}}": "owning bundle",
        },
    )


def render_fixture_council_here_orchestrator() -> str:
    """Render the inline counterpart template for the fixed native-lens bench."""
    template = _without_html_author_comments(HERE_ORCHESTRATOR_TEMPLATE)
    roster = _fixture_roster()
    roster_placeholder = (
        "{{ROSTER_SHAPE_BLOCK — must be byte-identical in substance to the roster in\n"
        "{{DOMAIN}}-council/SKILL.md's Phase 1, including the \"where each lens lives\"\n"
        "note and any REUSED_LENSES_NOTE.}}"
    )
    template = _replace_once(
        template,
        roster_placeholder,
        f"{roster['bench']}\n\n{roster['locations']}",
    )
    return _render_explicit_fields(
        template,
        {
            "{{DOMAIN}}": FIXTURE_DOMAIN,
            "{{DOMAIN_TITLE}}": FIXTURE_TITLE,
            "{{LENS_COUNT}}": "3",
            "{{example focus}}": "the service-boundary tradeoff",
            "{{ARTIFACT_NOUN}}": "architecture decision",
        },
    )


def render_fixture_native_lens(lens_name: str) -> str:
    """Render the lens body with a fixture-supplied discovery description.

    Description-budget checks cover this concrete fixture, not every possible
    completion of the template's free-form description guidance.
    """
    lens = FIXTURE_LENSES[lens_name]
    template = _without_html_author_comments(NATIVE_LENS_TEMPLATE)
    description_start = "description: |\n"
    description_end = "user-invocable: true"
    prefix, remainder = template.split(description_start, 1)
    _, suffix = remainder.split(description_end, 1)
    description = (
        f"description: >-\n"
        f"  Use for architecture checkpoints to assess: {lens['question']} "
        f"USE WHEN reviewing an architecture proposal before commitment. "
        f"DO NOT USE for a general implementation review; use the architecture council.\n"
    )
    template = f"{prefix}{description}{description_end}{suffix}"
    template = _replace_once(
        template,
        "{{explicit collapse-guard — name the SIBLING lens whose\n"
        'job this is NOT, e.g. "treating X as the problem (that is {{sibling}}\'s lens,\n'
        'not yours)"}}',
        lens["disallowed"],
    )
    template = _replace_once(
        template,
        "- **{{sibling-lens-1}}** — {{one line: what sibling owns vs what this lens\n"
        "  owns, and where they productively pull apart}}\n"
        "- **{{sibling-lens-2}}** — {{...}}",
        f"- **{lens['siblings'][0][0]}** — {lens['siblings'][0][1]}\n"
        f"- **{lens['siblings'][1][0]}** — {lens['siblings'][1][1]}",
    )

    fields = {
        "{{lens-name}}": lens_name,
        "{{SHORT}}": lens_name[:4],
        "{{Lens Title}}": lens["title"],
        "{{one-line role}}": f"{lens['title'].lower()} for architecture decisions",
        "{{disallowed role 1}}": "general solution designer",
        "{{disallowed role 2}}": "implementation planner",
        "{{load-bearing\nquestion}}": lens["question"],
        "{{The exact one-line load-bearing question}}": lens["question"],
        "{{One or two sentences establishing what you refuse to be\nimpressed or distracted by, and what a competent-but-wrong answer looks like\non your axis.}}": (
            "Do not be impressed by a fashionable pattern that cannot answer this question. "
            "A competent-but-wrong answer may be internally polished while failing this axis."
        ),
        "{{named framework/archetype/corpus}}": lens["grounding"],
        "{{one line on what\nthat grounding actually establishes as this lens's territory}}": lens["territory"],
        "{{Optional grounding read: a companion doc path, if one exists.}}": (
            "This representative fixture is designed-not-mined; its grounding is the stated decision record."
        ),
        "{{2-4 adjectives/phrases specific to this lens's posture}}": lens["tone"],
        "{{concrete style guidance — what a finding looks like in this\nlens's mouth}}": lens["style"],
        "{{Behavior name}}": lens["behaviors"][0][0],
        "{{What this behavior does and why. Anchor in a verbatim quote if mined from a\nreal corpus; otherwise a sharply concrete illustrative line.}}": lens["behaviors"][0][1],
        "{{what fully satisfies this lens's question}}": "The decision names specific evidence that answers the question.",
        "{{partially satisfies it; specific, nameable, fixable gaps}}": "The decision has evidence but leaves a named, fixable gap.",
        "{{what a genuine failure on this axis looks like}}": "The decision contradicts the question or supplies no credible evidence.",
        "{{a sibling's axis}}": "a sibling's axis",
        "{{this lens's own axis}}": "this lens's question",
        "{{PASS|CONCERN|FAIL}}": lens["example_verdict"],
        "{{One concrete, specific example finding in this lens's voice,\nciting the exact evidence it points at.}}": lens["example_finding"],
    }
    template = _replace_once(
        template,
        "### 2. {{Behavior name}}\n{{...}}\n\n### 3. {{Behavior name}}\n{{...}}",
        f"### 2. {lens['behaviors'][1][0]}\n{lens['behaviors'][1][1]}\n\n"
        f"### 3. {lens['behaviors'][2][0]}\n{lens['behaviors'][2][1]}",
    )
    return _render_explicit_fields(template, fields)


def render_fixture_root() -> str:
    """Render the actual supporting-root template for the fixed bench."""
    template = _without_html_author_comments(ROOT_TEMPLATE)
    return _render_explicit_fields(
        template,
        {
            "{{DOMAIN}}": FIXTURE_DOMAIN,
            "{{DOMAIN_TITLE}}": FIXTURE_TITLE,
            "{{LENS_COUNT}}": "3",
        },
    )


def render_fixture_behavior() -> str:
    """Render the actual behavior template with no reused-lens dependency."""
    template = _without_html_author_comments(BEHAVIOR_TEMPLATE)
    return _render_explicit_fields(
        template,
        {
            "{{DOMAIN}}": FIXTURE_DOMAIN,
            "{{DOMAIN_TITLE}}": FIXTURE_TITLE,
            "{{LENS_COUNT}}": "3",
            "{{REUSED_LENS_BEHAVIOR_INCLUDES}}": "",
        },
    )


def render_fixture_awareness() -> str:
    """Render the actual thin-awareness template for the fixed bench."""
    template = _without_html_author_comments(AWARENESS_TEMPLATE)
    return _render_explicit_fields(
        template,
        {
            "{{DOMAIN}}": FIXTURE_DOMAIN,
            "{{DOMAIN_TITLE}}": FIXTURE_TITLE,
            "{{one-line description of the kind of decision/artifact under review}}": (
                "an architecture proposal affects several interacting concerns"
            ),
            "{{a natural framing\nof the whole-council question}}": (
                "does this architecture serve its outcome, cohere internally, and remain feasible to operate?"
            ),
            "{{condition 1 — a \"done but want orthogonal perspective before X\" case}}": (
                "a proposal is ready for a commitment decision and needs independent review"
            ),
            "{{condition 2 — a \"reviewers keep circling the same surface issue\" case}}": (
                "reviewers disagree about a boundary, flow, or operational assumption"
            ),
            "{{condition 3 — a \"you suspect it's competent but missing Y\" case}}": (
                "the design is plausible but its outcome, coherence, or feasibility evidence is incomplete"
            ),
            "{{name 1-2 concrete tension pairs, e.g. \"outcome vs. scope,\nstakeholder-buy-in vs. delivery-risk\"}}": "outcome fit vs. operating burden",
            "{{one line per adjacent council, naming\nexactly what each owns instead — e.g. \"the engineering council (code/\narchitecture quality), design-council (visual/UX dimensions),\nadversarial-review (operational risk)\"}}": (
                "implementation review (code-level correctness) and design-council (visual and interaction quality)"
            ),
        },
    )


def render_fixture_readme() -> str:
    """Render a behavior-first README with an illustrative install URI."""
    return _render_explicit_fields(
        """# Architecture Council

## Install into an existing Amplifier host

```bash
amplifier bundle add {{BEHAVIOR_URI}} --app
```
""",
        FIXTURE_README_FIELDS,
    )


def write_representative_council_fixture(output_dir: Path | str) -> dict[Path, str]:
    """Write a deterministic scaffold for local loading tests.

    Usage from this repository:
      PYTHONPATH=tests python -c "from test_behavior_first_guidance import \
write_representative_council_fixture; write_representative_council_fixture('./test-output/architecture-council')"
    """
    root = Path(output_dir)
    artifacts = {
        Path("bundle.md"): render_fixture_root(),
        Path("README.md"): render_fixture_readme(),
        Path("behaviors/architecture-council-behavior.yaml"): render_fixture_behavior(),
        Path("context/architecture-council-awareness.md"): render_fixture_awareness(),
        Path("skills/architecture-council/SKILL.md"): render_fixture_council_orchestrator(),
        Path("skills/architecture-council-here/SKILL.md"): render_fixture_council_here_orchestrator(),
    }
    artifacts.update(
        {
            Path(f"skills/{lens_name}/SKILL.md"): render_fixture_native_lens(lens_name)
            for lens_name in FIXTURE_LENSES
        }
    )
    for relative_path, content in artifacts.items():
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return artifacts


def test_skills_docs_lead_with_the_behavior_and_keep_the_legacy_root_supporting():
    quick_start = README.split("## Quick Start", 1)[1].split("### Add your own", 1)[0]
    assert f"amplifier bundle add {SKILLS_BEHAVIOR_URI} --app" in quick_start
    assert quick_start.index(SKILLS_BEHAVIOR_URI) < quick_start.index(
        "Supporting legacy root"
    )
    legacy_root = frontmatter(BUNDLE)
    assert legacy_root["bundle"]["name"] == "skills"
    assert legacy_root["includes"] == LEGACY_ROOT_INCLUDES
    assert BUNDLE.split("---", 2)[2].strip() == (
        "@foundation:context/shared/common-system-base.md"
    )
    assert "@skills:context/skills-instructions.md" not in BUNDLE


def test_rendered_council_supporting_root_composes_anchors_and_own_behavior():
    rendered = render_template(ROOT_TEMPLATE, _product_root_fields())
    parsed = frontmatter(rendered)
    includes = [entry["bundle"] for entry in parsed["includes"]]
    assert includes == [
        ANCHORS_URI,
        "product-council:behaviors/product-council-behavior",
    ]
    assert parsed["bundle"]["name"] == "product-council"
    assert rendered.split("---", 2)[2].strip() == "@anchors:context/system.md"
    assert ROOT_ARTIFACT == Path("bundle.md")
    behavior_reference = includes[1]
    assert Path(behavior_reference.split(":", 1)[1]).with_suffix(".yaml") == (
        BEHAVIOR_ARTIFACT
    )
    assert "Always emit the flat-layout supporting root `bundle.md`" in COUNCIL_SKILL
    assert "`behaviors/<domain>-council-behavior.yaml`" in COUNCIL_SKILL
    assert "This namespace-only registration does not compose or select the root" in (
        COUNCIL_SKILL
    )


def test_rendered_council_behavior_keeps_portable_skill_dependency_in_behavior():
    rendered = render_template(BEHAVIOR_TEMPLATE, _product_behavior_fields())
    parsed = yaml.safe_load(rendered)
    tool = parsed["tools"][0]
    assert parsed["bundle"]["name"] == "product-council-behavior"
    assert parsed["bundle"]["name"] != "product-council"
    assert [entry["bundle"] for entry in parsed["includes"]] == [SKILLS_BEHAVIOR_URI]
    assert tool["module"] == "tool-skills"
    assert tool["config"]["skills"] == ["@product-council:skills"]
    assert "amplifier-bundle-skills@main#subdirectory=modules/tool-skills" in tool["source"]
    assert "context" in parsed and parsed["context"]["include"] == [
        "product-council:context/product-council-awareness.md"
    ]
    assert "#subdirectory=bundles/anchors" not in "\n".join(
        entry["bundle"] for entry in parsed["includes"]
    )
    assert "Write the human overview, lens descriptions, grounding, and division of labor" in (
        COUNCIL_SKILL
    )
    assert "to the generated `README.md`" in COUNCIL_SKILL
    assert "anchors:git-ops" in COUNCIL_SKILL
    assert "foundation:git-ops" not in COUNCIL_SKILL


def test_council_digest_uses_the_explorer_the_supporting_root_supplies():
    root = render_template(ROOT_TEMPLATE, _product_root_fields())
    root_includes = [entry["bundle"] for entry in frontmatter(root)["includes"]]

    assert root_includes[0] == ANCHORS_URI
    assert "`anchors:explorer`" in ORCHESTRATOR_TEMPLATE
    assert "foundation:explorer" not in ORCHESTRATOR_TEMPLATE
    assert re.search(
        r"only an explorer advertised in that host's\s+delegation agent catalog",
        ORCHESTRATOR_TEMPLATE,
    )
    assert "perform no writes or other effectful actions" in ORCHESTRATOR_TEMPLATE
    for template in (ORCHESTRATOR_TEMPLATE, ROOT_TEMPLATE, BEHAVIOR_TEMPLATE):
        assert "Ground truth: amplifier-bundle-design-council" not in template


def test_module_readme_existing_host_examples_are_parseable_includes_fragments():
    installation = section(
        MODULE_README,
        "### Recommended: Add the Behavior to an Existing Host",
        "### Supporting legacy root",
    )
    usage = section(MODULE_README, "### Usage in Bundles", "### Agent Workflow Example")

    for documented_section in (installation, usage):
        fragments = fenced_blocks(documented_section, "yaml")
        assert fragments
        for fragment in fragments:
            assert "---" not in fragment
            assert "bundle:\n" not in fragment
            assert includes_fragment(fragment) == [SKILLS_BEHAVIOR_URI]


def test_module_readme_quick_start_installs_into_the_existing_app():
    quick_start = section(MODULE_README, "## Quick Start", "### New complete host")

    assert f"amplifier bundle add {SKILLS_BEHAVIOR_URI} --app" in quick_start
    assert 'amplifier run "What skills are available?"' in quick_start
    assert "amplifier bundle use your-bundle.md" not in quick_start


def test_complete_host_examples_compose_anchors_or_are_intentional_legacy():
    complete_host_examples = [
        frontmatter(block)
        for block in fenced_blocks(MODULE_README, "yaml")
        if block.startswith("---") and "bundle:\n" in block
    ]
    complete_host_examples.append(
        frontmatter(render_template(ROOT_TEMPLATE, _product_root_fields()))
    )
    deployed_legacy_root = frontmatter(BUNDLE)

    assert complete_host_examples
    for example in complete_host_examples:
        includes = [entry["bundle"] for entry in example["includes"]]
        assert ANCHORS_URI in includes

    assert deployed_legacy_root["bundle"]["name"] == "skills"
    assert deployed_legacy_root["includes"] == LEGACY_ROOT_INCLUDES
    assert ANCHORS_URI not in [entry["bundle"] for entry in deployed_legacy_root["includes"]]


def test_representative_council_fixture_renders_all_actual_templates(tmp_path: Path):
    artifacts = write_representative_council_fixture(tmp_path)

    assert set(artifacts) == {
        Path("bundle.md"),
        Path("README.md"),
        Path("behaviors/architecture-council-behavior.yaml"),
        Path("context/architecture-council-awareness.md"),
        Path("skills/architecture-council/SKILL.md"),
        Path("skills/architecture-council-here/SKILL.md"),
        Path("skills/purpose/SKILL.md"),
        Path("skills/coherence/SKILL.md"),
        Path("skills/feasibility/SKILL.md"),
    }
    for relative_path, expected_content in artifacts.items():
        rendered = (tmp_path / relative_path).read_text(encoding="utf-8")
        assert rendered == expected_content
        assert "{{" not in rendered
        assert "}}" not in rendered
        assert "<!--" not in rendered
        assert "-->" not in rendered

    root = frontmatter(artifacts[Path("bundle.md")])
    assert root["bundle"]["name"] == "architecture-council"
    assert [entry["bundle"] for entry in root["includes"]] == [
        ANCHORS_URI,
        "architecture-council:behaviors/architecture-council-behavior",
    ]

    behavior = yaml.safe_load(
        artifacts[Path("behaviors/architecture-council-behavior.yaml")]
    )
    assert behavior["bundle"]["name"] == "architecture-council-behavior"
    assert [entry["bundle"] for entry in behavior["includes"]] == [SKILLS_BEHAVIOR_URI]
    assert behavior["tools"][0]["config"]["skills"] == ["@architecture-council:skills"]
    assert behavior["context"]["include"] == [
        "architecture-council:context/architecture-council-awareness.md"
    ]
    assert "example/reused" not in artifacts[
        Path("behaviors/architecture-council-behavior.yaml")
    ]

    assert (
        "amplifier bundle add "
        f"{FIXTURE_README_FIELDS['{{BEHAVIOR_URI}}']} --app"
    ) in artifacts[Path("README.md")]
    assert "/architecture-council <target>" in artifacts[
        Path("context/architecture-council-awareness.md")
    ]

    forked = frontmatter(artifacts[Path("skills/architecture-council/SKILL.md")])
    inline = frontmatter(
        artifacts[Path("skills/architecture-council-here/SKILL.md")]
    )
    assert forked["name"] == "architecture-council"
    assert forked["context"] == "fork"
    assert forked["user-invocable"] is True
    assert forked["model_role"] == "critique"
    assert inline["name"] == "architecture-council-here"
    assert "context" not in inline
    assert inline["user-invocable"] is True
    assert inline["model_role"] == "critique"
    assert _normalized_roster_section(artifacts[Path("skills/architecture-council/SKILL.md")]) == (
        _normalized_roster_section(
            artifacts[Path("skills/architecture-council-here/SKILL.md")]
        )
    )
    for skill in (forked, inline):
        assert len(skill["description"]) <= 400
        assert "<example>" not in skill["description"]
        assert "<commentary>" not in skill["description"]

    for lens_name in FIXTURE_LENSES:
        skill = frontmatter(artifacts[Path(f"skills/{lens_name}/SKILL.md")])
        description = skill["description"]
        assert skill["name"] == lens_name
        assert skill["user-invocable"] is True
        assert skill["model_role"] == "critique"
        assert len(description) <= 400
        assert "<example>" not in description
        assert "<commentary>" not in description