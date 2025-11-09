from analyzer import analyze_token

# Example test token data
test_token = {
    "symbol": "LOVE",
    "ca": "H6dFakeExampleContract111111111111111111111111111",  # replace with real CA to test
    "supply": 1_000_000_000,
    "owner_revoked": "✅",
    "freeze_auth": "✅",
    "raydium_pool": "✅",
    "deployer_pct": 8,
    "market_cap": 420_000
}

if __name__ == "__main__":
    alert_message = analyze_token(test_token, deployer_history="New dev")
    print(alert_message)
