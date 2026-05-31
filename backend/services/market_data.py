from services.stock_mapper import get_stock_meta, NSE_STOCKS
from services.nse_client import get_fast_quote, get_fast_chart, get_fast_history
from services.screener_client import get_screener_fundamentals
from utils.cache import get_cache, set_cache
from utils.helpers import format_market_cap, format_volume, safe_round
from utils.yf_client import get_ticker, with_retries
from utils.rate_limiter import rate_limit


def get_stock_data(symbol: str) -> dict:
    """
    Fetch full live stock data
    Live data from Yahoo chart API
    Fundamentals from Screener.in
    yfinance only as optional fallback
    """
    cache_key = f"stock_data_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    meta = get_stock_meta(symbol)

    fast = get_fast_quote(symbol)
    screener = get_screener_fundamentals(symbol)
    yf_info = _get_yf_fundamentals(symbol)  # optional fallback

    if not fast and not screener and not yf_info:
        return {"error": f"Failed to fetch data for {symbol}"}

    current_price = fast.get("current_price")
    prev_close = fast.get("prev_close")

    if not current_price or current_price == "N/A":
        return {"error": f"Stock '{symbol}' not found or market closed"}

    # Sector
    sector = (
        yf_info.get("sector") or
        meta.get("sector", "Unknown")
    )

    peers = meta.get("peers", [])
    if not peers:
        peers = _get_peers_from_sector(sector, exclude_symbol=symbol)

    # Market cap from screener (crore -> rupees)
    market_cap_raw = None
    if screener.get("market_cap_cr") is not None:
        market_cap_raw = screener["market_cap_cr"] * 10000000
    elif yf_info.get("marketCap"):
        market_cap_raw = yf_info.get("marketCap")

    # P/E
    pe_ratio = screener.get("pe_ratio")
    if pe_ratio is None:
        pe_ratio = safe_round(yf_info.get("trailingPE"))

    # Book value and PB
    book_value = screener.get("book_value")
    pb_ratio = None
    if book_value and current_price:
        try:
            pb_ratio = safe_round(float(current_price) / float(book_value))
        except Exception:
            pb_ratio = None
    if pb_ratio is None:
        pb_ratio = safe_round(yf_info.get("priceToBook"))

    # EPS from price / PE
    eps = None
    if pe_ratio and current_price:
        try:
            eps = safe_round(float(current_price) / float(pe_ratio))
        except Exception:
            eps = None
    if eps is None:
        eps = safe_round(yf_info.get("trailingEps"))

    # Dividend yield from screener %
    dividend_yield = None
    if screener.get("dividend_yield_pct") is not None:
        try:
            dividend_yield = safe_round(float(screener["dividend_yield_pct"]) / 100, 4)
        except Exception:
            dividend_yield = None
    if dividend_yield is None:
        raw_div = yf_info.get("dividendYield")
        if raw_div is not None:
            dividend_yield = safe_round(raw_div, 4)

    # Beta (still Yahoo fallback only)
    beta = safe_round(yf_info.get("beta"))

    result = {
        "name": fast.get("name") or meta.get("name", symbol),
        "symbol": symbol,
        "sector": sector,
        "peers": peers,

        "current_price": current_price,
        "prev_close": prev_close,
        "change": fast.get("change", "N/A"),
        "change_pct": fast.get("change_pct", "N/A"),

        "day_high": fast.get("day_high"),
        "day_low": fast.get("day_low"),
        "week_52_high": fast.get("week_52_high"),
        "week_52_low": fast.get("week_52_low"),

        "volume": fast.get("volume"),
        "volume_formatted": fast.get("volume_formatted") or format_volume(fast.get("volume")),
        "avg_volume": yf_info.get("averageVolume", "N/A"),

        "market_cap_raw": market_cap_raw,
        "market_cap": format_market_cap(market_cap_raw) if market_cap_raw else "N/A",

        "pe_ratio": pe_ratio if pe_ratio is not None else "N/A",
        "pb_ratio": pb_ratio if pb_ratio is not None else "N/A",
        "dividend_yield": dividend_yield if dividend_yield is not None else "N/A",
        "beta": beta if beta is not None else "N/A",
        "eps": eps if eps is not None else "N/A",

        "exchange": "NSE",
        "currency": "INR",
        "data_source": "yahoo_chart_api + screener"
    }

    set_cache(cache_key, result, ttl_seconds=300)
    return result


def _get_yf_fundamentals(symbol: str) -> dict:
    """
    Optional fallback only
    """
    cache_key = f"yf_fundamentals_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        rate_limit()
        ticker = get_ticker(symbol)
        info = with_retries(lambda: ticker.info) or {}
        set_cache(cache_key, info, ttl_seconds=3600)
        return info
    except Exception as e:
        print(f"[YF FUNDAMENTALS] Error for {symbol}: {e}")
        return {}


def get_historical_returns(symbol: str) -> dict:
    cache_key = f"returns_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    periods = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "5Y": "5y"}
    returns = {}

    for label, period in periods.items():
        try:
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

    set_cache(cache_key, returns, ttl_seconds=43200)
    return returns


def get_chart_data(symbol: str, period: str = "3mo") -> list:
    return get_fast_chart(symbol, period)


def _get_peers_from_sector(sector: str, exclude_symbol: str = "") -> list:
    peers = []
    for stock in NSE_STOCKS:
        if stock.get("sector") == sector and stock.get("symbol") != exclude_symbol:
            peers.append(stock["symbol"])
        if len(peers) >= 6:
            break
    return peers