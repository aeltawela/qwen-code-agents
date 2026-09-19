# Qwen Code Setup Guide

Use this repository's 92 plugins, 202 agents, 183 skills, and 105 commands with **Qwen Code** instead of Claude Code.

## Prerequisites

- [Qwen Code](https://qwenlm.github.io/qwen-code-docs/en/) installed
- Python 3.10+ (for conversion/install scripts)

## Quick Start

### 1. Install Qwen Code

```bash
npm install -g @anthropic-ai/qwen-code
# Verify
qwen --version
```

### 2. Authenticate (Free)

```bash
qwen auth qwen-oauth
```

This gives you **60 requests/minute** and **1,000 requests/day** for free.

Alternatively, use an API key for higher limits:

```bash
qwen auth api-key
# Enter your DashScope API key (sk-xxx)
```

### 3. Convert Plugins (Already Done)

The conversion has already been applied. If you need to re-run:

```bash
# Preview changes
python3 tools/convert-to-qwen.py --dry-run

# Apply conversion
python3 tools/convert-to-qwen.py

# Restore original Claude model references
python3 tools/convert-to-qwen.py --restore
```

### 4. Install Extensions

For a single plugin, use Qwen Code's native installer (recommended):

```bash
qwen extensions install --consent https://github.com/aeltawela/qwen-code-agents:python-development
```

For a local bulk install, use the repository helper:

```bash
# Install ALL 92 plugins
python3 tools/install-qwen-extensions.py

# Or install specific plugins only
python3 tools/install-qwen-extensions.py --plugins python-development backend-development full-stack-orchestration

# List available plugins
python3 tools/install-qwen-extensions.py --list

# Legacy symlink mode (prefer `qwen extensions link` for live local development)
python3 tools/install-qwen-extensions.py --symlink
```

### 5. Start Using

```bash
qwen
```

## Usage Examples

### Slash Commands

```bash
# Python project scaffolding
/python-development:python-scaffold fastapi-microservice

# Full-stack feature development
/full-stack-orchestration:full-stack-feature "user authentication system"

# Security scanning
/security-scanning:security-hardening

# TDD workflow
/tdd-workflows:tdd-red "User can reset password"

# Smart debugging
/debugging-toolkit:smart-debug "memory leak in API handler"

# Generate docs
/code-documentation:doc-generate
```

### Natural Language

```
"Use python-pro to optimize this async code"
"Have security-auditor scan for OWASP vulnerabilities"
"Get deployment-engineer to set up CI/CD"
```

### View Available Resources

```bash
# List all skills
/skills

# Manage agents
/agents manage

# See all commands
/help
```

## Model Mapping

| Original (Claude) | Qwen Equivalent | Use Case |
|---|---|---|
| opus | qwen-max | Critical: architecture, security, code review |
| sonnet | qwen-plus | Complex: multi-step tasks, analysis |
| haiku | qwen-flash | Fast: SEO, deployment, simple docs |
| inherit | inherit | Uses your session's default model |

## What Was Converted

| Component | Count | Changes Made |
|---|---|---|
| `qwen-extension.json` | 92 | Created from `.claude-plugin/plugin.json` |
| Agent model references | 130 | `opus->qwen-max`, `sonnet->qwen-plus`, `haiku->qwen-flash` |
| `QWEN.md` context files | 92 | Generated per-plugin context documents |
| Agent content | 0 | No changes - system prompts are model-agnostic |
| Skill content | 0 | No changes - knowledge packages work as-is |
| Command content | 0 | No changes - workflow definitions are portable |

## File Structure (Per Plugin)

```
plugins/plugin-name/
  qwen-extension.json     <-- NEW (Qwen Code extension manifest)
  QWEN.md                 <-- NEW (context file for Qwen Code)
  .claude-plugin/
    plugin.json            <-- Original (kept for reference)
  agents/
    agent-name.md          <-- Model field updated
  commands/
    command-name.md        <-- No changes
  skills/
    skill-name/
      SKILL.md             <-- No changes
```

## Tools Reference

### convert-to-qwen.py

```bash
python3 tools/convert-to-qwen.py              # Full conversion
python3 tools/convert-to-qwen.py --dry-run    # Preview only
python3 tools/convert-to-qwen.py --restore    # Revert to Claude models
python3 tools/convert-to-qwen.py --skip-models      # Skip model updates
python3 tools/convert-to-qwen.py --skip-extensions   # Skip JSON generation
python3 tools/convert-to-qwen.py --skip-qwen-md      # Skip QWEN.md generation
```

### install-qwen-extensions.py

```bash
python3 tools/install-qwen-extensions.py                # Install all
python3 tools/install-qwen-extensions.py --list         # List plugins
python3 tools/install-qwen-extensions.py --plugins X Y  # Install specific
python3 tools/install-qwen-extensions.py --symlink      # Use symlinks
python3 tools/install-qwen-extensions.py --uninstall    # Remove all
```

## Troubleshooting

### Extensions not appearing

Make sure they're installed in the correct directory:
- **Windows**: `%USERPROFILE%\.qwen\extensions\`
- **macOS/Linux**: `~/.qwen/extensions/`

### Rate limit errors

Switch from OAuth to API key for higher limits:
```bash
qwen auth api-key
```

### Model not available

If `qwen-max` isn't available on your plan, edit the agent files to use `qwen-plus` or `inherit`:
```bash
# Quick fix: change all agents to use inherit (your session's model)
python3 tools/convert-to-qwen.py --restore
# Then manually set all to inherit if needed
```

## Cost Comparison

| Auth Method | Cost | Limits |
|---|---|---|
| Qwen OAuth | Free | 60 req/min, 1,000 req/day |
| API Key (qwen-flash) | ~$0.01/1M tokens | Account limits |
| API Key (qwen-plus) | ~$0.02/1M tokens | Account limits |
| API Key (qwen-max) | ~$0.04/1M tokens | Account limits |
