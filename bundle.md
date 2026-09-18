---
bundle:
  name: skills
  version: 1.1.0
  description: Skills tool and Microsoft-curated skills collection for Amplifier agents

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: skills:behaviors/skills
---

# Skills

Provides the [Agent Skills](https://agentskills.io/specification) system for Amplifier agents: the `load_skill` tool, automatic skills visibility, and a curated collection of Microsoft-maintained skills.

## Behaviors

| Behavior | What you get | Use when |
|----------|-------------|----------|
| `skills:behaviors/skills` | Tool + instructions + curated skills | Default -- batteries included |
| `skills:behaviors/skills-tool` | Tool + instructions only | Your bundle brings its own skills |

## Curated Skills

| Skill | Description |
|-------|-------------|
| **image-vision** | LLM-based image analysis across multiple providers (Anthropic, OpenAI, Gemini, Azure) |
| **engineering-patterns** | Thirteen engineering pattern guides behind one catalog entry — CLI packaging, one-line installers, config/state, HTTP services, auth/TLS, file IPC, plugin discovery, instance storage, container orchestration, React microfrontends, MS Graph integration, self-managing tools, Amplifier tool leverage. Each is an L3 reference read on demand. |
| **second-opinion** | Independent, selected-reviewer feedback on current work or a named prior session |

## Use the behavior

For reusable skills capability, compose the full behavior into an existing
host:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-skills@main#subdirectory=behaviors/skills.yaml
```

### Include only the tool (no curated skills)

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-skills@main#subdirectory=behaviors/skills-tool.yaml
```

## Supporting legacy root

This `bundle.md` is a runnable legacy root for users who deliberately select
its Foundation-based session. It composes the behavior above; use the behavior
URI rather than this root when adding skills to another host.

```bash
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-skills@main
amplifier bundle use skills
```

## Add your own skills alongside curated ones

Bundles that include the behavior and also ship their own skills should declare
additional skill sources in their own behavior YAML:

```yaml
tools:
  - module: tool-skills
    source: git+https://github.com/microsoft/amplifier-bundle-skills@main#subdirectory=modules/tool-skills
    config:
      skills:
        - "git+https://github.com/microsoft/amplifier-bundle-skills@main#subdirectory=skills"
        - "git+https://github.com/microsoft/your-bundle@main#subdirectory=skills"
```

`#subdirectory=behaviors/<name>.yaml` is the canonical behavior URI form.
`#subdirectory=modules/tool-skills` and `#subdirectory=skills` select their
respective source directories.

@skills:context/skills-instructions.md

---

@foundation:context/shared/common-system-base.md
