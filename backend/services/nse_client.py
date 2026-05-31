import requests
import time
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round, format_market_cap, format_volume

# NSE requires these headers to not block requests
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/',
    'Connection': 'keep-alive',
}

def get_nse_session() -> requests.Session:
    """
    Create a session with NSE cookies
    NSE requires visiting homepage first to get cookies
    """
    session = requests.Session()
    session.headers.update(NSE_HEADERS)

    try:
        # Visit NSE homepage to get cookies
        session.get(
            'https://www.nseindia.com',
            timeout=10
        )
        time.sleep(0.5)
    except Exception as e:
        print(f"[NSE] Session init error: {e}")

    return session


def get_nse_quote(symbol: str) -> dict:
    """
    Fetch live stock quote from NSE India API
    symbol: e.g. RELIANCE (without .NS)
    """
    cache_key = f"nse_quote_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    clean_symbol = symbol.replace(".NS", "").replace(".BO", "").upper()

    try:
        session = get_nse_session()

        url = f"https://www.nseindia.com/api/quote-equity?symbol={clean_symbol}"
        response = session.get(url, timeout=10)

        if response.status_code != 200:
            print(f"[NSE] Status {response.status_code} for {clean_symbol}")
            return {}

        data = response.json()

        price_info = data.get("priceInfo", {})
        trade_info = data.get("industryInfo", {})
        info = data.get("info", {})
        metadata = data.get("metadata", {})
        security_info = data.get("securityInfo", {})

        # Basic price data
        current_price = price_info.get("lastPrice")
        prev_close = price_info.get("previousClose")

        change = None
        change_pct = None
        if current_price and prev_close:
            change = safe_round(float(current_price) - float(prev_close))
            change_pct = safe_round(
                ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
            )

        # Day range
        intraday_hl = price_info.get("intraDayHighLow", {})
        day_high = intraday_hl.get("max")
        day_low = intraday_hl.get("min")

        # 52 week range
        week_hl = price_info.get("weekHighLow", {})
        week_52_high = week_hl.get("max")
        week_52_low = week_hl.get("min")

        # Volume and market cap
        trade_volume = price_info.get("totalTradedVolume")
        market_cap_raw = metadata.get("pdSectorPe")  # fallback

        result = {
            "current_price": safe_round(current_price),
            "prev_close": safe_round(prev_close),
            "change": change,
            "change_pct": change_pct,
            "day_high": safe_round(day_high),
            "day_low": safe_round(day_low),
            "week_52_high": safe_round(week_52_high),
            "week_52_low": safe_round(week_52_low),
            "volume": trade_volume,
            "volume_formatted": format_volume(trade_volume) if trade_volume else "N/A",
            "sector": trade_info.get("macro", "Unknown"),
            "industry": trade_info.get("sector", "Unknown"),
            "pe_ratio": safe_round(metadata.get("pdSectorPe")),
            "symbol_clean": clean_symbol,
            "source": "nse"
        }

        # Cache for 3 minutes (NSE updates frequently)
        set_cache(cache_key, result, ttl_seconds=180)
        return result

    except Exception as e:
        print(f"[NSE] Quote error for {clean_symbol}: {e}")
        return {}


def get_nse_market_status() -> bool:
    """Check if NSE market is open"""
    try:
        session = get_nse_session()
        response = session.get(
            "https://www.nseindia.com/api/marketStatus",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            markets = data.get("marketState", [])
            for market in markets:
                if market.get("market") == "Capital Market":
                    return market.get("marketStatus") == "Open"
    except Exception:
        pass
    return False