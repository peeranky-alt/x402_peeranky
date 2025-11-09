from pyrogram import Client, filters
import re
import os
import subprocess

# ====== YOUR SESSION STRING (keep secret) ======
SESSION_STRING = "BAAAB_gAaL0j71ZQC_Nz7wf--LZEKa1jqBsCRr69H2Kx9vc-CTiiE7ciBDpEIMVbmgncYMD0b1RKHkJxWl-x9NBN4mY8qNlOnw1Z8YsXKBTOH48yGioqTs67Fw1cZdXgpnWmp9PUKuktRry42ZUVQcVgrk9C01r_I-Yzp0UTFhIMxZd4bvaVXHFzwZdLE9iX9eKRdtnFg5_v4HeMvmsglQWTqFWmAaqHDidSbIrIP5VClspJYHsrwKaHmqFtLHbK9c9qSGgYLsLwjIqGfu2-CSyPg6FaGjYgEAfvWis_vMsCDvqwGYZjrijxR4fqDDWZKclSyEpwlvBDRelvyuhfOmt2_buGiQAAAAGc3jyTAA"

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

# Channel to monitor
TARGET_CHAT = "DriftDegen"

# Regex for Solana contract addresses (32–44 base58 chars)
BASE58_RE = re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b')

app = Client(
    name="rugbot",
    session_string=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(filters.chat(TARGET_CHAT))
def handler(client, message):
    text = message.text or message.caption or ""
    if not text:
        return
    matches = BASE58_RE.findall(text)
    if not matches:
        return
    # remove duplicates
    matches = list(dict.fromkeys(matches))
    for m in matches:
        if len(m) >= 32:
            print(f"🟢 Sending {m} to analyzer...")
            subprocess.run(["python", "analyzer.py", m])

if __name__ == "__main__":
    print("🚀 RugBot (scraper) starting — listening to:", TARGET_CHAT)
    app.run()
