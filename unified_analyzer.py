import random
from datetime import datetime

def unified_analyze(token):
    """
    Extended AI-based analyzer for Base + Solana tokens.
    Computes conviction score, reputation tag, and structured insight.
    """

    # === Basic metadata (you can expand this from live APIs later) ===
    chain = token.get("chain", "unknown")
    ca = token.get("ca", "N/A")
    symbol = token.get("symbol", "N/A")
    context = token.get("context", "emerging token")

    # === Fake analysis data for now (later we go plug APIs) ===
    owner_revoked = random.choice(["✅", "❌"])
    freeze_auth = random.choice(["✅", "❌"])
    market_cap = random.randint(50_000, 2_000_000)
    top10_combined = random.randint(10, 90)
    narrative = random.choice(["AI Agent", "Content Coin", "Community", "Experimental", "DeFi Play"])
    time_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # === Conviction score computation ===
    score = 0
    if owner_revoked == "✅": score += 20
    if freeze_auth == "✅": score += 20
    if market_cap < 1_000_000: score += 10
    if top10_combined < 40: score += 20
    if any(x in context.lower() for x in ["ai", "agent", "content", "meme"]): score += 10
    if chain in ["base", "solana"]: score += 10
    if random.random() > 0.8: score += 10  # small randomness factor

    # === Reputation tag ===
    if score >= 75:
        reputation = "🔥 Strong"
    elif score >= 50:
        reputation = "⚡ Medium"
    else:
        reputation = "⚠️ Low"

    # === Final result package ===
    result = {
        "chain": chain,
        "ca": ca,
        "symbol": symbol,
        "context": context,
        "owner_revoked": owner_revoked,
        "freeze_auth": freeze_auth,
        "market_cap": market_cap,
        "top10_combined": top10_combined,
        "conviction_score": score,
        "reputation": reputation,
        "narrative": narrative,
        "added": time_now
    }

    # === Print quick summary to console ===
    print(f"\n🧠 [{symbol}] ({chain.upper()}) Analysis Complete:")
    print(f"Conviction Score: {score} | Reputation: {reputation}")
    print(f"Narrative: {narrative}\n")

    return result
