import requests

BOT_TOKEN = "8114783573:AAGAJZ0C9GYoqWDU2gX4nbpZhWe89BMO7d4"
CHAT_ID = "6926777491"  # your user ID

msg = "✅ Test message from CTAnalyzerBot"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": msg}

r = requests.post(url, data=payload)
print(r.json())
