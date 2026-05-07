"""
Price history report — shows a summary of all tracked products.
Usage: python src/report.py
"""

import json
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
HISTORY_FILE = DATA_DIR / "price_history.json"


def print_report():
    if not HISTORY_FILE.exists():
        print("No price history found. Run monitor.py first.")
        return

    with open(HISTORY_FILE) as f:
        history = json.load(f)

    if not history:
        print("History file is empty.")
        return

    by_product = defaultdict(list)
    for record in history:
        by_product[record["product_name"]].append(record)

    print("\n" + "=" * 60)
    print("  PRICE MONITOR — HISTORY REPORT")
    print("=" * 60)

    for name, records in by_product.items():
        prices = [r["price"] for r in records]
        alerts_sent = sum(1 for r in records if r.get("alert_sent"))
        latest = records[-1]

        print(f"\n📦 {name}")
        print(f"   Target price : R$ {latest['target_price']:.2f}")
        print(f"   Latest price : R$ {latest['price']:.2f}  ({latest['checked_at']})")
        print(f"   Highest      : R$ {max(prices):.2f}")
        print(f"   Lowest       : R$ {min(prices):.2f}")
        print(f"   Checks done  : {len(records)}")
        print(f"   Alerts sent  : {alerts_sent}")
        print(f"   URL          : {latest['url'][:60]}...")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    print_report()
