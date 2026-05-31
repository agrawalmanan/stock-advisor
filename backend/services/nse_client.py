import requests
import time
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round, format_volume

YAHOO_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


def get_fast_quote(symbol: str) -> dict:
    """
    Fetch live stock quote using Yahoo Finance chart API
    This endpoint is faster and less rate-limited than yfinance library
    """
    cache_key = f"fast_quote_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Ensure .NS suffix
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "range": "1d",
            "interval": "1d",
        }

        response = requests.get(
            url,
            headers=YAHOO_HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            print(f"[FAST QUOTE] Status {response.status_code} for {symbol}")
            return {}

        data = response.json()
        result_data = data.get("chart", {}).get("result", [])

        if not result_data:
            print(f"[FAST QUOTE] No result for {symbol}")
            return {}

        meta = result_data[0].get("meta", {})

        current_price = meta.get("regularMarketPrice")
        prev_close = meta.get("previousClose") or meta.get("chartPreviousClose")

        change = None
        change_pct = None
        if current_price and prev_close:
            change = safe_round(float(current_price) - float(prev_close))
            change_pct = safe_round(
                ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
            )

        volume = meta.get("regularMarketVolume")

        result = {
            "current_price": safe_round(current_price),
            "prev_close": safe_round(prev_close),
            "change": change,
            "change_pct": change_pct,
            "day_high": safe_round(meta.get("regularMarketDayHigh")),
            "day_low": safe_round(meta.get("regularMarketDayLow")),
            "week_52_high": safe_round(meta.get("fiftyTwoWeekHigh")),
            "week_52_low": safe_round(meta.get("fiftyTwoWeekLow")),
            "volume": volume,
            "volume_formatted": format_volume(volume) if volume else "N/A",
            "name": meta.get("longName") or meta.get("shortName") or symbol,
            "currency": meta.get("currency", "INR"),
            "exchange": meta.get("exchangeName", "NSE"),
            "source": "yahoo_chart_api"
        }

        # Cache 3 minutes
        set_cache(cache_key, result, ttl_seconds=180)
        print(f"[FAST QUOTE] Got {symbol}: ₹{current_price}")
        return result

    except Exception as e:
        print(f"[FAST QUOTE] Error for {symbol}: {e}")
        return {}


def get_fast_chart(symbol: str, period: str = "3mo") -> list:
    """
    Fetch chart data using Yahoo Finance chart API
    Much faster and less rate-limited than yfinance library
    """
    cache_key = f"fast_chart_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    # Map periods
    period_map = {
        "3mo": ("3mo", "1d"),
        "6mo": ("6mo", "1d"),
        "1y": ("1y", "1d"),
    }
    yf_range, interval = period_map.get(period, ("3mo", "1d"))

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "range": yf_range,
            "interval": interval,
        }

        response = requests.get(
            url,
            headers=YAHOO_HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()
        result_data = data.get("chart", {}).get("result", [])

        if not result_data:
            return []

        timestamps = result_data[0].get("timestamp", [])
        quotes = result_data[0].get("indicators", {}).get("quote", [{}])[0]

        opens = quotes.get("open", [])
        highs = quotes.get("high", [])
        lows = quotes.get("low", [])
        closes = quotes.get("close", [])
        volumes = quotes.get("volume", [])

        candles = []
        for i in range(len(timestamps)):
            if closes[i] is None:
                continue
            candles.append({
                "time": timestamps[i],
                "open": safe_round(opens[i]) if opens[i] else 0,
                "high": safe_round(highs[i]) if highs[i] else 0,
                "low": safe_round(lows[i]) if lows[i] else 0,
                "close": safe_round(closes[i]) if closes[i] else 0,
                "volume": int(volumes[i]) if volumes[i] else 0
            })

        # Cache 30 minutes
        set_cache(cache_key, candles, ttl_seconds=1800)
        print(f"[FAST CHART] Got {len(candles)} candles for {symbol} {period}")
        return candles

    except Exception as e:
        print(f"[FAST CHART] Error for {symbol}: {e}")
        return []


def get_fast_history(symbol: str, period: str = "1y") -> list:
    """
    Fetch historical close prices for technical analysis
    Returns list of dicts with date, open, high, low, close, volume
    """
    cache_key = f"fast_history_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "range": period,
            "interval": "1d",
        }

        response = requests.get(
            url,
            headers=YAHOO_HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()
        result_data = data.get("chart", {}).get("result", [])

        if not result_data:
            return []

        timestamps = result_data[0].get("timestamp", [])
        quotes = result_data[0].get("indicators", {}).get("quote", [{}])[0]

        history = []
        for i in range(len(timestamps)):
            close = quotes.get("close", [])[i] if i < len(quotes.get("close", [])) else None
            if close is None:
                continue
            history.append({
                "timestamp": timestamps[i],
                "open": quotes.get("open", [])[i],
                "high": quotes.get("high", [])[i],
                "low": quotes.get("low", [])[i],
                "close": close,
                "volume": quotes.get("volume", [])[i] or 0,
            })

        # Cache 15 minutes
        set_cache(cache_key, history, ttl_seconds=900)
        return history

    except Exception as e:
        print(f"[FAST HISTORY] Error for {symbol}: {e}")
        return []