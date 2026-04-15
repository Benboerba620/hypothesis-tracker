#!/usr/bin/env bash
# Hypothesis Tracker Install Script (Unix/macOS/Linux)
# Usage: bash scripts/install.sh --target-dir ./hypothesis-tracker [--force]

set -euo pipefail

TARGET_DIR="./hypothesis-tracker"
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target-dir) TARGET_DIR="$2"; shift 2 ;;
        --force) FORCE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

copy_if_needed() {
    local source="$1"
    local destination="$2"
    if [[ ! -e "$destination" || "$FORCE" == true ]]; then
        cp "$source" "$destination"
    fi
}

echo "=== Hypothesis Tracker Installer ==="
echo "Target directory: $TARGET_DIR"

# --- Check Python ---
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo ""
    echo "ERROR: Python not found. Please install Python >= 3.10:"
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "Then re-run this installer."
    exit 1
fi

PYTHON_VERSION="$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
PYTHON_OK="$($PYTHON_CMD -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)")"
if [[ "$PYTHON_OK" != "1" ]]; then
    echo ""
    echo "ERROR: Python version too old (current: $PYTHON_VERSION, required: >= 3.10)"
    echo "  https://www.python.org/downloads/"
    exit 1
fi
echo "OK Python $PYTHON_VERSION"

# --- Check target directory ---
if [[ -e "$TARGET_DIR" && ! -d "$TARGET_DIR" ]]; then
    echo "ERROR: $TARGET_DIR already exists and is not a directory."
    exit 1
fi

if [[ -d "$TARGET_DIR" ]]; then
    echo "Target directory already exists. Installing into existing workspace."
fi

# --- Create directory structure ---
mkdir -p \
    "$TARGET_DIR/config" \
    "$TARGET_DIR/scripts" \
    "$TARGET_DIR/templates" \
    "$TARGET_DIR/examples" \
    "$TARGET_DIR/hypothesis" \
    "$TARGET_DIR/portfolio/journal" \
    "$TARGET_DIR/.claude/skills"

# --- Copy script files ---
for s in check_setup.py workspace_paths.py sync_hypothesis.py trade_stats.py; do
    cp "$REPO_DIR/scripts/$s" "$TARGET_DIR/scripts/"
done

# --- Copy templates ---
for t in hypothesis-tracker-hypothesis-template.md hypothesis-tracker-journal-template.md hypothesis-tracker-report-template.md; do
    cp "$REPO_DIR/templates/$t" "$TARGET_DIR/templates/"
done

# --- Copy skills ---
for s in hypothesis-tracker-trade.md hypothesis-tracker-status.md hypothesis-tracker-new.md; do
    cp "$REPO_DIR/skills/$s" "$TARGET_DIR/.claude/skills/"
done

# --- Copy examples ---
cp "$REPO_DIR/examples/H1-example-thesis.md" "$TARGET_DIR/examples/"
cp "$REPO_DIR/examples/hypothesis-tracker.base" "$TARGET_DIR/examples/"

# --- Copy config files (working copies only, no .example duplicates) ---
copy_if_needed "$REPO_DIR/config/hypothesis-tracker.env.example" "$TARGET_DIR/config/hypothesis-tracker.env"
copy_if_needed "$REPO_DIR/config/hypothesis-tracker.example.yaml" "$TARGET_DIR/config/hypothesis-tracker.yaml"
copy_if_needed "$REPO_DIR/config/hypothesis-tracker.rules.example.md" "$TARGET_DIR/config/hypothesis-tracker-rules.md"

# --- Initialize CSV files ---
if [[ ! -f "$TARGET_DIR/portfolio/trades.csv" ]]; then
    echo "date,ticker,market,action,shares,price,currency,reasoning,kill_thesis,outcome_note" > "$TARGET_DIR/portfolio/trades.csv"
fi

if [[ ! -f "$TARGET_DIR/portfolio/holdings.csv" ]]; then
    echo "ticker,market,name,shares,avg_cost,currency,date_opened,hypothesis,stop_loss,status" > "$TARGET_DIR/portfolio/holdings.csv"
fi

# --- CLAUDE.md integration ---
PROTOCOL_HEADING="## Hypothesis Tracker"

if [[ ! -f "$TARGET_DIR/CLAUDE.md" ]]; then
    cat > "$TARGET_DIR/CLAUDE.md" <<'EOF'
# Workspace Instructions

## Hypothesis Tracker

For hypothesis tracking, prefer /ht-trade, /ht-status, and /ht-new.

Read these first:
- ./.claude/skills/hypothesis-tracker-trade.md
- ./.claude/skills/hypothesis-tracker-status.md
- ./.claude/skills/hypothesis-tracker-new.md
- ./config/hypothesis-tracker.yaml
- ./config/hypothesis-tracker-rules.md

Hypotheses live in ./hypothesis/H*.md.
Trades are recorded in ./portfolio/trades.csv.
EOF
elif ! grep -Fq "$PROTOCOL_HEADING" "$TARGET_DIR/CLAUDE.md"; then
    cat >> "$TARGET_DIR/CLAUDE.md" <<'EOF'

## Hypothesis Tracker

For hypothesis tracking, prefer /ht-trade, /ht-status, and /ht-new.

Read these first:
- ./.claude/skills/hypothesis-tracker-trade.md
- ./.claude/skills/hypothesis-tracker-status.md
- ./.claude/skills/hypothesis-tracker-new.md
- ./config/hypothesis-tracker.yaml
- ./config/hypothesis-tracker-rules.md

Hypotheses live in ./hypothesis/H*.md.
Trades are recorded in ./portfolio/trades.csv.
EOF
fi

# --- Install Python dependencies ---
echo ""
echo "Installing Python dependencies..."
if $PYTHON_CMD -m pip install -r "$REPO_DIR/requirements.txt" --quiet; then
    echo "OK Python dependencies installed"
else
    echo ""
    echo "WARNING: Dependency install failed. Please run manually:"
    echo "  $PYTHON_CMD -m pip install -r requirements.txt"
    echo ""
fi

# --- Run setup check ---
echo ""
echo "Running setup check..."
if $PYTHON_CMD "$TARGET_DIR/scripts/check_setup.py"; then
    echo ""
    echo "OK Installation complete! All checks passed."
else
    echo ""
    echo "WARNING: Installation complete, but setup check found issues."
    echo ""
fi

echo ""
echo "Installed to $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. Review config:       $TARGET_DIR/config/hypothesis-tracker.yaml"
echo "  2. Review rules:        $TARGET_DIR/config/hypothesis-tracker-rules.md"
echo "  3. Read the example:    $TARGET_DIR/examples/H1-example-thesis.md"
echo "  4. Create a hypothesis: Run /ht-new in Claude Code"
echo "  5. Record a trade:      Run /ht-trade in Claude Code"
