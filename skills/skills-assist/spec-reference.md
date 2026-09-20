# Agent Skills Spec Reference

Use this reference for the portable file format and Amplifier's loader. The
[Agent Skills specification](https://agentskills.io/specification) defines the
format; it does not guarantee another client's execution behavior. Checked
against the specification and this repository on 2026-09-20. Recheck the runtime
when changing versions or hosts.

## Standard Fields

`SKILL.md` contains YAML frontmatter followed by Markdown instructions.

| Field | Requirement | Type and constraints |
|-------|-------------|----------------------|
| `name` | Required | String, 1–64 characters; lowercase alphanumeric characters and single hyphens; no leading/trailing hyphen; matches its directory. ASCII names are the safest cross-client choice. |
| `description` | Required | Nonempty string, at most 1024 characters; purpose and selection conditions. |
| `license` | Optional | String naming a license or bundled terms. |
| `compatibility` | Optional | String, 1–500 characters, describing environment requirements. |
| `metadata` | Optional | String-to-string mapping; quote version numbers and other values YAML might interpret differently. |
| `allowed-tools` | Optional, experimental | Space-separated string of tool identifiers. Interpretation and support depend on the client. |

Top-level `version` and `hooks` are **not** standard fields. For a portable version,
use `metadata.version: "1.0.0"`. Amplifier accepts additional fields; that does not
establish support in other clients or strict validators. The specification does
not require a license field, but distribution rights still need verification.

Amplifier discovery is lenient: it warns on several naming/length problems and
can still load the skill. Loading therefore does not prove standard conformance.
It also accepts a YAML list for `allowed-tools`; use a string for the portable
format. See [`discovery.py`](../../modules/tool-skills/amplifier_module_tool_skills/discovery.py).

## Amplifier Frontmatter and Runtime Behavior

These are implementation details, not additions to the open standard. Other
clients may use the same field names with different defaults or semantics.

| Field | Default | Current Amplifier behavior |
|-------|---------|----------------------------|
| `context: fork` | Inline | Requests a child through `session.spawn`. Parent conversation is excluded by default; callers can request inheritance through `context_depth`, `context_scope`, and `context_turns`. |
| `agent` | Unset | Model-selection archetype hint, such as `Explore`, `Plan`, `Code`, or `Review`. Does **not** select a named agent bundle; the fork spawns `agent_name="self"`. |
| `model_role` | Unset | Semantic role resolved by the mounted `model_role_resolver`. A list is accepted, but the current resolver uses only its first element. |
| `provider_preferences` | Unset | Explicit provider/model preferences passed to the child session. |
| `model` | Unset | Model-name hint translated to a semantic role, not a guarantee of selecting that named model. |
| `disable-model-invocation` | `false` | Moves the skill into the visibility hook's user-invoked category. Does not prevent a model call, auto-delegate, inject the body at startup, or enforce a prohibition on `load_skill`. |
| `user-invocable` | `false` | Includes the skill in the discovery capability's command catalog. The app implements dispatch and menus. |
| `shortcut` | Unset | Additional command alias, normalized to lowercase. |
| `argument-hint` | Unset | Display-only argument hint; optional completion data uses the `amplifier.completions` sidecar convention. |
| `hooks` | Unset | Configuration forwarded in skill lifecycle events; execution requires a relevant hook module. |
| `auto-load` | `false` | With nonempty `hooks`, emits `skill:loaded` at mount and tracks cleanup. Does not automatically inject every skill body into the system prompt. |
| `version` | Unset | Legacy informational value exposed in info/lifecycle events. Prefer `metadata.version` for portable authoring. |

Use actual YAML booleans. Quoted `"false"` is a string, and the current parser can
treat a nonempty string as true.

### Loading and child sessions

`load_skill(skill_name="name", arguments="request")` returns an inline body and
`skill_directory`, or executes a fork and returns its response. Pass arguments
explicitly for forks; omitted input is not recovered from parent history unless
context inheritance was requested.

Without `session.spawn`, the current loader warns and returns a fork body inline,
without fork preprocessing. Treat this as an unmet capability when isolation is
required. A forked skill cannot invoke another forked skill; inline skills remain
loadable.

Companion paths resolve from `skill_directory`, not the working directory.
Loading an entrypoint does not read every resource or install packages. The
visibility hook advertises metadata within a configurable budget; listing or
searching can expose omitted skills. Verify discovery and activation separately.

Implementation: [`__init__.py`](../../modules/tool-skills/amplifier_module_tool_skills/__init__.py),
[`hooks.py`](../../modules/tool-skills/amplifier_module_tool_skills/hooks.py), and
[`context_inheritance.py`](../../modules/tool-skills/amplifier_module_tool_skills/context_inheritance.py).

### `allowed-tools` in Amplifier

For a fork, `allowed-tools` becomes the spawner's `inherit_tools`. It matches
Amplifier **module IDs**, such as `tool-filesystem`, `tool-search`, `tool-bash`,
`tool-delegate`, and `tool-skills`. It does not match callable names like
`read_file` or another client's expression such as `Bash(git:*)`.

A nonempty list with no matching modules leaves no inherited tools. Omitting the
field inherits the parent tool surface. An empty string/list is also treated as
omitted; it does not deny all tools. Inline skills do not restrict the parent's
tools. This field is not a process or filesystem sandbox. Validate the mounted
child tool set in the destination host.

## Preprocessing and Argument Substitution

[`preprocessing.py`](../../modules/tool-skills/amplifier_module_tool_skills/preprocessing.py)
replaces `${SKILL_DIR}`, processes enabled/trusted shell expressions, and then
substitutes user arguments.

| Expression | Current Amplifier interpretation |
|------------|----------------------------------|
| `$ARGUMENTS` | Entire `arguments` string; empty when omitted. |
| `$0`, `$1`, … | Zero-based whitespace-separated words: `$0` is first. Missing positions become empty strings. Quotes do not group words. |
| `${SKILL_DIR}` | Skill directory supplied by the loader. |

```markdown
Review file: $0
Focus: $1
Full request: $ARGUMENTS

If no file was supplied, ask for the file before proceeding.
Read ${SKILL_DIR}/references/review.md for the review procedure.
```

These expressions are client extensions. A portable body can instead refer to
the user's request and use a relative Markdown link to `references/review.md`.

### Shell expressions

The expression `` !`command` `` is preprocessing, not portable Markdown execution.
Inline loads use `execute_shell=False`, leaving expressions literal. Forks execute
expressions when the source passes the trust check. Remote URLs configured in
`skills` or registered with `load_skill(source=...)` retain their origin after
cache resolution and receive a blocked marker. Explicit `trusted=False` metadata
also blocks execution. Local paths and bundle namespace sources retain the
existing composition trust behavior; they are not classified as remote URLs.
Do not claim universal isolation for every source form. Prefer explicit,
authorized tool execution when host approval matters.

Commands run through the platform shell in the skill directory with a 30-second
timeout. An environment allowlist includes the caller's **existing PATH**, not a
fixed set of system directories. On POSIX it also includes HOME, TMPDIR, LANG,
TERM, USER, SHELL, and LC_ALL; Windows has an essential-variable set. Filtering
is not a sandbox and does not prevent filesystem access.

Successful nonempty stdout is wrapped in `<shell-output>` and truncated at the
output limit (currently approximately 1 MiB). Failures/timeouts become inline
error markers and do not automatically fail the skill. Do not place user input
inside preprocessing commands or mistake an error marker for completed work.

## Model Selection Precedence

[`model_resolver.py`](../../modules/tool-skills/amplifier_module_tool_skills/model_resolver.py)
implements this skill-level chain:

1. `provider_preferences` — passed to the spawner.
2. `model_role` — resolved through the mounted role resolver.
3. `model` — hint mapping, such as `haiku` → `fast`, `sonnet` → `coding`,
   `opus` → `reasoning`.
4. `agent` — archetype mapping: `Explore` → `fast`, `Plan` → `reasoning`,
   `Code` → `coding`, `Review` → `critique`.
5. No preference — inherit the parent's provider configuration.

Unknown hints map to `general`. A role without a mounted resolver falls back to
the parent provider. Available roles and actual models depend on the bundle and
host; there is no universal fixed role catalog. Prefer capability-oriented roles
for shared Amplifier skills, then verify the resolved model in a real session.

## Format Validation and Runtime Validation

Use short entrypoints and load resources as needed. A format checker such as
`skills-ref validate ./my-skill` catches structural problems, but does not prove
dependencies, adapters, permissions, model behavior, or artifact quality.

Use [testing-guide.md](testing-guide.md) for session tests and
[compatibility-matrix.md](compatibility-matrix.md) for portability. Keep format,
discovery, activation, execution, and user-visible results as separate evidence.
