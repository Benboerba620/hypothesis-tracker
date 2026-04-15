"""
安装验证脚本 / Installation Checker
验证 hypothesis-tracker 安装是否完整。
用法：python check_setup.py [--workspace /path/to/workspace]
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from workspace_paths import find_workspace_root
except ImportError:
    def find_workspace_root():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(label, condition, warn=False):
    tag = "[OK]" if condition else ("[WARN]" if warn else "[FAIL]")
    print(f"  {tag} {label}")
    return condition


def check_repo(root):
    """Check that all source files exist in the repo (for CI)."""
    print(f"Hypothesis Tracker 仓库检查 (repo mode)")
    print(f"仓库目录：{root}\n")

    ok = True
    j = lambda *p: os.path.join(root, *p)

    py = sys.version_info
    ok &= check(f"Python {py.major}.{py.minor}.{py.micro}", py >= (3, 10))

    print("\n源文件：")
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
    for f in source_files:
        ok &= check(f, os.path.isfile(j(f)))

    print("\n文档：")
    for f in ["README.md", "LICENSE", "VERSION", "CHANGELOG.md", "CONTRIBUTING.md", "INSTALL-FOR-AI.md"]:
        ok &= check(f, os.path.isfile(j(f)))

    # YAML parse check
    print("\nYAML 验证：")
    yaml_ok = False
    try:
        import yaml
        with open(j("config", "hypothesis-tracker.example.yaml"), "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        yaml_ok = cfg is not None and isinstance(cfg, dict)
    except ImportError:
        print("  [WARN] PyYAML not installed")
    except Exception as e:
        print(f"  [FAIL] YAML parse error: {e}")
    ok &= check("example YAML valid", yaml_ok)

    print(f"\n{'✅ 仓库检查通过' if ok else '❌ 存在问题，请检查上方 [FAIL] 项目'}")
    sys.exit(0 if ok else 1)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=None)
    parser.add_argument("--repo-mode", action="store_true",
                        help="Check repo source files instead of installed workspace")
    args = parser.parse_args()

    root = args.workspace or find_workspace_root()

    if args.repo_mode:
        return check_repo(root)

    print(f"Hypothesis Tracker 安装检查")
    print(f"工作目录：{root}\n")

    ok = True
    j = lambda *p: os.path.join(root, *p)

    # Python version
    py = sys.version_info
    ok &= check(f"Python {py.major}.{py.minor}.{py.micro}", py >= (3, 10))

    # Directories
    print("\n目录结构：")
    for d in ["hypothesis", "portfolio", "portfolio/journal", "config", "scripts", "templates"]:
        ok &= check(d, os.path.isdir(j(d)))

    skills_dir = j(".claude", "skills")
    ok &= check(".claude/skills", os.path.isdir(skills_dir))

    # Config files
    print("\n配置文件：")
    ok &= check("config/hypothesis-tracker.yaml", os.path.isfile(j("config", "hypothesis-tracker.yaml")))
    ok &= check("config/hypothesis-tracker-rules.md", os.path.isfile(j("config", "hypothesis-tracker-rules.md")))

    # Try loading YAML
    yaml_ok = False
    try:
        import yaml
        with open(j("config", "hypothesis-tracker.yaml"), "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        yaml_ok = cfg is not None and isinstance(cfg, dict)
    except ImportError:
        print("  [WARN] PyYAML not installed — run: pip install pyyaml")
    except Exception as e:
        print(f"  [FAIL] YAML parse error: {e}")
    ok &= check("YAML config valid", yaml_ok)

    # Skills
    print("\nSkill 文件：")
    for skill in ["hypothesis-tracker-trade.md", "hypothesis-tracker-status.md", "hypothesis-tracker-new.md"]:
        ok &= check(skill, os.path.isfile(os.path.join(skills_dir, skill)))

    # Templates
    print("\n模板文件：")
    for tmpl in ["hypothesis-tracker-hypothesis-template.md", "hypothesis-tracker-journal-template.md", "hypothesis-tracker-report-template.md"]:
        ok &= check(tmpl, os.path.isfile(j("templates", tmpl)))

    # CSV files
    print("\n数据文件：")
    for csv_file in ["portfolio/trades.csv", "portfolio/holdings.csv"]:
        ok &= check(csv_file, os.path.isfile(j(csv_file)))

    # CLAUDE.md
    print("\nCLAUDE.md：")
    claude_path = j("CLAUDE.md")
    has_claude = os.path.isfile(claude_path)
    check("CLAUDE.md exists", has_claude)
    if has_claude:
        with open(claude_path, "r", encoding="utf-8") as f:
            content = f.read()
        check("contains Hypothesis Tracker section", "Hypothesis Tracker" in content, warn=True)

    # Example
    print("\n示例文件：")
    check("examples/H1-example-thesis.md", os.path.isfile(j("examples", "H1-example-thesis.md")))

    # Obsidian
    print("\nObsidian Bases：")
    obsidian_dir = os.path.join(os.path.dirname(root), ".obsidian")
    if os.path.isdir(obsidian_dir):
        print("  [INFO] Obsidian vault detected. Set obsidian.enabled: true in config to activate dashboard.")
    else:
        print("  [INFO] Obsidian not detected (optional feature)")

    # Summary
    print(f"\n{'✅ 安装完整' if ok else '❌ 存在问题，请检查上方 [FAIL] 项目'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
