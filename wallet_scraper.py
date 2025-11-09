import requests
import json
import time
from datetime import datetime

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["telegram_bot_token"]
CHAT_ID = config["telegram_chat_id"]

def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def get_token_data(ca: str):
    url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
    r = requests.get(url).json()
    if not r.get("pairs"):
        return None
    return r["pairs"][0]

def analyze_token(ca: str):
    pair = get_token_data(ca)
    if not pair:
        return []

    # Dexscreener only exposes traders summary (not full holders) – so we simulate alpha wallets
    txns = pair.get("txns", {}).get("h24", [])
    if not txns:
        return []

    # Example: identify wallets that bought early & are in profit
    alpha_wallets = []
    price_usd = float(pair["priceUsd"])
    base_token = pair["baseToken"]["symbol"]

    for txn in txns:
        # placeholder – normally you'd call etherscan or another API for pnl
        wallet = txn.get("maker") or txn.get("from")
        if not wallet:
            continue

        # Fake rule: assume buys < 1h old at lower price are alpha
        ts = txn.get("blockTimestamp", int(time.time()))
        buy_time = datetime.fromtimestamp(ts)
        value_usd = float(txn.get("usdValue", 0))

        if value_usd > 1000:  # filter
            alpha_wallets.append({
                "wallet": wallet,
                "first_buy": str(buy_time),
                "value_usd": value_usd,
                "current_price": price_usd,
                "token": base_token
            })

    return alpha_wallets

def save_alpha_wallets(wallets, filename="alpha_wallets.json"):
    try:
        with open(filename, "r") as f:
            old = json.load(f)
    except:
        old = []

    combined = old + wallets
    with open(filename, "w") as f:
        json.dump(combined, f, indent=2)

if __name__ == "__main__":
    for ca in config["token_addresses"]:
        alphas = analyze_token(ca)
        if alphas:
            save_alpha_wallets(alphas)
            msg = f"*Alpha wallets found for {ca}*\n\n"
            for w in alphas:
                msg += f"Wallet: `{w['wallet']}`\nFirst Buy: {w['first_buy']}\nAmount: ${w['value_usd']}\n\n"
            send_telegram(msg)
        else:
            print(f"No alpha wallets for {ca}")
