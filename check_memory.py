import sqlite3

def view_recent_tokens():
    conn = sqlite3.connect("conviction_memory.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT chain, symbol, conviction_score, reputation, narrative, added
        FROM tokens
        ORDER BY added DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    conn.close()

    print("🧠 Recent Conviction Memory Entries:\n")
    for r in rows:
        print(f"Chain: {r[0].upper()} | Symbol: {r[1]} | Conviction: {r[2]} | Rep: {r[3]} | Narrative: {r[4]} | Added: {r[5]}")

if __name__ == "__main__":
    view_recent_tokens()
