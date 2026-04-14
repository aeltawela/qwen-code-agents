# security-scanning

SAST analysis, dependency vulnerability scanning, OWASP Top 10 compliance, container security scanning, and automated security hardening

## Components

### Agents

- **security-auditor**: See `agents/security-auditor.md`
- **threat-modeling-expert**: See `agents/threat-modeling-expert.md`

### Commands

- **/security-scanning:security-dependencies**: See `commands/security-dependencies.md`
- **/security-scanning:security-hardening**: See `commands/security-hardening.md`
- **/security-scanning:security-sast**: See `commands/security-sast.md`

### Skills

- **attack-tree-construction**: See `skills/attack-tree-construction/SKILL.md`
- **sast-configuration**: See `skills/sast-configuration/SKILL.md`
- **security-requirement-extraction**: See `skills/security-requirement-extraction/SKILL.md`
- **stride-analysis-patterns**: See `skills/stride-analysis-patterns/SKILL.md`
- **threat-mitigation-mapping**: See `skills/threat-mitigation-mapping/SKILL.md`

## Usage

This extension is designed for Qwen Code. Install it with:

```
qwen extensions install <path-to-this-directory>
```

Or copy to `~/.qwen/extensions/` for global availability.
