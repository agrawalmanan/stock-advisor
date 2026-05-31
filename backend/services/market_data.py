import yfinance as yf
from utils.helpers import format_market_cap, format_volume, safe_round, safe_get
from utils.cache import get_cache, set_cache
from services.stock_mapper import get_stock_meta


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
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info or "regularMarketPrice" not in info:
            return {"error": f"Stock '{symbol}' not found or market closed"}

        # get stock meta from our JSON (sector, peers)
        meta = get_stock_meta(symbol)

        # current price — try fast_info first, fall back to info
        current_price = safe_get(info, "regularMarketPrice")
        if current_price == "N/A":
            current_price = safe_get(info, "currentPrice")

        prev_close = safe_get(info, "regularMarketPreviousClose")
        if prev_close == "N/A":
            prev_close = safe_get(info, "previousClose")

        # calculate change
        change = "N/A"
        change_pct = "N/A"
        if current_price != "N/A" and prev_close != "N/A":
            change = safe_round(float(current_price) - float(prev_close))
            change_pct = safe_round(
                ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
            )

        result = {
            "name": meta["name"],
            "symbol": symbol,
            "sector": info.get("sector") or meta["sector"],
            "peers": meta["peers"] if meta["peers"] else _get_peers_from_sector(info.get("sector", "Unknown")),

            # price data
            "current_price": safe_round(current_price),
            "prev_close": safe_round(prev_close),
            "change": change,
            "change_pct": change_pct,

            # day range
            "day_high": safe_round(safe_get(info, "dayHigh")),
            "day_low": safe_round(safe_get(info, "dayLow")),

            # 52 week range
            "week_52_high": safe_round(safe_get(info, "fiftyTwoWeekHigh")),
            "week_52_low": safe_round(safe_get(info, "fiftyTwoWeekLow")),

            # volume
            "volume": safe_get(info, "regularMarketVolume"),
            "volume_formatted": format_volume(safe_get(info, "regularMarketVolume", default=None)),
            "avg_volume": safe_get(info, "averageVolume"),

            # market cap
            "market_cap_raw": safe_get(info, "marketCap", default=None),
            "market_cap": format_market_cap(safe_get(info, "marketCap", default=None)),

            # fundamentals
            "pe_ratio": safe_round(safe_get(info, "trailingPE")),
            "pb_ratio": safe_round(safe_get(info, "priceToBook")),
            "dividend_yield": safe_round(safe_get(info, "dividendYield"), 4),
            "beta": safe_round(safe_get(info, "beta")),
            "eps": safe_round(safe_get(info, "trailingEps")),

            # exchange info
            "exchange": safe_get(info, "exchange"),
            "currency": safe_get(info, "currency", default="INR"),
        }

        # cache for 5 minutes
        set_cache(cache_key, result, ttl_seconds=300)
        return result

    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}


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
    ticker = yf.Ticker(symbol)

    for label, period in periods.items():
        try:
            hist = ticker.history(period=period)
            if hist.empty:
                returns[label] = "N/A"
                continue
            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            pct_return = safe_round(((end_price - start_price) / start_price) * 100)
            returns[label] = pct_return
        except Exception:
            returns[label] = "N/A"

    set_cache(cache_key, returns, ttl_seconds=3600)  # cache 1 hour
    return returns


def get_chart_data(symbol: str, period: str = "3mo") -> list:
    """
    Get OHLCV candlestick data for charting
    period: '3mo' or '6mo'
    Returns list of candles for TradingView Lightweight Charts
    """
    cache_key = f"chart_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval="1d")

        if hist.empty:
            return []

        candles = []
        for date, row in hist.iterrows():
            # TradingView expects time as Unix timestamp
            timestamp = int(date.timestamp())
            candles.append({
                "time": timestamp,
                "open": safe_round(row["Open"]),
                "high": safe_round(row["High"]),
                "low": safe_round(row["Low"]),
                "close": safe_round(row["Close"]),
                "volume": int(row["Volume"]) if row["Volume"] else 0
            })

        set_cache(cache_key, candles, ttl_seconds=300)
        return candles

    except Exception as e:
        print(f"Chart data error: {e}")
        return []
    
def _get_peers_from_sector(sector: str) -> list:
    """
    Fallback peer finder — finds stocks from same sector in our JSON
    """
    from services.stock_mapper import NSE_STOCKS
    peers = []
    for stock in NSE_STOCKS:
        if stock.get("sector") == sector:
            peers.append(stock["symbol"])
        if len(peers) >= 3:
            break
    return peers