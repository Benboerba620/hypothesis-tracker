"""
假设系统扫描脚本 / Hypothesis Scanner
扫描 hypothesis/H*.md，提取确定性 + 状态，输出汇总。
用法：
  python sync_hypothesis.py          # 人类可读表格
  python sync_hypothesis.py --json   # JSON 输出（供 Claude 解析）
"""
import re
import glob
import os
import sys
import io
import json

# Windows UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from workspace_paths import find_workspace_root, resolve_hypothesis_dir
except ImportError:
    # Fallback if run standalone
    def find_workspace_root():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def resolve_hypothesis_dir(root):
        return os.path.join(root, "hypothesis")

# Skip conflict/version artifacts
SKIP_PATTERNS = ("冲突文件", "(版本")


def read_hypothesis_files(hypothesis_dir=None):
    """Scan H*.md files, extract certainty and status."""
    if hypothesis_dir is None:
        hypothesis_dir = resolve_hypothesis_dir(find_workspace_root())

    data = {}
    pattern = os.path.join(hypothesis_dir, "H*.md")
    for f in sorted(glob.glob(pattern)):
        name = os.path.basename(f)
        if any(p in name for p in SKIP_PATTERNS):
            print(f"⚠️  跳过冲突/版本残留：{name}", file=sys.stderr)
            continue
        match_id = re.match(r"H(\d+)", name)
        if not match_id:
            continue
        hid = f"H{match_id.group(1)}"
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()

        # Try YAML frontmatter first
        cert = None
        status_val = None
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            cert_fm = re.search(r"certainty:\s*(\d+)", fm)
            status_fm = re.search(r"status:\s*(.+)", fm)
            if cert_fm:
                cert = int(cert_fm.group(1))
            if status_fm:
                status_val = status_fm.group(1).strip()

        # Fallback: extract from content body
        if cert is None:
            cert_body = re.search(r"当前确定性[：:]\s*(\d+)%", content)
            if cert_body:
                cert = int(cert_body.group(1))
        if status_val is None:
            status_body = re.search(r"状态[：:]\s*(.+)", content)
            if status_body:
                status_val = status_body.group(1).strip()

        # Extract title from heading
        title_match = re.search(r"^#\s+H\d+[：:]\s*(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else name

        data[hid] = {
            "certainty": cert,
            "status": status_val,
            "title": title,
            "file": name,
        }
    return data


def format_certainty_bar(cert):
    if cert is None:
        return "—"
    if cert >= 80:
        return f"🟢 {cert}%"
    if cert >= 50:
        return f"🟡 {cert}%"
    return f"🔴 {cert}%"


if __name__ == "__main__":
    data = read_hypothesis_files()

    if "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"读取 {len(data)} 个假设文件：\n")
        print(f"| ID | 确定性 | 状态 | 文件 |")
        print(f"|-----|--------|------|------|")
        for hid, info in sorted(data.items(), key=lambda kv: int(kv[0][1:])):
            bar = format_certainty_bar(info["certainty"])
            print(f"| {hid} | {bar} | {info['status'] or '—'} | {info['file']} |")
