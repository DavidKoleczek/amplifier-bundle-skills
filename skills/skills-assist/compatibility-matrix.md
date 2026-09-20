# Agent Skills Compatibility Matrix

This matrix separates the portable package format from Amplifier's runtime.
It does not infer another product's support from a shared field name. Checked
against the [specification](https://agentskills.io/specification),
[client guide](https://agentskills.io/client-implementation/adding-skills-support),
and this repository on 2026-09-20. Consult each destination's current official
documentation and test its actual session before promising parity.

## Format and Execution Boundaries

| Feature | Agent Skills format | Current Amplifier behavior | Portability check |
|---------|---------------------|----------------------------|-------------------|
| `name`, `description` | Required | Discovery and visibility | Validate types, lengths, naming, and trigger wording. |
| `license`, `compatibility`, `metadata` | Optional | Parsed; does not install dependencies | Preserve terms; compatibility is a string, metadata values are strings. |
| Top-level `version` | Not standard | Legacy informational metadata | Use `metadata.version`. |
| `allowed-tools` | Experimental string | Fork tool inheritance by **module ID** | Translate identifiers and test enforcement; not a common permission language. |
| Fork/model-selection fields | Client extensions | Spawn and role-resolution contracts | Check capabilities; `agent` is an archetype hint here. |
| `disable-model-invocation` | Client extension | User-invoked visibility category | Does not enforce refusal of model-initiated loading. |
| `user-invocable`, command metadata | Client extensions | Exposed through discovery capability | App must implement dispatch and presentation. |
| `hooks`, `auto-load` | Client extensions | Lifecycle events and optional integration | Check hook module; no universal lifecycle syntax. |
| `$ARGUMENTS`, `$0`, `${SKILL_DIR}` | Client extensions | Loader substitutions | Avoid in portable bodies or adapt and test. |
| Shell preprocessing | Client extension | Disabled inline; trust-gated for forks | Check source provenance and execution policy. |
| Resources/scripts | Package files | Read/run through available tools | Test paths, dependencies, permissions, and output. |

Recognizing `SKILL.md` establishes format compatibility. It does not establish
access to another application's private tools, cloud documents, live workbook
sessions, image service, browser UI, or renderer.

## Discovery in Amplifier

The standard does not prescribe installation paths. The client guide describes
`.agents/skills/` as a sharing convention. Amplifier's current default helper does
not automatically scan that convention.

| Configuration | Behavior |
|---------------|----------|
| Default helper | `AMPLIFIER_SKILLS_DIR`, project `.amplifier/skills/`, then `~/.amplifier/skills/`. |
| Tool configuration `skills` | Ordered local paths, supported Git sources, and `@namespace:path` references; inspect the composed configuration. |
| Namespace sources | Resolve through `mention_resolver`; may defer to the first `provider:request` if the resolver arrives after mounts. |
| Multiple source directories | First discovered name wins; order determines overrides. |
| Runtime overlays | Locally discovered names shadow overlay names. |

To opt into shared directories, configure them in the intended override order:

```yaml
tools:
  - module: tool-skills
    source: git+https://github.com/microsoft/amplifier-bundle-skills@main#subdirectory=modules/tool-skills
    config:
      skills:
        - .amplifier/skills
        - .agents/skills
        - ~/.amplifier/skills
        - ~/.agents/skills
```

Add the bundle's own skill source as appropriate. A client's plugin cache is not
a portable installation root: select actual entrypoints, resolve version/name
collisions, and preserve companion files. The `adapt-skill` inventory records
these decisions.

Symlinks are optional. Amplifier follows them subject to a repository/directory
boundary check. For canonical `skills/` at project root, a sibling link at
`.amplifier/skills` targets `../skills`, not `../../skills`. Confirm the resolved
path remains in the intended repository; avoid cycles. Explicit configured
sources are often simpler.

## Portable Authoring Pattern

Keep task instructions and relative resource links in the portable core. Label
host-specific setup and optional adapters in separate references.

```markdown
---
name: review-summary
description: Summarize supplied review notes and identify unresolved decisions. Use when the user asks to turn a review into a decision summary.
metadata:
  author: example-team
  version: "1.0.0"
---

# Review Summary

Read the user's request and review notes. If the review is missing, ask for it
before making claims about its contents.

Use [the summary structure](references/summary-structure.md).
Distinguish supported decisions from open questions.
```

This example does not require invocation syntax, substitutions, named tools,
a provider, or shell preprocessing. The host still needs a way to read the
reference. Document script dependencies; portable syntax does not remove setup.

For an Amplifier extension, state the dependency. An inline skill uses the live
conversation; a fork needs arguments and spawning support. Do not assume unknown
fields are ignored or that ignoring one preserves the intended behavior.

## Validate the Destination

Use a fresh session in each intended composition, including the actual app host
when relevant. Check selected source/version, deferred discovery, activation,
resources, and representative results. Test available and missing adapters.
Format validation alone does not establish behavior on Claude Code, Codex,
Copilot, or any other client.

The client guide's collision diagnostics, bounded discovery, explicit activation,
resource paths, and retention through context management are useful integration
review points, not claims that this loader or every app already implements them.

See [spec-reference.md](spec-reference.md) for Amplifier semantics and
[testing-guide.md](testing-guide.md) for the acceptance workflow.
