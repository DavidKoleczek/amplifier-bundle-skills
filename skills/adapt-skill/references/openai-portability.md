# Porting OpenAI Codex and ChatGPT skills

Inspect the installed package rather than assuming the session catalog is complete.
Codex caches can contain `cache/<marketplace>/<plugin>/<version>/skills/<name>`
and core skills can live separately under `.codex/skills/.system`. A plugin may
contain multiple skills. Never choose a cached version by lexicographic order;
use active installation metadata, an explicit version, or a reviewed selection.

Official format references:
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/plugins/concepts/plugins

## Package boundary and provenance

Read `SKILL.md`, linked resources, `agents/openai.yaml`, `plugin.json` and/or
`.codex-plugin/plugin.json`, MCP configuration, and license notices. Inventory
binary template references as well as text. An installed copy is not proof of
redistribution rights. Preserve notices and distinguish local adaptation from
publication; resolve explicit restrictions before copying restricted materials.
If writing an original alternative, label it as such instead of claiming an exact
port. Do not copy credentials, caches, user data, node_modules, or dependency
runtimes into a skills bundle. Reject symlink escapes and report name collisions.

Record every input with source-relative path, plugin/version, file hashes, target
name, retained resources, adaptation decisions, dependency requirements, and
validation evidence. A hash identifies a source; it does not grant a license.

## Mapping decisions

| Source feature | Amplifier treatment |
| --- | --- |
| `name`, `description`, references/scripts/assets | Preserve intent and relative package structure; use unique names and concise routing descriptions. |
| `agents/openai.yaml` interface metadata | Optional provenance; not Amplifier registration. Translate useful descriptions into frontmatter. |
| Sidecar dependency or implicit-invocation policy | Record requirements; map invocation intent to `user-invocable`/`disable-model-invocation`; dependencies must actually be composed or discovered. |
| `$skill`, `plugin://`, `skill://`, catalog aliases | Resolve actual filesystem/resource package, then use `load_skill` and returned `skill_directory`. Do not treat an alias as a portable path. |
| `functions.exec`, `tools.*`, `nodeRepl`, `cua` | Host APIs, not ordinary Node modules. Replace with mounted tools or a supported host adapter; never paste into a shell script. |
| `load_workspace_dependencies`, `/mnt/data`, `/home/oai`, Codex caches | Use documented host runtime setup or a task-local environment with declared dependencies and workspace outputs. |
| `@oai/artifact-tool` | Runtime dependency, not provided by the skill's API docs. Require authorized availability or implement and test a portable library workflow. Preserve formula, fidelity, and visual QA requirements. |
| Artifact telemetry/operation markers | Host instrumentation; remove from portable authoring prerequisites unless the destination implements it. |
| Native Google Docs/Sheets/Slides import | Requires a real authorized connector. Local Office output is a separate deliverable and must not be called a native cloud document. |
| Live Excel/add-in session tools | Require a discovered live-workbook adapter; do not silently fall back to a detached XLSX. |
| OpenAI plugin marketplace/install helpers | Discover the destination's bundle/MCP/Smart Tool management surface. Installing a skill does not install a server or establish an account connection. |
| Inline visualization directives, `window.openai.*`, Tweak, host CSS/CDNs | Implement standalone HTML with local assets and optional destination presentation. Follow its CSP, interaction, persistence, and rendering contracts. |
| File citation/follow-up/template-card directives | Use destination-supported links/artifacts and ordinary suggestions. Do not emit foreign rendering directives. |
| Template manifests and retained files | Keep relative references and preview assets when permitted. Validate fidelity using the applicable authoring skill. A template cannot work from a missing reference. |

Avoid global substitutions: an OpenAI API identifier in a research example or a
tool name in source provenance is not necessarily an executable dependency.
Review instructions, scripts, and transitive references. An adapter paragraph
does not fix a later unconditional call to an unavailable tool.

## Destination contract and tests

Keep the bundle provider-neutral. Use inline skills for interactive artifact work;
`context: fork` loses the parent's interactive workflow. Fork `allowed-tools`
filters **module IDs**, not callable tool names. The current code is authoritative
if a reference disagrees. Do not auto-load the full ported library every turn.

Compose tool-skills using the destination's source policy (branch tracking or an
explicitly requested revision), record the revision tested, and configure a bundle
namespace source such as `@work:skills`. Preserve namespace base paths when the
host resolves the bundle. An unrelated working directory must not break loading.
Publish reusable guidance separately from optional host instructions; do not put
an application dependency in a portable bundle.

Test actual discovery/loading for every target, resource closure, asset hashes,
and representative output creation and rendering. For spreadsheets, distinguish
formula preservation from real recalculation. For HTML, distinguish accepted
publication from browser render evidence. Test missing native connectors and
fallback disclosures. Keep source inventories, package checks, behavioral agent
tests, and host/browser acceptance as separate evidence levels.
