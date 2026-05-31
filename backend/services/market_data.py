from services.stock_mapper import get_stock_meta, NSE_STOCKS
from services.nse_client import get_fast_quote, get_fast_chart
from utils.cache import get_cache, set_cache
from utils.helpers import format_market_cap, format_volume, safe_round, safe_get
from utils.yf_client import get_ticker, with_retries
from utils.rate_limiter import rate_limit


def get_stock_data(symbol: str) -> dict:
    """
    Fetch full live stock data
    Uses fast Yahoo chart API for price + yfinance for fundamentals
    """
    cache_key = f"stock_data_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    meta = get_stock_meta(symbol)

    # Step 1: Get live price from fast API (no rate limit issues)
    fast = get_fast_quote(symbol)

    # Step 2: Get fundamentals from yfinance (cached heavily)
    yf_info = _get_yf_fundamentals(symbol)

    if not fast and not yf_info:
        return {"error": f"Failed to fetch data for {symbol}"}

    current_price = fast.get("current_price") or safe_round(
        yf_info.get("regularMarketPrice") or yf_info.get("currentPrice")
    )

    if not current_price or current_price == "N/A":
        return {"error": f"Stock '{symbol}' not found or market closed"}

    prev_close = fast.get("prev_close") or safe_round(
        yf_info.get("regularMarketPreviousClose") or yf_info.get("previousClose")
    )

    change = fast.get("change", "N/A")
    change_pct = fast.get("change_pct", "N/A")

    sector = yf_info.get("sector") or meta.get("sector", "Unknown")
    peers = meta.get("peers", [])
    if not peers:
        peers = _get_peers_from_sector(sector, exclude_symbol=symbol)

    market_cap_raw = yf_info.get("marketCap")

    result = {
        "name": fast.get("name") or yf_info.get("longName") or meta.get("name", symbol),
        "symbol": symbol,
        "sector": sector,
        "peers": peers,

        "current_price": current_price,
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,

        "day_high": fast.get("day_high") or safe_round(yf_info.get("dayHigh")),
        "day_low": fast.get("day_low") or safe_round(yf_info.get("dayLow")),
        "week_52_high": fast.get("week_52_high") or safe_round(yf_info.get("fiftyTwoWeekHigh")),
        "week_52_low": fast.get("week_52_low") or safe_round(yf_info.get("fiftyTwoWeekLow")),

        "volume": fast.get("volume") or yf_info.get("regularMarketVolume"),
        "volume_formatted": fast.get("volume_formatted") or format_volume(yf_info.get("regularMarketVolume")),
        "avg_volume": yf_info.get("averageVolume", "N/A"),

        "market_cap_raw": market_cap_raw,
        "market_cap": format_market_cap(market_cap_raw),

        "pe_ratio": safe_round(yf_info.get("trailingPE")),
        "pb_ratio": safe_round(yf_info.get("priceToBook")),
        "dividend_yield": safe_round(yf_info.get("dividendYield"), 4),
        "beta": safe_round(yf_info.get("beta")),
        "eps": safe_round(yf_info.get("trailingEps")),

        "exchange": "NSE",
        "currency": "INR",
        "data_source": fast.get("source", "yfinance"),
    }

    set_cache(cache_key, result, ttl_seconds=300)
    return result


def _get_yf_fundamentals(symbol: str) -> dict:
    """
    Get fundamentals from yfinance — heavily cached
    Only called once per hour per stock
    """
    cache_key = f"yf_fundamentals_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        rate_limit()
        ticker = get_ticker(symbol)
        info = with_retries(lambda: ticker.info) or {}
        # Cache 1 hour — fundamentals don't change frequently
        set_cache(cache_key, info, ttl_seconds=3600)
        return info
    except Exception as e:
        print(f"[YF FUNDAMENTALS] Error for {symbol}: {e}")
        return {}


def get_historical_returns(symbol: str) -> dict:
    """Calculate 1M, 3M, 6M, 1Y, 5Y returns using fast API"""
    cache_key = f"returns_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    periods = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "5Y": "5y"}
    returns = {}

    for label, period in periods.items():
        try:
            from services.nse_client import get_fast_history
            history = get_fast_history(symbol, period)
            if history and len(history) >= 2:
                start = history[0]["close"]
                end = history[-1]["close"]
                if start and end and start > 0:
                    returns[label] = safe_round(((end - start) / start) * 100)
                else:
                    returns[label] = "N/A"
            else:
                returns[label] = "N/A"
        except Exception:
            returns[label] = "N/A"

    set_cache(cache_key, returns, ttl_seconds=43200)  # 12 hours
    return returns


def get_chart_data(symbol: str, period: str = "3mo") -> list:
    """Get chart data using fast API"""
    candles = get_fast_chart(symbol, period)
    return candles


def _get_peers_from_sector(sector: str, exclude_symbol: str = "") -> list:
    peers = []
    for stock in NSE_STOCKS:
        if stock.get("sector") == sector and stock.get("symbol") != exclude_symbol:
            peers.append(stock["symbol"])
        if len(peers) >= 6:
            break
    return peers