import sqlite3
import datetime
import requests

# === Database Setup ===
DB_PATH = "conviction_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain TEXT,
            ca TEXT,
            symbol TEXT,
            name TEXT,
            creator TEXT,
            market_cap REAL,
            detected_at TEXT,
            last_update TEXT,
            performance REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# === Add New Token ===
def save_new_token(data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO memory (chain, ca, symbol, name, creator, market_cap, detected_at, last_update)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("chain"),
        data.get("ca"),
        data.get("symbol"),
        data.get("name"),
        data.get("creator"),
        data.get("market_cap", 0),
        datetime.datetime.utcnow().isoformat(),
        datetime.datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


# === Update Performance Later ===
def update_performance(ca, new_cap):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT market_cap FROM memory WHERE ca=?", (ca,))
    row = cur.fetchone()
    if row:
        old_cap = row[0] or 0
        performance = ((new_cap - old_cap) / old_cap * 100) if old_cap > 0 else 0
        cur.execute("""
            UPDATE memory
            SET market_cap=?, performance=?, last_update=?
            WHERE ca=?
        """, (new_cap, performance, datetime.datetime.utcnow().isoformat(), ca))
    conn.commit()
    conn.close()


# === Simple Scoring ===
def top_performers(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT symbol, performance FROM memory ORDER BY performance DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
