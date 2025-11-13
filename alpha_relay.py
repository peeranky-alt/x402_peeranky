# ==============================
#  PHASE 9: REAL-TIME ALPHA RELAY
# ==============================
# Monitors filtered_alpha.json and relays new high-conviction tokens
# directly to Telegram in real time.

import json, time, requests
from datetime import datetime

BOT_TOKEN = "7404930359:AAFBMfFIZUZuToI25LszgYcAlgdcYdWCLTo"
CHAT_ID = "6926777491"

def load_filtered():
    try:
        with open("filtered_alpha.json", "r") as f:
            return json.load(f)
    except:
        return []

def send_tg_alert(token):
    msg = (
        f"🚨 *NEW HIGH-CONVICTION TOKEN ALERT* 🚨\n\n"
        f"*Name:* {token.get('name','N/A')} ({token.get('symbol','?')})\n"
        f"*Score:* {token.get('conviction_score','?')}\n"
        f"*Reputation:* {token.get('reputation','?')}\n"
        f"*Narrative:* {token.get('context','?')}\n"
        f"*Chain:* {token.get('chain','?').upper()}\n"
        f"*CA:* `{token.get('ca','?')}`\n\n"
        f"_Detected at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"✅ TG Alert Sent for {token.get('symbol')}")
        else:
            print(f"⚠️ TG send error: {r.text}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def watch_filtered():
    print("🧠 Alpha Relay running... Checking filtered_alpha.json every 5 minutes.")
    sent_cache = set()

    while True:
        data = load_filtered()
        if not data:
            print("⚠️ No filtered tokens yet — waiting...")
            time.sleep(300)
            continue

        for token in data:
            ca = token.get("ca")
            score = token.get("conviction_score", 0)
            if ca and ca not in sent_cache and score >= 70:
                send_tg_alert(token)
                sent_cache.add(ca)

        print(f"✅ Cycle complete — {len(sent_cache)} relays sent so far.\n")
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    watch_filtered()
