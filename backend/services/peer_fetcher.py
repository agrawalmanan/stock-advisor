import yfinance as yf
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round, format_market_cap
from services.financials_calc import get_financial_metrics


# Expanded sector → peers mapping (6 peers each)
SECTOR_PEERS = {
    "Energy": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "HINDPETRO.NS", "PETRONET.NS"],
    "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS"],
    "Financial Services": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BANKBARODA.NS"],
    "Healthcare": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "FORTIS.NS", "BIOCON.NS"],
    "Consumer Defensive": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS"],
    "Consumer Cyclical": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS"],
    "Industrials": ["LT.NS", "SIEMENS.NS", "ABB.NS", "BHEL.NS", "HAL.NS", "BEL.NS", "CUMMINSIND.NS"],
    "Basic Materials": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "SAIL.NS", "NMDC.NS", "COALINDIA.NS"],
    "Utilities": ["NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS", "ADANIGREEN.NS", "NHPC.NS", "SJVN.NS", "IREDA.NS"],
    "Real Estate": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS", "LODHA.NS"],
    "Communication Services": ["BHARTIARTL.NS", "IDEA.NS", "TATACOMM.NS", "INDUSTOWER.NS", "ROUTE.NS", "NAZARA.NS", "LATENTVIEW.NS"],
}


def get_peers_by_sector(sector: str, exclude_symbol: str, limit: int = 6) -> list:
    """Find peer symbols from same sector"""
    peers = SECTOR_PEERS.get(sector, [])
    peers = [p for p in peers if p != exclude_symbol]
    return peers[:limit]


def get_peer_data(peer_symbols: list, exclude_symbol: str = "", sector: str = "") -> dict:
    """
    Fetch detailed data for peer stocks including ROCE and OPM
    Returns peers list + industry median
    """
    # If no peers provided, find by sector
    if not peer_symbols and sector:
        peer_symbols = get_peers_by_sector(sector, exclude_symbol)

    if not peer_symbols:
        return {"peers": [], "industry_median": {}}

    cache_key = f"peers_enhanced_{'_'.join(sorted(peer_symbols[:6]))}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    peers = []

    for symbol in peer_symbols[:6]:
        try:
            if not symbol.endswith(".NS"):
                symbol = symbol + ".NS"

            if symbol == exclude_symbol:
                continue

            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                continue

            current_price = info.get("regularMarketPrice") or info.get("currentPrice")
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

            change_pct = "N/A"
            if current_price and prev_close:
                change_pct = safe_round(
                    ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
                )

            # Get financial metrics (ROCE, OPM)
            financials = get_financial_metrics(symbol)

            peers.append({
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "current_price": safe_round(current_price),
                "change_pct": change_pct,
                "market_cap": format_market_cap(info.get("marketCap")),
                "market_cap_raw": info.get("marketCap", 0),
                "pe_ratio": financials.get("pe_ratio", "N/A"),
                "roce_pct": financials.get("roce_pct", "N/A"),
                "opm_pct": financials.get("opm_pct", "N/A"),
                "week_52_high": safe_round(info.get("fiftyTwoWeekHigh")),
                "week_52_low": safe_round(info.get("fiftyTwoWeekLow")),
                "sector": info.get("sector", "N/A"),
            })

        except Exception as e:
            print(f"Peer fetch error for {symbol}: {e}")
            continue

    # Calculate Industry Median
    industry_median = calculate_industry_median(peers)

    result = {
        "peers": peers,
        "industry_median": industry_median
    }

    # Cache for 10 minutes (peer data takes long to fetch)
    set_cache(cache_key, result, ttl_seconds=600)
    return result


def calculate_industry_median(peers: list) -> dict:
    """
    Calculate median of P/E, ROCE%, OPM% across all peers
    """
    import statistics

    def get_valid_numbers(key):
        vals = []
        for p in peers:
            v = p.get(key)
            if v != "N/A" and v is not None:
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
        return vals

    pe_values = get_valid_numbers("pe_ratio")
    roce_values = get_valid_numbers("roce_pct")
    opm_values = get_valid_numbers("opm_pct")
    price_values = get_valid_numbers("current_price")
    change_values = get_valid_numbers("change_pct")

    return {
        "pe_ratio": safe_round(statistics.median(pe_values)) if pe_values else "N/A",
        "roce_pct": safe_round(statistics.median(roce_values)) if roce_values else "N/A",
        "opm_pct": safe_round(statistics.median(opm_values)) if opm_values else "N/A",
        "current_price": safe_round(statistics.median(price_values)) if price_values else "N/A",
        "change_pct": safe_round(statistics.median(change_values)) if change_values else "N/A",
        "market_cap": "Median",
    }