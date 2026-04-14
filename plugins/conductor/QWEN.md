# conductor

Context-Driven Development plugin that transforms Claude Code into a project management tool with structured workflow: Context → Spec & Plan → Implement

## Components

### Agents

- **conductor-validator**: See `agents/conductor-validator.md`

### Commands

- **/conductor:implement**: See `commands/implement.md`
- **/conductor:manage**: See `commands/manage.md`
- **/conductor:new-track**: See `commands/new-track.md`
- **/conductor:revert**: See `commands/revert.md`
- **/conductor:setup**: See `commands/setup.md`
- **/conductor:status**: See `commands/status.md`

### Skills

- **context-driven-development**: See `skills/context-driven-development/SKILL.md`
- **track-management**: See `skills/track-management/SKILL.md`
- **workflow-patterns**: See `skills/workflow-patterns/SKILL.md`

## Usage

This extension is designed for Qwen Code. Install it with:

```
qwen extensions install <path-to-this-directory>
```

Or copy to `~/.qwen/extensions/` for global availability.
