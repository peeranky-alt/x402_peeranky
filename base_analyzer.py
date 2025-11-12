import requests

def get_top_holders(ca):
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        holders_data = data.get("pairs", [])
        if not holders_data:
            return {"holders": "N/A", "lp_locked": "Unknown"}

        pair = holders_data[0]
        liquidity = pair.get("liquidity", {})
        lp_locked = "✅" if liquidity.get("locked", 0) > 0 else "❌"
        fdv = pair.get("fdv", "N/A")

        return {
            "lp_locked": lp_locked,
            "fdv": fdv
        }
    except Exception:
        return {"lp_locked": "N/A", "fdv": "N/A"}


def get_deployer_activity(deployer):
    try:
        url = f"https://api.basescan.org/api?module=account&action=txlist&address={deployer}&sort=desc"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        txs = data.get("result", [])
        if not txs:
            return "No recent activity"

        deploy_count = sum(1 for tx in txs if tx.get("isError") == "0")
        unique_contracts = len(set(tx["to"] for tx in txs if tx.get("to")))

        return f"Tx count: {deploy_count}, Interacted contracts: {unique_contracts}"
    except Exception:
        return "Error fetching deployer activity"


def analyze_token_base(token_data):
    try:
        ca = token_data.get("ca", "UnknownCA")
        name = token_data.get("name", "Unknown")
        symbol = token_data.get("symbol", "UNK")
        supply = token_data.get("supply", "N/A")
        creator = token_data.get("creator", "Unknown")

        holders_info = get_top_holders(ca)
        deployer_history = get_deployer_activity(creator)

        status = "⚠️ RISKY"
        if holders_info["lp_locked"] == "✅":
            status = "✅ SAFER"

        alert = f"""
🚨 New Base Token Detected 🚨
Name: {name} (${symbol})
CA: {ca}
Total Supply: {supply}
LP Locked: {holders_info["lp_locked"]}
FDV: {holders_info['fdv']}
Creator: {creator}
Deployer Activity: {deployer_history}
Status: {status}
"""
        return alert.strip()
    except Exception as e:
        return f"❌ Analyzer error: {str(e)}"
