#!/usr/bin/env python3
"""
Convert Claude Code plugins to Qwen Code extensions.

This script:
1. Generates qwen-extension.json for each plugin (from .claude-plugin/plugin.json)
2. Updates model references in agent .md files (opus->qwen-max, sonnet->qwen-plus, haiku->qwen-flash)
3. Creates a summary report of all conversions

Usage:
    python tools/convert-to-qwen.py
    python tools/convert-to-qwen.py --dry-run       # Preview changes without writing
    python tools/convert-to-qwen.py --restore        # Restore original model references
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

MODEL_MAPPING = {
    "opus": "qwen-max",
    "sonnet": "qwen-plus",
    "haiku": "qwen-flash",
    "inherit": "inherit",
}

REVERSE_MODEL_MAPPING = {v: k for k, v in MODEL_MAPPING.items()}

# ── Helpers ────────────────────────────────────────────────────────────────────

def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: Path, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ── Step 1: Generate qwen-extension.json ───────────────────────────────────────

def generate_extension_json(plugin_dir: Path, dry_run: bool = False) -> dict | None:
    """Convert .claude-plugin/plugin.json -> qwen-extension.json"""
    claude_json = plugin_dir / ".claude-plugin" / "plugin.json"

    if not claude_json.exists():
        return None

    data = read_json(claude_json)

    # Detect which subdirectories exist
    has_agents = (plugin_dir / "agents").is_dir()
    has_commands = (plugin_dir / "commands").is_dir()
    has_skills = (plugin_dir / "skills").is_dir()

    qwen_ext = {
        "name": data.get("name", plugin_dir.name),
        "version": data.get("version", "1.0.0"),
        "description": data.get("description", ""),
    }

    # Only include directories that exist
    if has_agents:
        qwen_ext["agents"] = "agents"
    if has_commands:
        qwen_ext["commands"] = "commands"
    if has_skills:
        qwen_ext["skills"] = "skills"

    out_path = plugin_dir / "qwen-extension.json"

    if not dry_run:
        write_json(out_path, qwen_ext)

    return {
        "plugin": data.get("name", plugin_dir.name),
        "path": str(out_path.relative_to(REPO_ROOT)),
        "agents": has_agents,
        "commands": has_commands,
        "skills": has_skills,
    }


# ── Step 2: Update model references in agent files ────────────────────────────

MODEL_LINE_RE = re.compile(r"^(model:\s*)([\w-]+)(\s*)$", re.MULTILINE)


def update_agent_models(plugin_dir: Path, dry_run: bool = False, restore: bool = False) -> list[dict]:
    """Update model: lines in agent .md files."""
    agents_dir = plugin_dir / "agents"
    if not agents_dir.is_dir():
        return []

    changes = []
    mapping = REVERSE_MODEL_MAPPING if restore else MODEL_MAPPING

    for md_file in sorted(agents_dir.glob("*.md")):
        content = read_text(md_file)
        original = content

        def replace_model(match):
            prefix = match.group(1)
            model_name = match.group(2)
            suffix = match.group(3)
            new_model = mapping.get(model_name, model_name)
            return f"{prefix}{new_model}{suffix}"

        new_content = MODEL_LINE_RE.sub(replace_model, content)

        if new_content != original:
            # Extract old and new model from regex match
            old_match = MODEL_LINE_RE.search(original)
            old_model = old_match.group(2) if old_match else "unknown"
            new_model = mapping.get(old_model, old_model)

            if not dry_run:
                write_text(md_file, new_content)

            changes.append({
                "file": str(md_file.relative_to(REPO_ROOT)),
                "old_model": old_model,
                "new_model": new_model,
            })

    return changes


# ── Step 3: Generate QWEN.md for each plugin ──────────────────────────────────

def generate_qwen_md(plugin_dir: Path, dry_run: bool = False) -> bool:
    """Generate a QWEN.md context file for the plugin."""
    qwen_md_path = plugin_dir / "QWEN.md"

    # Skip if already exists
    if qwen_md_path.exists():
        return False

    # Read plugin info
    claude_json = plugin_dir / ".claude-plugin" / "plugin.json"
    if claude_json.exists():
        data = read_json(claude_json)
    else:
        data = {"name": plugin_dir.name, "description": ""}

    name = data.get("name", plugin_dir.name)
    description = data.get("description", "")

    # Count components
    agents_dir = plugin_dir / "agents"
    commands_dir = plugin_dir / "commands"
    skills_dir = plugin_dir / "skills"

    agent_files = sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []
    command_files = sorted(commands_dir.glob("*.md")) if commands_dir.is_dir() else []
    skill_dirs = sorted(skills_dir.iterdir()) if skills_dir.is_dir() else []
    skill_dirs = [d for d in skill_dirs if d.is_dir() and (d / "SKILL.md").exists()]

    content = f"""# {name}

{description}

## Components

