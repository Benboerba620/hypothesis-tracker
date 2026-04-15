"""
Installation and repository checker for Hypothesis Tracker.

Usage:
  python scripts/check_setup.py
  python scripts/check_setup.py --workspace /path/to/workspace
  python scripts/check_setup.py --repo-mode
"""

from __future__ import annotations

import argparse
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from workspace_paths import find_workspace_root
except ImportError:
    def find_workspace_root() -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(label: str, condition: bool, warn: bool = False) -> bool:
    tag = "[OK]" if condition else ("[WARN]" if warn else "[FAIL]")
    print(f"  {tag} {label}")
    return condition


def joiner(root: str, *parts: str) -> str:
    return os.path.join(root, *parts)


def check_repo(root: str) -> int:
    """Check repository source files for CI."""
    print("Hypothesis Tracker repository check (repo mode)")
    print(f"Repository root: {root}\n")

    ok = True
    py = sys.version_info
    ok &= check(f"Python {py.major}.{py.minor}.{py.micro}", py >= (3, 10))

    print("\nSource files:")
    source_files = [
        "scripts/check_setup.py",
        "scripts/workspace_paths.py",
        "scripts/sync_hypothesis.py",
        "scripts/trade_stats.py",
        "scripts/install.sh",
        "scripts/install.ps1",
        "skills/hypothesis-tracker-trade.md",
        "skills/hypothesis-tracker-status.md",
        "skills/hypothesis-tracker-new.md",
        "templates/hypothesis-tracker-hypothesis-template.md",
        "templates/hypothesis-tracker-journal-template.md",
        "templates/hypothesis-tracker-report-template.md",
        "config/hypothesis-tracker.example.yaml",
        "config/hypothesis-tracker.rules.example.md",
        "config/hypothesis-tracker.env.example",
        "examples/H1-example-thesis.md",
    ]
    for file_path in source_files:
        ok &= check(file_path, os.path.isfile(joiner(root, file_path)))

    print("\nDocs:")
    docs = [
        "README.md",
        "LICENSE",
        "VERSION",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "INSTALL-FOR-AI.md",
    ]
    for file_path in docs:
        ok &= check(file_path, os.path.isfile(joiner(root, file_path)))

    print("\nYAML validation:")
    yaml_ok = False
    try:
        import yaml

        config_path = joiner(root, "config", "hypothesis-tracker.example.yaml")
        with open(config_path, "r", encoding="utf-8") as handle:
            cfg = yaml.safe_load(handle)
        yaml_ok = cfg is not None and isinstance(cfg, dict)
    except ImportError:
        print("  [WARN] PyYAML not installed")
    except Exception as exc:  # pragma: no cover - surfaced in CI/logs
        print(f"  [FAIL] YAML parse error: {exc}")
    ok &= check("example YAML valid", yaml_ok)

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


def check_workspace(root: str) -> int:
    """Check an installed workspace."""
    print("Hypothesis Tracker installation check")
    print(f"Workspace root: {root}\n")

    ok = True
    py = sys.version_info
    ok &= check(f"Python {py.major}.{py.minor}.{py.micro}", py >= (3, 10))

    print("\nDirectory structure:")
    directories = [
        "hypothesis",
        "portfolio",
        "portfolio/journal",
        "config",
        "scripts",
        "templates",
    ]
    for directory in directories:
        ok &= check(directory, os.path.isdir(joiner(root, directory)))

    skills_dir = joiner(root, ".claude", "skills")
    ok &= check(".claude/skills", os.path.isdir(skills_dir))

    print("\nConfig files:")
    ok &= check(
        "config/hypothesis-tracker.yaml",
        os.path.isfile(joiner(root, "config", "hypothesis-tracker.yaml")),
    )
    ok &= check(
        "config/hypothesis-tracker-rules.md",
        os.path.isfile(joiner(root, "config", "hypothesis-tracker-rules.md")),
    )

    yaml_ok = False
    try:
        import yaml

        config_path = joiner(root, "config", "hypothesis-tracker.yaml")
        with open(config_path, "r", encoding="utf-8") as handle:
            cfg = yaml.safe_load(handle)
        yaml_ok = cfg is not None and isinstance(cfg, dict)
    except ImportError:
        print("  [WARN] PyYAML not installed - run: pip install pyyaml")
    except Exception as exc:  # pragma: no cover - surfaced in CI/logs
        print(f"  [FAIL] YAML parse error: {exc}")
    ok &= check("YAML config valid", yaml_ok)

    print("\nSkill files:")
    skills = [
        "hypothesis-tracker-trade.md",
        "hypothesis-tracker-status.md",
        "hypothesis-tracker-new.md",
    ]
    for skill in skills:
        ok &= check(skill, os.path.isfile(os.path.join(skills_dir, skill)))

    print("\nTemplate files:")
    templates = [
        "hypothesis-tracker-hypothesis-template.md",
        "hypothesis-tracker-journal-template.md",
        "hypothesis-tracker-report-template.md",
    ]
    for template in templates:
        ok &= check(template, os.path.isfile(joiner(root, "templates", template)))

    print("\nData files:")
    csv_files = ["portfolio/trades.csv", "portfolio/holdings.csv"]
    for csv_file in csv_files:
        ok &= check(csv_file, os.path.isfile(joiner(root, csv_file)))

    print("\nCLAUDE.md:")
    claude_path = joiner(root, "CLAUDE.md")
    has_claude = os.path.isfile(claude_path)
    check("CLAUDE.md exists", has_claude)
    if has_claude:
        with open(claude_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        check(
            "contains Hypothesis Tracker section",
            "Hypothesis Tracker" in content,
            warn=True,
        )

    print("\nExample file:")
    check(
        "examples/H1-example-thesis.md",
        os.path.isfile(joiner(root, "examples", "H1-example-thesis.md")),
    )

    print("\nObsidian:")
    obsidian_dir = os.path.join(os.path.dirname(root), ".obsidian")
    if os.path.isdir(obsidian_dir):
        print(
            "  [INFO] Obsidian vault detected. "
            "Set obsidian.enabled: true in config to activate dashboard."
        )
    else:
        print("  [INFO] Obsidian not detected (optional feature)")

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=None)
    parser.add_argument(
        "--repo-mode",
        action="store_true",
        help="Check repo source files instead of installed workspace",
    )
    args = parser.parse_args()

    root = args.workspace or find_workspace_root()
    if args.repo_mode:
        return check_repo(root)
    return check_workspace(root)


if __name__ == "__main__":
    raise SystemExit(main())
