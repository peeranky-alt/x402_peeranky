from flask import Flask, request
import os
import requests

app = Flask(__name__)

# ==============================
# Telegram Webhook + Handlers
# ==============================

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route('/', methods=['GET'])
def home():
    return "🤖 Peetaskbot is alive!", 200

@app.route('/', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "👋 Hey boss! Bot is live and ready for tasks.")
        else:
            send_message(chat_id, f"✅ Message received: {text}")

    return "ok", 200


# ==============================
# Run Flask
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8787)
