---
bundle:
  name: skills
  version: 1.1.0
  description: Skills tool and Microsoft-curated skills collection for Amplifier agents

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: skills:behaviors/skills
---

@foundation:context/shared/common-system-base.md
