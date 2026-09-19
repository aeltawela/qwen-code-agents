#!/usr/bin/env python3
"""
Install converted plugins as Qwen Code extensions.

This script copies/symlinks plugins into Qwen Code's extension directory:
  - Windows: %USERPROFILE%\\.qwen\\extensions\\
  - macOS/Linux: ~/.qwen/extensions/

Usage:
    python3 tools/install-qwen-extensions.py                  # Install all plugins
    python3 tools/install-qwen-extensions.py --plugins python-development backend-development
    python3 tools/install-qwen-extensions.py --list            # List available plugins
    python3 tools/install-qwen-extensions.py --uninstall       # Remove all installed extensions
    python3 tools/install-qwen-extensions.py --symlink         # Legacy symlink mode
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"

def get_qwen_extensions_dir() -> Path:
    """Get the Qwen Code extensions directory for the current OS."""
    if sys.platform == "win32":
        home = Path(os.environ.get("USERPROFILE", Path.home()))
    else:
        home = Path.home()

    ext_dir = home / ".qwen" / "extensions"
    return ext_dir


def get_available_plugins() -> list[dict]:
    """List all plugins that have been converted (have qwen-extension.json)."""
    plugins = []
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir():
            continue
        ext_json = plugin_dir / "qwen-extension.json"
        if ext_json.exists():
            with open(ext_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            plugins.append({
                "name": data.get("name", plugin_dir.name),
                "version": data.get("version", "1.0.0"),
                "description": data.get("description", ""),
                "path": plugin_dir,
                "has_agents": (plugin_dir / "agents").is_dir(),
                "has_commands": (plugin_dir / "commands").is_dir(),
                "has_skills": (plugin_dir / "skills").is_dir(),
            })
    return plugins


def install_plugin(plugin: dict, ext_dir: Path, use_symlink: bool = False) -> bool:
    """Install a single plugin as a Qwen Code extension."""
    target = ext_dir / plugin["name"]
    source = plugin["path"]

    # Remove existing installation
    if target.exists() or target.is_symlink():
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)

    if use_symlink:
        # Create symlink (requires admin on Windows)
        try:
            target.symlink_to(source, target_is_directory=True)
            return True
        except OSError as e:
            print(f"    WARNING: Symlink failed ({e}). Falling back to copy.")

    # Copy the plugin directory
    # Only copy relevant files, skip .claude-plugin, README.md, etc.
    target.mkdir(parents=True, exist_ok=True)

    # Copy qwen-extension.json
    shutil.copy2(source / "qwen-extension.json", target / "qwen-extension.json")

    # Copy QWEN.md if exists
    qwen_md = source / "QWEN.md"
    if qwen_md.exists():
        shutil.copy2(qwen_md, target / "QWEN.md")

    # Copy agents/ directory
    if (source / "agents").is_dir():
        shutil.copytree(source / "agents", target / "agents", dirs_exist_ok=True)

    # Copy commands/ at the manifest-declared root. Qwen Code handles command
    # conflicts by applying the extension prefix; nesting commands manually
    # prevents the commands from being discovered.
    if (source / "commands").is_dir():
        shutil.copytree(source / "commands", target / "commands", dirs_exist_ok=True)

    # Copy skills/ directory
    if (source / "skills").is_dir():
        shutil.copytree(source / "skills", target / "skills", dirs_exist_ok=True)

    return True


def uninstall_all(ext_dir: Path, plugins: list[dict]):
    """Remove all installed extensions."""
    removed = 0
    for plugin in plugins:
        target = ext_dir / plugin["name"]
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                target.unlink()
            else:
                shutil.rmtree(target)
            print(f"  [REMOVED] {plugin['name']}")
            removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(description="Install Qwen Code extensions")
    parser.add_argument("--plugins", nargs="+", help="Specific plugins to install")
    parser.add_argument("--list", action="store_true", help="List available plugins")
    parser.add_argument("--uninstall", action="store_true", help="Remove all installed extensions")
    parser.add_argument("--symlink", action="store_true", help="Use symlinks instead of copying")
    args = parser.parse_args()

    ext_dir = get_qwen_extensions_dir()
    plugins = get_available_plugins()

    if not plugins:
        print("No converted plugins found. Run 'python3 tools/convert-to-qwen.py' first.")
        sys.exit(1)

    # ── List mode ──
    if args.list:
        print(f"\nAvailable plugins ({len(plugins)}):\n")
        print(f"  {'Name':<40} {'Ver':<8} {'A':>3} {'C':>3} {'S':>3}")
        print(f"  {'─'*40} {'─'*8} {'─'*3} {'─'*3} {'─'*3}")
        for p in plugins:
            a = "✓" if p["has_agents"] else "·"
            c = "✓" if p["has_commands"] else "·"
            s = "✓" if p["has_skills"] else "·"
            print(f"  {p['name']:<40} {p['version']:<8} {a:>3} {c:>3} {s:>3}")
        print(f"\n  A=Agents  C=Commands  S=Skills")
        print(f"\n  Extensions directory: {ext_dir}")
        return

    # ── Uninstall mode ──
    if args.uninstall:
        print(f"\nUninstalling extensions from: {ext_dir}\n")
        removed = uninstall_all(ext_dir, plugins)
        print(f"\n  Removed {removed} extensions.")
        return

    # ── Install mode ──
    # Filter plugins if specific ones requested
    if args.plugins:
        selected = [p for p in plugins if p["name"] in args.plugins]
        not_found = [n for n in args.plugins if n not in [p["name"] for p in plugins]]
        if not_found:
            print(f"WARNING: Plugins not found: {', '.join(not_found)}")
        plugins = selected

    if not plugins:
        print("No plugins to install.")
        return

    # Ensure extensions directory exists
    ext_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nInstalling {len(plugins)} extensions to: {ext_dir}\n")
    method = "symlink" if args.symlink else "copy"
    print(f"  Method: {method}\n")

    installed = 0
    for plugin in plugins:
        success = install_plugin(plugin, ext_dir, use_symlink=args.symlink)
        if success:
            installed += 1
            components = []
            if plugin["has_agents"]:
                components.append("agents")
            if plugin["has_commands"]:
                components.append("commands")
            if plugin["has_skills"]:
                components.append("skills")
            comp_str = ", ".join(components) if components else "context only"
            print(f"  [INSTALLED] {plugin['name']} ({comp_str})")
        else:
            print(f"  [FAILED]    {plugin['name']}")

    print(f"\n  Successfully installed {installed}/{len(plugins)} extensions.")
    print(f"\n  Next steps:")
    print(f"  1. Start Qwen Code: qwen")
    print(f"  2. List skills: /skills")
    print(f"  3. List agents: /agents manage")
    print(f"  4. Try a command: /<command-name> (Qwen prefixes conflicts automatically)")


if __name__ == "__main__":
    main()
