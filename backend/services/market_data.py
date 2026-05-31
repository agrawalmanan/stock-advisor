from services.stock_mapper import get_stock_meta, NSE_STOCKS
from utils.cache import get_cache, set_cache
from utils.helpers import format_market_cap, format_volume, safe_round, safe_get
from utils.yf_client import get_ticker, with_retries


def get_stock_data(symbol: str) -> dict:
    """
    Fetch full live stock data for a given NSE symbol
    symbol should be like: RELIANCE.NS
    """
    cache_key = f"stock_data_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        def fetch_info():
            ticker = get_ticker(symbol)
            return ticker.info

        info = with_retries(fetch_info)

        if not info or (
            "regularMarketPrice" not in info and
            "currentPrice" not in info
        ):
            return {"error": f"Stock '{symbol}' not found or market closed"}

        meta = get_stock_meta(symbol)

        current_price = safe_get(info, "regularMarketPrice")
        if current_price == "N/A":
            current_price = safe_get(info, "currentPrice")

        prev_close = safe_get(info, "regularMarketPreviousClose")
        if prev_close == "N/A":
            prev_close = safe_get(info, "previousClose")

        change = "N/A"
        change_pct = "N/A"
        if current_price != "N/A" and prev_close != "N/A":
            try:
                change = safe_round(float(current_price) - float(prev_close))
                change_pct = safe_round(
                    ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
                )
            except Exception:
                pass

        sector = info.get("sector") or meta.get("sector", "Unknown")
        peers = meta.get("peers", [])
        if not peers:
            peers = _get_peers_from_sector(sector, exclude_symbol=symbol)

        result = {
            "name": info.get("longName") or meta.get("name", symbol),
            "symbol": symbol,
            "sector": sector,
            "peers": peers,

            "current_price": safe_round(current_price),
            "prev_close": safe_round(prev_close),
            "change": change,
            "change_pct": change_pct,

            "day_high": safe_round(safe_get(info, "dayHigh")),
            "day_low": safe_round(safe_get(info, "dayLow")),

            "week_52_high": safe_round(safe_get(info, "fiftyTwoWeekHigh")),
            "week_52_low": safe_round(safe_get(info, "fiftyTwoWeekLow")),

            "volume": safe_get(info, "regularMarketVolume"),
            "volume_formatted": format_volume(safe_get(info, "regularMarketVolume", default=None)),
            "avg_volume": safe_get(info, "averageVolume"),

            "market_cap_raw": safe_get(info, "marketCap", default=None),
            "market_cap": format_market_cap(safe_get(info, "marketCap", default=None)),

            "pe_ratio": safe_round(safe_get(info, "trailingPE")),
            "pb_ratio": safe_round(safe_get(info, "priceToBook")),
            "dividend_yield": safe_round(safe_get(info, "dividendYield"), 4),
            "beta": safe_round(safe_get(info, "beta")),
            "eps": safe_round(safe_get(info, "trailingEps")),

            "exchange": safe_get(info, "exchange"),
            "currency": safe_get(info, "currency", default="INR"),
        }

        set_cache(cache_key, result, ttl_seconds=1800)  # 30 min
        return result

    except Exception as e:
        msg = str(e)
        if "Too Many Requests" in msg or "rate" in msg.lower() or "429" in msg:
            return {"error": "Too Many Requests. Rate limited. Try after a while."}
        return {"error": f"Failed to fetch data: {msg}"}


def get_historical_returns(symbol: str) -> dict:
    """
    Calculate 1M, 3M, 6M, 1Y, 5Y returns for a stock
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
        ticker = get_ticker(symbol)

        for label, period in periods.items():
            try:
                hist = with_retries(lambda: ticker.history(period=period))
                if hist is None or hist.empty:
                    returns[label] = "N/A"
                    continue

                start_price = hist["Close"].iloc[0]
                end_price = hist["Close"].iloc[-1]
                pct_return = safe_round(((end_price - start_price) / start_price) * 100)
                returns[label] = pct_return
            except Exception:
                returns[label] = "N/A"

        set_cache(cache_key, returns, ttl_seconds=43200)  # 12 hrs
        return returns

    except Exception:
        return {k: "N/A" for k in periods.keys()}


def get_chart_data(symbol: str, period: str = "3mo") -> list:
    """
    Get OHLCV candlestick data for charting
    period: '3mo', '6mo', '1y'
    """
    cache_key = f"chart_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
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

        set_cache(cache_key, candles, ttl_seconds=1800)  # 30 min
        return candles

    except Exception as e:
        print(f"Chart data error for {symbol}: {e}")
        return []


def _get_peers_from_sector(sector: str, exclude_symbol: str = "") -> list:
    """
    Fallback peer finder — finds stocks from same sector in our JSON
    """
    peers = []
    for stock in NSE_STOCKS:
        if stock.get("sector") == sector and stock.get("symbol") != exclude_symbol:
            peers.append(stock["symbol"])
        if len(peers) >= 6:
            break
    return peers