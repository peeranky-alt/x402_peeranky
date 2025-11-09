import requests, json, time
from datetime import datetime

# Load config
with open("config.json") as f:
    CONFIG = json.load(f)

BOT_TOKEN = CONFIG["telegram_bot_token"]
CHAT_ID = CONFIG["telegram_chat_id"]

def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

def analyze_token(ca):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
    r = requests.get(url).json()

    if not r.get("pairs"):
        return []

    trades = r["pairs"][0].get("txns", {}).get("h24", [])
    alphas = []

    for txn in trades:
        # sometimes txn is dict, sometimes just address string
        if isinstance(txn, dict):
            wallet = txn.get("maker") or txn.get("from") or "unknown"
            amount_usd = txn.get("usdValue", 0)
            side = txn.get("side", "")
            timestamp = txn.get("timestamp", int(time.time()))
        elif isinstance(txn, str):
            wallet = txn
            amount_usd = 0
            side = "unknown"
            timestamp = int(time.time())
        else:
            continue

        # Filter for whales / potential alpha
        if amount_usd >= CONFIG["filters"]["min_trade_value_usd"]:
            alphas.append({
                "wallet": wallet,
                "amount_usd": amount_usd,
                "side": side,
                "time": datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            })

    return alphas

if __name__ == "__main__":
    for ca in CONFIG["token_addresses"]:
        alphas = analyze_token(ca)
        if alphas:
            for a in alphas:
                msg = f"""
🚨 Alpha Wallet Detected
Wallet: {a['wallet']}
Trade: {a['side']}
Amount: ${a['amount_usd']}
Time: {a['time']}
CA: {ca}
"""
                send_telegram(msg)

            # Save detected wallets
            with open("alpha_wallets.json", "w") as f:
                json.dump(alphas, f, indent=2)
        else:
            print(f"No alpha trades for {ca}")
