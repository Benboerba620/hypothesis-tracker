"""
Scan hypothesis markdown files and summarize certainty / status.

Usage:
  python scripts/sync_hypothesis.py
  python scripts/sync_hypothesis.py --json
"""

from __future__ import annotations

import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from workspace_paths import find_workspace_root, resolve_hypothesis_dir
except ImportError:
    def find_workspace_root() -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def resolve_hypothesis_dir(root: str) -> str:
        return os.path.join(root, "hypothesis")


SKIP_PATTERNS = ("冲突文件", "(版本")


def read_hypothesis_files(
    hypothesis_dir: str | None = None,
) -> dict[str, dict[str, object]]:
    """Scan H*.md files and extract certainty/status/title."""
    if hypothesis_dir is None:
        hypothesis_dir = resolve_hypothesis_dir(find_workspace_root())

    data: dict[str, dict[str, object]] = {}
    pattern = os.path.join(hypothesis_dir, "H*.md")
    for file_path in sorted(glob.glob(pattern)):
        name = os.path.basename(file_path)
        if any(pattern_text in name for pattern_text in SKIP_PATTERNS):
            print(f"Skipping conflict/version artifact: {name}", file=sys.stderr)
            continue

        match_id = re.match(r"H(\d+)", name)
        if not match_id:
            continue

        hypothesis_id = f"H{match_id.group(1)}"
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()

        certainty = None
        status_value = None
        frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            certainty_match = re.search(r"certainty:\s*(\d+)", frontmatter)
            status_match = re.search(r"status:\s*(.+)", frontmatter)
            if certainty_match:
                certainty = int(certainty_match.group(1))
            if status_match:
                status_value = status_match.group(1).strip()

        if certainty is None:
            certainty_match = re.search(r"当前确定性[：:]\s*(\d+)%", content)
            if certainty_match:
                certainty = int(certainty_match.group(1))

        if status_value is None:
            status_match = re.search(r"状态[：:]\s*(.+)", content)
            if status_match:
                status_value = status_match.group(1).strip()

        title_match = re.search(r"^#\s+H\d+[：:]\s*(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else name

        data[hypothesis_id] = {
            "certainty": certainty,
            "status": status_value,
            "title": title,
            "file": name,
        }

    return data


def format_certainty_bar(certainty: int | None) -> str:
    if certainty is None:
        return "—"
    if certainty >= 80:
        return f"🟢 {certainty}%"
    if certainty >= 50:
        return f"🟡 {certainty}%"
    return f"🔴 {certainty}%"


def main() -> int:
    data = read_hypothesis_files()

    if "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(f"Read {len(data)} hypothesis files:\n")
    print("| ID | Certainty | Status | File |")
    print("|-----|-----------|--------|------|")
    for hypothesis_id, info in sorted(data.items(), key=lambda item: int(item[0][1:])):
        bar = format_certainty_bar(info["certainty"])
        status_value = info["status"] or "—"
        print(f"| {hypothesis_id} | {bar} | {status_value} | {info['file']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
