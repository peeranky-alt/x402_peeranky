import requests
from datetime import datetime

# Import token analyzer
from unified_analyzer import unified_analyze
from context_engine import analyze_context_summary
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message: str):
    """Send a clean formatted alert to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Telegram send error: {e}")


def notify_new_token(chain: str, token_data: dict):
    """Generate formatted token summary and push to Telegram"""
    try:
        name = token_data.get("name", "Unknown")
        symbol = token_data.get("symbol", "???")
        ca = token_data.get("ca", "N/A")

        # Generate unified analysis
        analysis = unified_analyze(token_data)

        # Extract context
        context_result = analyze_context_summary(name, symbol, token_data.get("creator", ""))

        # Format message
        message = f"""
📡 *[{chain.upper()}]* | ${symbol}
🧠 *Context:* {context_result}
⚙️ *Status:* {("⚠️ RISKY" if "⚠️" in analysis else "✅ SAFE")}
🔗 *CA:* `{ca}`
🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()

        # Send to Telegram
        send_telegram_message(message)

        print(f"✅ Sent alert for {symbol} ({chain})")
    except Exception as e:
        print(f"❌ Notify error: {e}")
