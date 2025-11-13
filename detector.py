import time
import requests
from datetime import datetime, timezone
from conviction_alerts import alert_and_log
from unified_analyzer import unified_analyze
from notifier import notify_new_token
from conviction_memory import save_new_token, init_db

# === Initialize Conviction DB ===
print("🚀 Live Detector Started — tracking Base & Solana new pairs...\n")
init_db()  # ✅ create DB table if not exist


# === Fetch new token pairs from Dexscreener ===
def fetch_new_pairs():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("pairs", [])
    except Exception as e:
        print(f"❌ Fetch error: {e}")
    return []


# === Filter recent tokens (<= 30 mins old) ===
def filter_recent_tokens(pairs):
    filtered = []
    now = datetime.now(timezone.utc)

    for pair in pairs:
        chain = pair.get("chainId")
        if chain not in ["base", "solana"]:
            continue

        created_at_ms = pair.get("pairCreatedAt")
        if not created_at_ms:
            continue

        created_time = datetime.fromtimestamp(created_at_ms / 1000, tz=timezone.utc)
        minutes_old = (now - created_time).total_seconds() / 60

        if minutes_old <= 30:  # new tokens only
            token = {
                "chain": "base" if chain == "base" else "sol",
                "ca": pair.get("baseToken", {}).get("address"),
                "symbol": pair.get("baseToken", {}).get("symbol"),
                "name": pair.get("baseToken", {}).get("name"),
                "creator": pair.get("pairAddress", "Unknown"),
                "dex": pair.get("dexId"),
                "age": f"{round(minutes_old, 1)} mins ago"
            }
            filtered.append(token)
    return filtered


# === Main Live Scanner Loop ===
known_tokens = set()

while True:
    pairs = fetch_new_pairs()
    recent_tokens = filter_recent_tokens(pairs)

    for token in recent_tokens:
        ca = token.get("ca")
        if ca and ca not in known_tokens:
            known_tokens.add(ca)
            chain = token["chain"]
            print(f"\n🔍 New Token Found on {chain.upper()} — {token['symbol']} ({token['age']})")

            # 🧠 Deep Analysis
            result = unified_analyze(token)
            print(result)

            # 💾 Save to conviction memory DB
            save_new_token(result)

            # 📡 Send alert to Telegram
            notify_new_token(chain, token)

            # 🚨 Trigger Conviction Alert System (logs + highlights top ones)
            alert_and_log(result)

    time.sleep(90)  # check every 1.5 minutes
