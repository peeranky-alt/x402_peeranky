import re

def classify_token_context(name: str, symbol: str, deployer_label: str = ""):
    """
    🔍 Identify token narrative type based on name, symbol & deployer info
    """
    text = f"{name} {symbol} {deployer_label}".lower()

    # 🧠 Category keywords
    categories = {
        "ai": ["ai", "agent", "gpt", "bot", "neural", "auto"],
        "meme": ["pepe", "doge", "cat", "frog", "meme", "based"],
        "degen": ["ape", "pump", "moon", "degen", "rekt"],
        "social": ["friend", "post", "tweet", "x", "viral", "fren"],
        "gamefi": ["game", "play", "nft", "quest", "xp"],
        "base_narrative": ["base", "coinbase", "brian", "onbase"],
        "eth_narrative": ["eth", "ethereum", "vitalik", "l2"],
        "solana_narrative": ["sol", "solana", "raydium", "jupiter"]
    }

    tags = []
    for category, words in categories.items():
        if any(w in text for w in words):
            tags.append(category)

    # 🧩 Combine logic
    if not tags:
        tags.append("unknown")

    if "ai" in tags and "meme" in tags:
        tags.append("hybrid_ai_meme")

    if "degen" in tags and "base_narrative" in tags:
        tags.append("base_degen_rotation")

    return list(set(tags))


def analyze_context_summary(name: str, symbol: str, deployer_label: str = ""):
    tags = classify_token_context(name, symbol, deployer_label)
    primary = tags[0]
    summary = f"🧠 Context: {', '.join(tags)} | Core: {primary.upper()}"
    return summary
