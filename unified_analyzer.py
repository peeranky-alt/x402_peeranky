from analyzer import analyze_token as analyze_solana
from base_analyzer import analyze_token_base as analyze_base

def unified_analyze(token_data):
    """
    Auto-detect chain and route analysis accordingly.
    token_data must contain 'chain' field: 'sol' or 'base'
    """
    try:
        chain = token_data.get("chain", "").lower()

        if chain == "sol":
            return analyze_solana(token_data)

        elif chain == "base":
            return analyze_base(token_data)

        else:
            return "❌ Unknown chain type. Please specify 'sol' or 'base'."

    except Exception as e:
        return f"❌ Unified analyzer error: {str(e)}"
