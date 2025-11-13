# ==============================
#  PHASE 8B: ALPHA FILTER BRAIN (SQLite Edition)
# ==============================
# This module reads tokens from conviction_memory.db,
# re-analyzes conviction, ranks top plays, and stores to filtered_alpha.json
# for alpha_relay.py to send clean alerts.

import json
import sqlite3
from datetime import datetime

# === Telegram Details (For Reference)
BOT_TOKEN = "7404930359:AAFBMfFIZUZuToI25LszgYcAlgdcYdWCLTo"
CHAT_ID = "6926777491"

DB_PATH = "conviction_memory.db"


# === Load Data from SQLite ===
def load_from_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT chain, ca, symbol, market_cap, performance, detected_at, last_update
            FROM memory
        """)
        rows = cur.fetchall()
        conn.close()

        tokens = []
        for row in rows:
            tokens.append({
                "chain": row[0],
                "ca": row[1],
                "symbol": row[2],
                "market_cap": row[3],
                "performance": row[4],
                "detected_at": row[5],
                "last_update": row[6],
            })
        return tokens
    except Exception as e:
        print(f"❌ DB Load Error: {e}")
        return []


# === Conviction Scoring System ===
def calculate_conviction_score(token):
    base = 40

    # Chain multipliers
    chain_mult = {
        "base": 1.3,
        "sol": 1.2,
        "eth": 1.4,
        "bera": 1.1,
        "blast": 1.05
    }
    base *= chain_mult.get(token.get("chain", "").lower(), 1)

    # Market cap & performance impact
    mc = token.get("market_cap", 0) or 0
    perf = token.get("performance", 0) or 0

    if mc < 500_000:
        base += 5
    elif mc < 2_000_000:
        base += 10
    if perf > 20:
        base += 10
    elif perf > 50:
        base += 20

    # Normalize range
    return int(min(max(base, 10), 100))


# === Main Filter + Rank ===
def filter_and_rank():
    tokens = load_from_db()
    if not tokens:
        print("⚠️ No tokens found in conviction_memory.db")
        return []

    # Score each token
    for t in tokens:
        t["conviction_score"] = calculate_conviction_score(t)

    # Filter + sort
    strong = [t for t in tokens if t["conviction_score"] >= 55]
    ranked = sorted(strong, key=lambda x: x["conviction_score"], reverse=True)

    # Save filtered results
    with open("filtered_alpha.json", "w") as f:
        json.dump(ranked, f, indent=4)

    print(f"✅ Filtered {len(ranked)} tokens (score ≥ 55)")
    if ranked:
        print(f"🏆 Top Token: {ranked[0]['symbol']} [{ranked[0]['conviction_score']}]")

    return ranked


if __name__ == "__main__":
    filter_and_rank()
