"""
交易统计脚本 / Trade Statistics
从 trades.csv 聚合交易统计，支持按假设、标的、月份过滤。
用法：
  python trade_stats.py                        # 全部统计
  python trade_stats.py --hypothesis H1        # 按假设过滤
  python trade_stats.py --ticker AAPL          # 按标的过滤
  python trade_stats.py --month 2026-04        # 按月份过滤
  python trade_stats.py --json                 # JSON 输出
"""
import csv
import os
import sys
import io
import json
import re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from workspace_paths import find_workspace_root, resolve_trades_path
except ImportError:
    def find_workspace_root():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def resolve_trades_path(root):
        return os.path.join(root, "portfolio", "trades.csv")


def load_trades(trades_path=None):
    if trades_path is None:
        trades_path = resolve_trades_path(find_workspace_root())
    if not os.path.isfile(trades_path):
        return []
    with open(trades_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def filter_trades(trades, hypothesis=None, ticker=None, month=None):
    result = trades
    if hypothesis:
        h_tag = f"[{hypothesis}]"
        result = [t for t in result if h_tag in (t.get("reasoning", "") + t.get("kill_thesis", ""))]
    if ticker:
        ticker_upper = ticker.upper()
        result = [t for t in result if t.get("ticker", "").upper() == ticker_upper]
    if month:
        result = [t for t in result if t.get("date", "").startswith(month)]
    return result


def compute_stats(trades):
    if not trades:
        return {"total": 0, "buys": 0, "sells": 0, "adds": 0, "reduces": 0, "closes": 0}

    action_counts = defaultdict(int)
    tickers = set()
    for t in trades:
        action = t.get("action", "").upper()
        action_counts[action] += 1
        tickers.add(t.get("ticker", ""))

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


if __name__ == "__main__":
    import argparse

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
    else:
        if stats["total"] == 0:
            print("无匹配的交易记录。")
        else:
            label = ""
            if args.hypothesis:
                label += f" [{args.hypothesis}]"
            if args.ticker:
                label += f" [{args.ticker}]"
            if args.month:
                label += f" [{args.month}]"
            print(f"交易统计{label}：\n")
            print(f"  总交易数：{stats['total']}")
            print(f"  买入：{stats['buys']}  加仓：{stats['adds']}  卖出：{stats['sells']}  减仓：{stats['reduces']}  平仓：{stats['closes']}")
            print(f"  涉及标的：{stats['unique_tickers']} 个 ({', '.join(stats['tickers'])})")
