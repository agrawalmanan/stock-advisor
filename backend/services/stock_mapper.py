import json
import os

# Load the NSE stocks JSON once when server starts
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_PATH = os.path.join(_BASE_DIR, "data", "nse_stocks.json")

with open(_DATA_PATH, "r") as f:
    NSE_STOCKS = json.load(f)

# Build a quick lookup dictionary: symbol → full stock info
SYMBOL_MAP = {stock["symbol"]: stock for stock in NSE_STOCKS}


def search_stocks(query: str, limit: int = 10) -> list:
    """
    Search stocks by name or symbol
    Returns top matches for autocomplete
    """
    query = query.lower().strip()
    if not query:
        return []

    results = []
    for stock in NSE_STOCKS:
        name_match = query in stock["name"].lower()
        symbol_match = query in stock["symbol"].lower()
        if name_match or symbol_match:
            results.append({
                "name": stock["name"],
                "symbol": stock["symbol"],
                "sector": stock["sector"]
            })
        if len(results) >= limit:
            break

    return results


def get_stock_meta(symbol: str) -> dict:
    """
    Get sector, peers for a given symbol
    Tries both with and without .NS suffix
    """
    # try direct match
    if symbol in SYMBOL_MAP:
        return SYMBOL_MAP[symbol]

    # try adding .NS
    symbol_ns = symbol + ".NS"
    if symbol_ns in SYMBOL_MAP:
        return SYMBOL_MAP[symbol_ns]

    # not found, return defaults
    return {
        "name": symbol,
        "symbol": symbol,
        "sector": "Unknown",
        "peers": []
    }