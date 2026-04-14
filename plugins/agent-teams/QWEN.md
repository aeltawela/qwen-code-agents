# agent-teams

Orchestrate multi-agent teams for parallel code review, hypothesis-driven debugging, and coordinated feature development using Claude Code's Agent Teams

## Components

### Agents

- **team-debugger**: See `agents/team-debugger.md`
- **team-implementer**: See `agents/team-implementer.md`
- **team-lead**: See `agents/team-lead.md`
- **team-reviewer**: See `agents/team-reviewer.md`

### Commands

- **/agent-teams:team-debug**: See `commands/team-debug.md`
- **/agent-teams:team-delegate**: See `commands/team-delegate.md`
- **/agent-teams:team-feature**: See `commands/team-feature.md`
- **/agent-teams:team-review**: See `commands/team-review.md`
- **/agent-teams:team-shutdown**: See `commands/team-shutdown.md`
- **/agent-teams:team-spawn**: See `commands/team-spawn.md`
- **/agent-teams:team-status**: See `commands/team-status.md`

### Skills

- **multi-reviewer-patterns**: See `skills/multi-reviewer-patterns/SKILL.md`
- **parallel-debugging**: See `skills/parallel-debugging/SKILL.md`
- **parallel-feature-development**: See `skills/parallel-feature-development/SKILL.md`
- **task-coordination-strategies**: See `skills/task-coordination-strategies/SKILL.md`
- **team-communication-protocols**: See `skills/team-communication-protocols/SKILL.md`
- **team-composition-patterns**: See `skills/team-composition-patterns/SKILL.md`

## Usage

This extension is designed for Qwen Code. Install it with:

```
qwen extensions install <path-to-this-directory>
```

Or copy to `~/.qwen/extensions/` for global availability.
