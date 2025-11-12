import time
import requests
from datetime import datetime, timezone
from unified_analyzer import unified_analyze
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram send error: {e}")

def fetch_new_pairs():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json().get("pairs", [])
    except Exception as e:
        print(f"❌ Fetch error: {e}")
    return []

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

        if minutes_old <= 30:  # Only tokens created within the last 30 mins
            token = {
                "chain": "base" if chain == "base" else "sol",
                "ca": pair.get("baseToken", {}).get("address"),
                "symbol": pair.get("baseToken", {}).get("symbol"),
                "dex": pair.get("dexId"),
                "age": f"{round(minutes_old, 1)} mins ago"
            }
            filtered.append(token)
    return filtered

print("🚀 Live Detector Started — tracking Base & Solana new pairs...\n")

known_tokens = set()

while True:
    pairs = fetch_new_pairs()
    recent_tokens = filter_recent_tokens(pairs)

    for token in recent_tokens:
        ca = token.get("ca")
        if ca and ca not in known_tokens:
            known_tokens.add(ca)
            print(f"\n🔍 New Token Found on {token['chain'].upper()} — {token['symbol']} ({token['age']})")
            result = unified_analyze(token)
            print(result)
            send_telegram_message(result)

    time.sleep(90)  # Check every 1.5 minutes
