import requests
import datetime
from rich.console import Console

console = Console()

# ====== Use Peetaskbot + your chat id ======
TELEGRAM_BOT_TOKEN = "7404930359:AAFBMfFIZUZuToI25LszgYcAlgdcYdWCLTo"
TELEGRAM_CHAT_ID = "6926777491"  # Surely (private chat)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, data=data, timeout=8)
        if res.status_code == 200:
            console.print("📤 Telegram alert sent.", style="green")
        else:
            console.print(f"⚠️ Telegram send failed: {res.status_code} {res.text}", style="red")
    except Exception as e:
        console.print(f"⚠️ Telegram alert failed: {e}", style="red")

def alert_and_log(token_data):
    # build message (Markdown)
    message = (
        f"🧠 *[CONVICTION ALERT]* — {token_data.get('symbol', 'Unknown')}\n"
        f"Reputation: *{token_data.get('reputation', 'N/A')}* | Score: *{token_data.get('conviction_score', 'N/A')}*\n"
        f"Chain: `{token_data.get('chain', 'N/A')}` | CA:\n"
        f"`{token_data.get('ca', 'N/A')}`\n\n"
        f"Narrative: {token_data.get('narrative', 'N/A')}\n"
        f"Detected at: {token_data.get('added', datetime.datetime.utcnow().isoformat())}\n"
        "--------------------------------------------------------"
    )

    # print locally
    console.print(message)

    # send to Telegram (best-effort)
    send_telegram_alert(message)
