import requests

def get_holders_distribution(ca):
    try:
        url = f"https://public-api.solscan.io/token/holders?tokenAddress={ca}&limit=10"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        holders = []
        total_percent = 0
        for i, h in enumerate(data.get("data", []), start=1):
            pct = round(h.get("percent", 0) * 100, 2)
            holders.append(f"#{i}: {pct}%")
            total_percent += pct

        unique_holders = data.get("total", "N/A")

        return {
            "holders": holders,
            "top10_combined": total_percent,
            "unique_holders": unique_holders
        }
    except Exception:
        return {"holders": [], "top10_combined": "N/A", "unique_holders": "N/A"}


def analyze_token(token_data, deployer_history="New dev"):
    try:
        ca = token_data.get("ca", "UnknownCA")
        symbol = token_data.get("symbol", "UNK")
        supply = token_data.get("supply", 0)
        owner_revoked = token_data.get("owner_revoked", "❌")
        freeze_auth = token_data.get("freeze_auth", "❌")
        raydium_pool = token_data.get("raydium_pool", "❌")
        deployer_pct = token_data.get("deployer_pct", "N/A")
        market_cap = token_data.get("market_cap", 0)

        # 🔎 Fetch holders distribution
        holders_info = get_holders_distribution(ca)
        holders_text = "\n".join(holders_info["holders"])
        if not holders_text:
            holders_text = "Unavailable"

        # ✅ Simple status check
        status = "GOOD ✅" if owner_revoked == "✅" and freeze_auth == "✅" else "⚠️ RISKY"

        alert = f"""
🚨 New SPL Token Detected 🚨
Name: ${symbol}
CA: {ca}
Supply: {supply:,}
Owner Revoked: {owner_revoked}
Freeze Authority: {freeze_auth}
Raydium Pool: {raydium_pool}
Top Holders:
{holders_text}
Top 10 Combined: {holders_info["top10_combined"]}%
Unique Holders: {holders_info["unique_holders"]}
Deployer Wallet: {deployer_pct}%
Deployer History: {deployer_history}
Market Cap: ${market_cap:,}
Status: {status}
"""
        return alert.strip()
    except Exception as e:
        return f"❌ Analyzer error: {str(e)}"
