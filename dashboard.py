import json
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

def load_memory():
    try:
        with open("conviction_memory.json", "r") as f:
            return json.load(f)
    except:
        return []

def build_table(data):
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Chain", justify="center")
    table.add_column("Symbol", justify="center")
    table.add_column("CA", justify="center")
    table.add_column("Context", justify="center")
    table.add_column("Reputation", justify="center")
    table.add_column("Added", justify="center")

    for token in reversed(data[-15:]):  # Show last 15 tokens
        chain = token.get("chain", "N/A").upper()
        symbol = token.get("symbol", "N/A")
        ca = token.get("ca", "N/A")[:10] + "..." if token.get("ca") else "N/A"
        context = token.get("context", "N/A")
        reputation = token.get("reputation", "⚠️ Low")
        added = token.get("added", "N/A")

        try:
            added = datetime.strptime(added, "%Y-%m-%d %H:%M:%S UTC").strftime("%H:%M:%S")
        except:
            pass

        table.add_row(chain, symbol, ca, context, reputation, added)
    return table

def main():
    console.print(Panel("🧠 [bold yellow]Conviction Dashboard[/bold yellow] — Tracking New Tokens in Real Time", style="cyan"))
    with Live(refresh_per_second=1) as live:
        while True:
            data = load_memory()
            table = build_table(data)
            live.update(table)
            time.sleep(5)

if __name__ == "__main__":
    main()
