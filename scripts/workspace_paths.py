"""
Path resolution for Hypothesis Tracker.
All other scripts import paths from here.
"""
import os
import yaml

CONFIG_DIRNAME = "config"
HYPOTHESIS_DIRNAME = "hypothesis"
PORTFOLIO_DIRNAME = "portfolio"
JOURNAL_DIRNAME = "journal"
SCRIPTS_DIRNAME = "scripts"
TEMPLATES_DIRNAME = "templates"

CONFIG_FILENAME = "hypothesis-tracker.yaml"
ENV_FILENAME = "hypothesis-tracker.env"
RULES_FILENAME = "hypothesis-tracker-rules.md"
TRADES_FILENAME = "trades.csv"
HOLDINGS_FILENAME = "holdings.csv"


def find_workspace_root():
    """Walk up from this script's directory to find the workspace root.
    The workspace root is the directory containing a 'config/' folder
    with a hypothesis-tracker config file.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        candidate = os.path.join(d, CONFIG_DIRNAME, CONFIG_FILENAME)
        if os.path.isfile(candidate):
            return d
        # Also check one level up (scripts/ lives inside workspace)
        parent = os.path.dirname(d)
        candidate = os.path.join(parent, CONFIG_DIRNAME, CONFIG_FILENAME)
        if os.path.isfile(candidate):
            return parent
        d = parent
    # Fallback: parent of scripts/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_path(workspace_root, *parts):
    return os.path.join(workspace_root, *parts)


def resolve_config_path(workspace_root):
    return resolve_path(workspace_root, CONFIG_DIRNAME, CONFIG_FILENAME)


def resolve_rules_path(workspace_root):
    return resolve_path(workspace_root, CONFIG_DIRNAME, RULES_FILENAME)


def resolve_hypothesis_dir(workspace_root):
    return resolve_path(workspace_root, HYPOTHESIS_DIRNAME)


def resolve_trades_path(workspace_root):
    return resolve_path(workspace_root, PORTFOLIO_DIRNAME, TRADES_FILENAME)


def resolve_holdings_path(workspace_root):
    return resolve_path(workspace_root, PORTFOLIO_DIRNAME, HOLDINGS_FILENAME)


def resolve_journal_dir(workspace_root):
    return resolve_path(workspace_root, PORTFOLIO_DIRNAME, JOURNAL_DIRNAME)


def load_config(workspace_root):
    """Load and return the YAML config dict."""
    config_path = resolve_config_path(workspace_root)
    if not os.path.isfile(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
