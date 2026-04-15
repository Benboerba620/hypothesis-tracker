"""
Aggregate trade statistics from trades.csv.

Usage:
  python scripts/trade_stats.py
  python scripts/trade_stats.py --hypothesis H1
  python scripts/trade_stats.py --ticker AAPL
  python scripts/trade_stats.py --month 2026-04
  python scripts/trade_stats.py --json
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from workspace_paths import find_workspace_root, resolve_trades_path
except ImportError:
    def find_workspace_root() -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def resolve_trades_path(root: str) -> str:
        return os.path.join(root, "portfolio", "trades.csv")


def load_trades(trades_path: str | None = None) -> list[dict[str, str]]:
    if trades_path is None:
        trades_path = resolve_trades_path(find_workspace_root())
    if not os.path.isfile(trades_path):
        return []
    with open(trades_path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def filter_trades(
    trades: list[dict[str, str]],
    hypothesis: str | None = None,
    ticker: str | None = None,
    month: str | None = None,
) -> list[dict[str, str]]:
    result = trades
    if hypothesis:
        hypothesis_tag = f"[{hypothesis}]"
        result = [
            trade
            for trade in result
            if hypothesis_tag
            in (trade.get("reasoning", "") + trade.get("kill_thesis", ""))
        ]
    if ticker:
        ticker_upper = ticker.upper()
        result = [
            trade for trade in result if trade.get("ticker", "").upper() == ticker_upper
        ]
    if month:
        result = [trade for trade in result if trade.get("date", "").startswith(month)]
    return result


def compute_stats(trades: list[dict[str, str]]) -> dict[str, object]:
    if not trades:
        return {
            "total": 0,
            "buys": 0,
            "sells": 0,
            "adds": 0,
            "reduces": 0,
            "closes": 0,
        }

    action_counts: defaultdict[str, int] = defaultdict(int)
    tickers: set[str] = set()
    for trade in trades:
        action = trade.get("action", "").upper()
        action_counts[action] += 1
        tickers.add(trade.get("ticker", ""))

    return {
        "total": len(trades),
        "buys": action_counts.get("BUY", 0),
        "sells": action_counts.get("SELL", 0),
        "adds": action_counts.get("ADD", 0),
        "reduces": action_counts.get("REDUCE", 0),
        "closes": action_counts.get("CLOSE", 0),
        "unique_tickers": len(tickers),
        "tickers": sorted(tickers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Trade statistics")
    parser.add_argument("--hypothesis", help="Filter by hypothesis tag, e.g. H1")
    parser.add_argument("--ticker", help="Filter by ticker")
    parser.add_argument("--month", help="Filter by month, e.g. 2026-04")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    trades = load_trades()
    filtered = filter_trades(trades, args.hypothesis, args.ticker, args.month)
    stats = compute_stats(filtered)

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    if stats["total"] == 0:
        print("No matching trades found.")
        return 0

    label = ""
    if args.hypothesis:
        label += f" [{args.hypothesis}]"
    if args.ticker:
        label += f" [{args.ticker}]"
    if args.month:
        label += f" [{args.month}]"

    print(f"Trade statistics{label}:\n")
    print(f"  Total trades: {stats['total']}")
    print(
        f"  Buy: {stats['buys']}  Add: {stats['adds']}  "
        f"Sell: {stats['sells']}  Reduce: {stats['reduces']}  "
        f"Close: {stats['closes']}"
    )
    tickers = ", ".join(stats["tickers"])
    print(f"  Tickers: {stats['unique_tickers']} ({tickers})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
