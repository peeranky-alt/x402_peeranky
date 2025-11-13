# x402_peeranky.py
import json, time, os, requests, datetime, random
from rich.console import Console
from rich.table import Table

console = Console()

# === TELEGRAM CONFIG ===
BOT_TOKEN = "7404930359:AAFBMfFIZUZuToI25LszgYcAlgdcYdWCLTo"
CHAT_ID = "6926777491"  # replace with your actual chat id

# === FILE STORAGE ===
MEMORY_FILE = "conviction_memory.json"

# === CHAINS TO MONITOR ===
CHAINS = ["base", "solana"]

# === FAKE TOKEN FETCH (replace later with onchain sources or APIs) ===
def fetch_new_tokens(chain):
    samples = [
        {"symbol": "AIPEER", "ca": f"0x{random.randint(10**15, 10**16)}", "context": "AI + agent narrative"},
        {"symbol": "MEMEAI", "ca": f"0x{random.randint(10**15, 10**16)}", "context": "content coin on Base"},
    ]
    return random.sample(samples, k=1)

# === CONVICTION SCORE ===
def get_conviction_score(token):
    score = 0
    if token.get("owner_revoked") == "✅": score += 20
    if token.get("freeze_auth") == "✅": score += 20
    if token.get("market_cap", 0) < 1_000_000: score += 10
    if token.get("top10_combined", 100) < 40: score += 20
    ctx = token.get("context", "")
    if "ai" in ctx or "agent" in ctx: score += 10
    if "base" in ctx or "solana" in ctx: score += 5
    return min(score, 100)

def get_reputation_tag(score):
    if score >= 75: return "🔥 Strong"
    elif score >= 50: return "⚡ Medium"
    else: return "⚠️ Low"

# === LOAD + SAVE MEMORY ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === TELEGRAM NOTIFIER ===
def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
        )
    except Exception as e:
        console.print(f"[red]Telegram error:[/red] {e}")

# === UNIFIED ANALYZE ===
def unified_analyze(chain, token):
    # fake example data – later we go plug live sources
    token["chain"] = chain
    token["owner_revoked"] = random.choice(["✅", "❌"])
    token["freeze_auth"] = random.choice(["✅", "❌"])
    token["market_cap"] = random.randint(50_000, 2_000_000)
    token["top10_combined"] = random.randint(10, 90)
    token["added"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    token["status"] = "🧠 Analyzed"

    score = get_conviction_score(token)
    token["conviction_score"] = score
    token["reputation"] = get_reputation_tag(score)
    return token

# === MAIN DETECTION LOOP ===
def start_agent():
    console.print("[bold green]🚀 x402_peeranky agent running...[/bold green]")
    memory = load_memory()
    known_ca = {x["ca"] for x in memory}

    while True:
        try:
            for chain in CHAINS:
                new_tokens = fetch_new_tokens(chain)
                for token in new_tokens:
                    if token["ca"] not in known_ca:
                        analyzed = unified_analyze(chain, token)
                        memory.append(analyzed)
                        save_memory(memory)
                        known_ca.add(token["ca"])

                        msg = (
                            f"🚨 <b>New Token Detected</b>\n"
                            f"Chain: {chain.upper()}\n"
                            f"Symbol: {token['symbol']}\n"
                            f"CA: <code>{token['ca']}</code>\n"
                            f"Context: {token['context']}\n"
                            f"Conviction Score: {token['conviction_score']}\n"
                            f"Reputation: {token['reputation']}\n"
                            f"Added: {token['added']}"
                        )
                        send_telegram(msg)
                        console.print(f"[cyan]🧠 Added {token['symbol']} ({chain})[/cyan]")

            time.sleep(30)  # adjust speed if needed
        except KeyboardInterrupt:
            console.print("[red]Stopped by user[/red]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            time.sleep(10)

if __name__ == "__main__":
    start_agent()





# dashboard.py
import json, os, time
from rich.console import Console
from rich.table import Table

console = Console()

def load_data():
    try:
        with open("conviction_memory.json", "r") as f:
            return json.load(f)
    except:
        return []

def render_table(data):
    table = Table(title="[bold magenta]🧠 Conviction Dashboard – Real-Time View[/bold magenta]")
    table.add_column("Chain", style="cyan")
    table.add_column("Symbol", style="yellow")
    table.add_column("CA", style="green")
    table.add_column("Reputation", style="bold magenta")
    table.add_column("Score", style="bold white")
    table.add_column("Status", style="red")
    table.add_column("Added", style="white")

    for entry in reversed(data[-15:]):
        table.add_row(
            entry.get("chain", "–"),
            entry.get("symbol", "–"),
            entry.get("ca", "–"),
            entry.get("reputation", "–"),
            str(entry.get("conviction_score", "–")),
            entry.get("status", "–"),
            entry.get("added", "–"),
        )
    return table

console.clear()
console.print("[bold green]🧠 Conviction Dashboard – Auto Refresh Active[/bold green]\n")

last_size = 0
while True:
    try:
        size = os.path.getsize("conviction_memory.json")
        if size != last_size:
            last_size = size
            os.system("clear")
            data = load_data()
            console.print(render_table(data))
        time.sleep(10)
    except KeyboardInterrupt:
        console.print("[red]Stopped by user[/red]")
        break
