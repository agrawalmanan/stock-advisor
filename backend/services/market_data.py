import yfinance as yf
from services.stock_mapper import get_stock_meta, NSE_STOCKS
from services.nse_client import get_nse_quote
from utils.cache import get_cache, set_cache
from utils.helpers import format_market_cap, format_volume, safe_round, safe_get
from utils.yf_client import get_ticker, with_retries
from utils.rate_limiter import rate_limit


def get_stock_data(symbol: str) -> dict:
    """
    Fetch full live stock data
    Uses NSE API for live price + yfinance for extra fundamentals
    """
    cache_key = f"stock_data_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Normalize symbol
    clean_symbol = symbol.replace(".NS", "").upper()

    # Get stock meta from our JSON
    meta = get_stock_meta(symbol)

    # Step 1: Try NSE API first for live price
    nse_data = get_nse_quote(symbol)

    # Step 2: Get extra fundamentals from yfinance
    yf_info = {}
    try:
        rate_limit()
        ticker = get_ticker(symbol)
        yf_info = with_retries(lambda: ticker.info) or {}
    except Exception as e:
        print(f"[MARKET DATA] yfinance fallback error: {e}")

    # Build result — prefer NSE data, fallback to yfinance
    current_price = nse_data.get("current_price") or safe_round(
        yf_info.get("regularMarketPrice") or yf_info.get("currentPrice")
    )
    prev_close = nse_data.get("prev_close") or safe_round(
        yf_info.get("regularMarketPreviousClose") or yf_info.get("previousClose")
    )

    # Calculate change if not from NSE
    change = nse_data.get("change")
    change_pct = nse_data.get("change_pct")
    if change is None and current_price and prev_close:
        try:
            change = safe_round(float(current_price) - float(prev_close))
            change_pct = safe_round(
                ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
            )
        except Exception:
            change = "N/A"
            change_pct = "N/A"

    # Sector — NSE → yfinance → meta
    sector = (
        nse_data.get("sector") or
        yf_info.get("sector") or
        meta.get("sector", "Unknown")
    )

    # Peers
    peers = meta.get("peers", [])
    if not peers:
        peers = _get_peers_from_sector(sector, exclude_symbol=symbol)

    # Market cap from yfinance (NSE API doesn't give it directly)
    market_cap_raw = yf_info.get("marketCap")

    result = {
        "name": (
            yf_info.get("longName") or
            yf_info.get("shortName") or
            meta.get("name", clean_symbol)
        ),
        "symbol": symbol,
        "sector": sector,
        "peers": peers,

        # Price data (NSE preferred)
        "current_price": current_price,
        "prev_close": prev_close,
        "change": change if change is not None else "N/A",
        "change_pct": change_pct if change_pct is not None else "N/A",

        # Ranges (NSE preferred)
        "day_high": nse_data.get("day_high") or safe_round(yf_info.get("dayHigh")),
        "day_low": nse_data.get("day_low") or safe_round(yf_info.get("dayLow")),
        "week_52_high": nse_data.get("week_52_high") or safe_round(yf_info.get("fiftyTwoWeekHigh")),
        "week_52_low": nse_data.get("week_52_low") or safe_round(yf_info.get("fiftyTwoWeekLow")),

        # Volume (NSE preferred)
        "volume": nse_data.get("volume") or yf_info.get("regularMarketVolume"),
        "volume_formatted": nse_data.get("volume_formatted") or format_volume(yf_info.get("regularMarketVolume")),
        "avg_volume": yf_info.get("averageVolume", "N/A"),

        # Market cap (yfinance)
        "market_cap_raw": market_cap_raw,
        "market_cap": format_market_cap(market_cap_raw),

        # Fundamentals (yfinance)
        "pe_ratio": safe_round(yf_info.get("trailingPE")),
        "pb_ratio": safe_round(yf_info.get("priceToBook")),
        "dividend_yield": safe_round(yf_info.get("dividendYield"), 4),
        "beta": safe_round(yf_info.get("beta")),
        "eps": safe_round(yf_info.get("trailingEps")),

        "exchange": "NSE",
        "currency": "INR",
        "data_source": "NSE + YFinance" if nse_data else "YFinance",
    }

    # If NSE gave us data, use shorter cache
    # If only yfinance, use longer cache to avoid rate limits
    ttl = 180 if nse_data else 900
    set_cache(cache_key, result, ttl_seconds=ttl)
    return result


def get_historical_returns(symbol: str) -> dict:
    """
    Calculate 1M, 3M, 6M, 1Y, 5Y returns
    Uses yfinance — cached for 12 hours to avoid rate limits
    """
    cache_key = f"returns_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    periods = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y",
        "5Y": "5y"
    }

    returns = {}

    try:
        rate_limit()
        ticker = get_ticker(symbol)

        for label, period in periods.items():
            try:
                hist = with_retries(lambda p=period: ticker.history(period=p))
                if hist is None or hist.empty:
                    returns[label] = "N/A"
                    continue
                start_price = hist["Close"].iloc[0]
                end_price = hist["Close"].iloc[-1]
                returns[label] = safe_round(
                    ((end_price - start_price) / start_price) * 100
                )
            except Exception:
                returns[label] = "N/A"

        # Cache 12 hours
        set_cache(cache_key, returns, ttl_seconds=43200)
        return returns

    except Exception as e:
        print(f"[RETURNS] Error for {symbol}: {e}")
        return {k: "N/A" for k in periods.keys()}


def get_chart_data(symbol: str, period: str = "3mo") -> list:
    """
    Get OHLCV candlestick data
    Uses yfinance — cached for 30 min
    """
    cache_key = f"chart_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        rate_limit()
        ticker = get_ticker(symbol)
        hist = with_retries(lambda: ticker.history(period=period, interval="1d"))

        if hist is None or hist.empty:
            return []

        candles = []
        for date, row in hist.iterrows():
            candles.append({
                "time": int(date.timestamp()),
                "open": safe_round(row["Open"]),
                "high": safe_round(row["High"]),
                "low": safe_round(row["Low"]),
                "close": safe_round(row["Close"]),
                "volume": int(row["Volume"]) if row["Volume"] else 0
            })

        # Cache 30 minutes
        set_cache(cache_key, candles, ttl_seconds=1800)
        return candles

    except Exception as e:
        print(f"[CHART] Error for {symbol}: {e}")
        return []


def _get_peers_from_sector(sector: str, exclude_symbol: str = "") -> list:
    """Fallback peer finder from nse_stocks.json"""
    peers = []
    for stock in NSE_STOCKS:
        if stock.get("sector") == sector and stock.get("symbol") != exclude_symbol:
            peers.append(stock["symbol"])
        if len(peers) >= 6:
            break
    return peers