"""
    if agent_files:
        content += "### Agents\n\n"
        for af in agent_files:
            agent_name = af.stem
            content += f"- **{agent_name}**: See `agents/{af.name}`\n"
        content += "\n"

    if command_files:
        content += "### Commands\n\n"
        for cf in command_files:
            cmd_name = cf.stem
            content += f"- **/{name}:{cmd_name}**: See `commands/{cf.name}`\n"
        content += "\n"

    if skill_dirs:
        content += "### Skills\n\n"
        for sd in skill_dirs:
            content += f"- **{sd.name}**: See `skills/{sd.name}/SKILL.md`\n"
        content += "\n"

    content += """## Usage

This extension is designed for Qwen Code. Install it with:

```
qwen extensions install <path-to-this-directory>
```

Or copy to `~/.qwen/extensions/` for global availability.
"""

    if not dry_run:
        write_text(qwen_md_path, content)

    return True


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Convert Claude plugins to Qwen Code extensions")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--restore", action="store_true", help="Restore original Claude model references")
    parser.add_argument("--skip-models", action="store_true", help="Skip model reference updates")
    parser.add_argument("--skip-extensions", action="store_true", help="Skip qwen-extension.json generation")
    parser.add_argument("--skip-qwen-md", action="store_true", help="Skip QWEN.md generation")
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("  DRY RUN - No files will be modified")
        print("=" * 60)

    if args.restore:
        print("=" * 60)
        print("  RESTORE MODE - Reverting to Claude model names")
        print("=" * 60)

    print(f"\nRepository root: {REPO_ROOT}")
    print(f"Plugins directory: {PLUGINS_DIR}\n")

    # Collect all plugin directories
    plugin_dirs = sorted([d for d in PLUGINS_DIR.iterdir() if d.is_dir()])
    print(f"Found {len(plugin_dirs)} plugin directories\n")

    # ── Step 1: Generate qwen-extension.json ──
    ext_results = []
    if not args.skip_extensions and not args.restore:
        print("-" * 60)
        print("Step 1: Generating qwen-extension.json files")
        print("-" * 60)

        for plugin_dir in plugin_dirs:
            result = generate_extension_json(plugin_dir, dry_run=args.dry_run)
            if result:
                ext_results.append(result)
                status = "WOULD CREATE" if args.dry_run else "CREATED"
                print(f"  [{status}] {result['path']}")

        print(f"\n  Total: {len(ext_results)} extension files\n")

    # ── Step 2: Update model references ──
    all_model_changes = []
    if not args.skip_models:
        print("-" * 60)
        action = "Restoring Claude model references" if args.restore else "Step 2: Updating model references"
        print(action)
        print("-" * 60)

        for plugin_dir in plugin_dirs:
            changes = update_agent_models(plugin_dir, dry_run=args.dry_run, restore=args.restore)
            all_model_changes.extend(changes)
            for c in changes:
                status = "WOULD UPDATE" if args.dry_run else "UPDATED"
                print(f"  [{status}] {c['file']}: {c['old_model']} -> {c['new_model']}")

        print(f"\n  Total: {len(all_model_changes)} agent files updated\n")

    # ── Step 3: Generate QWEN.md ──
    qwen_md_count = 0
    if not args.skip_qwen_md and not args.restore:
        print("-" * 60)
        print("Step 3: Generating QWEN.md context files")
        print("-" * 60)

        for plugin_dir in plugin_dirs:
            created = generate_qwen_md(plugin_dir, dry_run=args.dry_run)
            if created:
                qwen_md_count += 1
                status = "WOULD CREATE" if args.dry_run else "CREATED"
                print(f"  [{status}] {plugin_dir.name}/QWEN.md")

        print(f"\n  Total: {qwen_md_count} QWEN.md files\n")

    # ── Summary Report ──
    print("=" * 60)
    print("  CONVERSION SUMMARY")
    print("=" * 60)
    print(f"  Plugins processed:        {len(plugin_dirs)}")
    print(f"  Extension JSONs created:  {len(ext_results)}")
    print(f"  Agent models updated:     {len(all_model_changes)}")
    print(f"  QWEN.md files created:    {qwen_md_count}")
    print()

    if all_model_changes:
        # Count by model transition
        transitions = {}
        for c in all_model_changes:
            key = f"{c['old_model']} -> {c['new_model']}"
            transitions[key] = transitions.get(key, 0) + 1
        print("  Model transitions:")
        for k, v in sorted(transitions.items()):
            print(f"    {k}: {v} files")

    print()
    if args.dry_run:
        print("  This was a DRY RUN. Run without --dry-run to apply changes.")
    elif args.restore:
        print("  Model references restored to Claude originals.")
    else:
        print("  Conversion complete! Next steps:")
        print("  1. Install Qwen Code: npm install -g @anthropic-ai/qwen-code")
        print("  2. Run: python tools/install-qwen-extensions.py")
        print("  3. Start Qwen Code: qwen")
        print("  4. Try: /skills or /agents manage")


if __name__ == "__main__":
    main()
