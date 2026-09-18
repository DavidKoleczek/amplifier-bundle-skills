"""Behavior-first documentation and council scaffold regression tests."""

from pathlib import Path

import yaml


REPO = Path(__file__).parents[1]
README = (REPO / "README.md").read_text(encoding="utf-8")
BUNDLE = (REPO / "bundle.md").read_text(encoding="utf-8")
COUNCIL_SKILL = (REPO / "skills" / "councilify" / "SKILL.md").read_text(encoding="utf-8")
ROOT_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "bundle.md.tmpl"
).read_text(encoding="utf-8")
BEHAVIOR_TEMPLATE = (
    REPO / "skills" / "councilify" / "templates" / "behavior.yaml.tmpl"
).read_text(encoding="utf-8")

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
    "{{REUSED_LENS_BEHAVIOR_INCLUDES}}": (
        "  - bundle: git+https://github.com/example/reused-lenses@main"
        "#subdirectory=behaviors/prioritization.yaml\n"
    ),
}
ROOT_ARTIFACT = Path("bundle.md")
BEHAVIOR_ARTIFACT = Path("behaviors/product-council-behavior.yaml")


def render_template(template: str) -> str:
    """Render the fixed fixture used by the parent DTU scaffold/load test."""
    rendered = template.split("-->\n", 1)[1]
    for placeholder, value in COUNCIL_FIXTURE.items():
        rendered = rendered.replace(placeholder, value)
    assert "{{" not in rendered
    return rendered


def frontmatter(text: str) -> dict:
    _, yaml_text, _ = text.split("---", 2)
    parsed = yaml.safe_load(yaml_text)
    assert isinstance(parsed, dict)
    return parsed


def test_skills_docs_lead_with_the_behavior_and_keep_the_legacy_root_supporting():
    quick_start = README.split("## Quick Start", 1)[1].split("### Add your own", 1)[0]
    assert f"amplifier bundle add {SKILLS_BEHAVIOR_URI} --app" in quick_start
    assert quick_start.index(SKILLS_BEHAVIOR_URI) < quick_start.index(
        "Supporting legacy root"
    )
    assert "Supporting legacy root" in BUNDLE
    assert SKILLS_BEHAVIOR_URI in BUNDLE
    assert "#path=" not in BUNDLE


def test_rendered_council_supporting_root_composes_anchors_and_own_behavior():
    rendered = render_template(ROOT_TEMPLATE)
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
    rendered = render_template(BEHAVIOR_TEMPLATE)
    parsed = yaml.safe_load(rendered)
    tool = parsed["tools"][0]
    assert parsed["bundle"]["name"] == "product-council-behavior"
    assert parsed["bundle"]["name"] != "product-council"
    assert [entry["bundle"] for entry in parsed["includes"]] == [
        SKILLS_BEHAVIOR_URI,
        COUNCIL_FIXTURE["{{REUSED_LENS_BEHAVIOR_INCLUDES}}"].strip().removeprefix(
            "- bundle: "
        ),
    ]
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