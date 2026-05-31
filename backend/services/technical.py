import pandas_ta as ta
import pandas as pd
import yfinance as yf
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round


def get_historical_df(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical OHLCV data as a pandas DataFrame
    Used as base for all technical calculations
    
    Supported periods: 1mo, 3mo, 6mo, 1y, 2y, 5y
    """
    cache_key = f"hist_df_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached is not None:
        # Check if cached value is actually a DataFrame
        if isinstance(cached, pd.DataFrame) and not cached.empty:
            return cached

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval="1d")

        if df is None or df.empty:
            print(f"No data returned from yfinance for {symbol} period={period}")
            return pd.DataFrame()

        # Clean up — keep only required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        available_cols = [c for c in required_cols if c in df.columns]
        
        if not available_cols:
            print(f"Required columns missing for {symbol}")
            return pd.DataFrame()
            
        df = df[available_cols]
        df.dropna(inplace=True)

        if df.empty:
            print(f"DataFrame empty after cleanup for {symbol}")
            return pd.DataFrame()

        print(f"Fetched {len(df)} rows for {symbol} period={period}")
        set_cache(cache_key, df, ttl_seconds=300)
        return df

    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def calculate_moving_averages(df: pd.DataFrame) -> dict:
    """
    Calculate SMA and EMA using full historical dataset
    so 100/200 day averages can be computed properly.
    """
    if df.empty:
        return {}

    close = df["Close"]
    result = {}

    current_price = safe_round(close.iloc[-1])

    # Simple Moving Averages
    for period in [20, 50, 100, 200]:
        try:
            if len(close) < period:
                result[f"sma_{period}"] = {
                    "value": "N/A",
                    "signal": "N/A",
                    "label": f"SMA {period}"
                }
                continue

            sma = ta.sma(close, length=period)

            if sma is not None and not sma.empty and pd.notna(sma.iloc[-1]):
                value = safe_round(sma.iloc[-1])

                if value != "N/A" and current_price != "N/A":
                    signal = "Above" if float(current_price) > float(value) else "Below"
                else:
                    signal = "N/A"

                result[f"sma_{period}"] = {
                    "value": value,
                    "signal": signal,
                    "label": f"SMA {period}"
                }
            else:
                result[f"sma_{period}"] = {
                    "value": "N/A",
                    "signal": "N/A",
                    "label": f"SMA {period}"
                }

        except Exception as e:
            print(f"SMA {period} error: {e}")
            result[f"sma_{period}"] = {
                "value": "N/A",
                "signal": "N/A",
                "label": f"SMA {period}"
            }

    # Exponential Moving Averages
    for period in [20, 50, 100, 200]:
        try:
            if len(close) < period:
                result[f"ema_{period}"] = {
                    "value": "N/A",
                    "signal": "N/A",
                    "label": f"EMA {period}"
                }
                continue

            ema = ta.ema(close, length=period)

            if ema is not None and not ema.empty and pd.notna(ema.iloc[-1]):
                value = safe_round(ema.iloc[-1])

                if value != "N/A" and current_price != "N/A":
                    signal = "Above" if float(current_price) > float(value) else "Below"
                else:
                    signal = "N/A"

                result[f"ema_{period}"] = {
                    "value": value,
                    "signal": signal,
                    "label": f"EMA {period}"
                }
            else:
                result[f"ema_{period}"] = {
                    "value": "N/A",
                    "signal": "N/A",
                    "label": f"EMA {period}"
                }

        except Exception as e:
            print(f"EMA {period} error: {e}")
            result[f"ema_{period}"] = {
                "value": "N/A",
                "signal": "N/A",
                "label": f"EMA {period}"
            }

    return result

def calculate_rsi(df: pd.DataFrame) -> dict:
    """
    Calculate RSI (14 period)
    RSI > 70 = Overbought (potential sell)
    RSI < 30 = Oversold (potential buy)
    """
    if df.empty:
        return {"value": "N/A", "signal": "N/A"}

    try:
        rsi = ta.rsi(df["Close"], length=14)
        if rsi is None or rsi.empty:
            return {"value": "N/A", "signal": "N/A"}

        value = safe_round(rsi.iloc[-1])

        # Determine signal
        if value == "N/A":
            signal = "N/A"
        elif float(value) >= 70:
            signal = "Overbought"
        elif float(value) <= 30:
            signal = "Oversold"
        elif float(value) >= 55:
            signal = "Bullish"
        elif float(value) <= 45:
            signal = "Bearish"
        else:
            signal = "Neutral"

        return {
            "value": value,
            "signal": signal,
            "description": f"RSI at {value} indicates {signal} momentum"
        }

    except Exception as e:
        print(f"RSI error: {e}")
        return {"value": "N/A", "signal": "N/A"}


def calculate_macd(df: pd.DataFrame) -> dict:
    """
    Calculate MACD (12, 26, 9)
    MACD line > Signal line = Bullish
    MACD line < Signal line = Bearish
    """
    if df.empty:
        return {"macd": "N/A", "signal": "N/A", "histogram": "N/A", "trend": "N/A"}

    try:
        macd_df = ta.macd(df["Close"], fast=12, slow=26, signal=9)

        if macd_df is None or macd_df.empty:
            return {"macd": "N/A", "signal": "N/A", "histogram": "N/A", "trend": "N/A"}

        # pandas_ta returns columns: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        macd_col = [c for c in macd_df.columns if c.startswith("MACD_")]
        signal_col = [c for c in macd_df.columns if c.startswith("MACDs_")]
        hist_col = [c for c in macd_df.columns if c.startswith("MACDh_")]

        macd_val = safe_round(macd_df[macd_col[0]].iloc[-1]) if macd_col else "N/A"
        signal_val = safe_round(macd_df[signal_col[0]].iloc[-1]) if signal_col else "N/A"
        hist_val = safe_round(macd_df[hist_col[0]].iloc[-1]) if hist_col else "N/A"

        # Determine trend
        if macd_val != "N/A" and signal_val != "N/A":
            if float(macd_val) > float(signal_val):
                trend = "Bullish"
            else:
                trend = "Bearish"
        else:
            trend = "N/A"

        return {
            "macd": macd_val,
            "signal": signal_val,
            "histogram": hist_val,
            "trend": trend,
            "description": f"MACD is {trend} — MACD line {'above' if trend == 'Bullish' else 'below'} signal line"
        }

    except Exception as e:
        print(f"MACD error: {e}")
        return {"macd": "N/A", "signal": "N/A", "histogram": "N/A", "trend": "N/A"}


def calculate_bollinger_bands(df: pd.DataFrame) -> dict:
    """
    Calculate Bollinger Bands (20 period, 2 std dev)
    Price near upper band = Overbought
    Price near lower band = Oversold
    """
    if df.empty:
        return {"upper": "N/A", "middle": "N/A", "lower": "N/A", "signal": "N/A"}

    try:
        bb = ta.bbands(df["Close"], length=20, std=2)

        if bb is None or bb.empty:
            return {"upper": "N/A", "middle": "N/A", "lower": "N/A", "signal": "N/A"}

        upper_col = [c for c in bb.columns if "BBU" in c]
        middle_col = [c for c in bb.columns if "BBM" in c]
        lower_col = [c for c in bb.columns if "BBL" in c]

        upper = safe_round(bb[upper_col[0]].iloc[-1]) if upper_col else "N/A"
        middle = safe_round(bb[middle_col[0]].iloc[-1]) if middle_col else "N/A"
        lower = safe_round(bb[lower_col[0]].iloc[-1]) if lower_col else "N/A"

        current_price = safe_round(df["Close"].iloc[-1])

        # Determine signal
        signal = "N/A"
        if upper != "N/A" and lower != "N/A" and current_price != "N/A":
            price = float(current_price)
            up = float(upper)
            lo = float(lower)
            band_range = up - lo

            if band_range > 0:
                position = (price - lo) / band_range
                if position >= 0.8:
                    signal = "Overbought"
                elif position <= 0.2:
                    signal = "Oversold"
                else:
                    signal = "Neutral"

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "signal": signal,
            "current_price": current_price,
            "description": f"Price is {signal} relative to Bollinger Bands"
        }

    except Exception as e:
        print(f"Bollinger Bands error: {e}")
        return {"upper": "N/A", "middle": "N/A", "lower": "N/A", "signal": "N/A"}


def calculate_support_resistance(df: pd.DataFrame) -> dict:
    """
    Calculate Support and Resistance levels
    Method: Pivot points from recent price action
    Finds local minima (support) and maxima (resistance)
    """
    if df.empty or len(df) < 20:
        return {"support": [], "resistance": []}

    try:
        close = df["Close"].values
        high = df["High"].values
        low = df["Low"].values

        support_levels = []
        resistance_levels = []

        # Find local minima and maxima using a window of 5 candles
        window = 5
        for i in range(window, len(close) - window):
            # Local minimum = support
            if low[i] == min(low[i - window:i + window + 1]):
                support_levels.append(safe_round(low[i]))

            # Local maximum = resistance
            if high[i] == max(high[i - window:i + window + 1]):
                resistance_levels.append(safe_round(high[i]))

        current_price = float(close[-1])

        # Filter: support = below current price, resistance = above
        support_levels = sorted(
            [s for s in support_levels if isinstance(s, float) and s < current_price],
            reverse=True  # closest support first
        )
        resistance_levels = sorted(
            [r for r in resistance_levels if isinstance(r, float) and r > current_price]
            # closest resistance first
        )

        # Remove duplicates that are too close (within 0.5%)
        def deduplicate(levels, threshold=0.005):
            if not levels:
                return []
            deduped = [levels[0]]
            for level in levels[1:]:
                if abs(level - deduped[-1]) / deduped[-1] > threshold:
                    deduped.append(level)
            return deduped

        support_levels = deduplicate(support_levels)[:3]   # top 3
        resistance_levels = deduplicate(resistance_levels)[:3]  # top 3

        return {
            "support": support_levels,
            "resistance": resistance_levels,
            "current_price": safe_round(current_price)
        }

    except Exception as e:
        print(f"Support/Resistance error: {e}")
        return {"support": [], "resistance": []}


def calculate_overall_trend(
    moving_averages: dict,
    rsi: dict,
    macd: dict
) -> dict:
    """
    Determine overall trend from all indicators combined
    """
    bullish_count = 0
    bearish_count = 0
    total = 0

    # Check MAs — how many is price above?
    for key, ma in moving_averages.items():
        signal = ma.get("signal", "N/A")
        if signal == "Above":
            bullish_count += 1
        elif signal == "Below":
            bearish_count += 1
        total += 1

    # Check RSI
    rsi_signal = rsi.get("signal", "N/A")
    if rsi_signal in ["Bullish", "Overbought"]:
        bullish_count += 1
    elif rsi_signal in ["Bearish", "Oversold"]:
        bearish_count += 1
    total += 1

    # Check MACD
    macd_trend = macd.get("trend", "N/A")
    if macd_trend == "Bullish":
        bullish_count += 1
    elif macd_trend == "Bearish":
        bearish_count += 1
    total += 1

    # Avoid division by zero
    if total == 0:
        return {"trend": "Neutral", "score": 50, "color": "yellow"}

    bull_pct = round((bullish_count / total) * 100, 2)

    if bull_pct >= 65:
        trend = "Bullish"
        color = "green"
    elif bull_pct <= 35:
        trend = "Bearish"
        color = "red"
    else:
        trend = "Neutral"
        color = "yellow"

    return {
        "trend": trend,
        "score": bull_pct,
        "bullish_indicators": bullish_count,
        "bearish_indicators": bearish_count,
        "total_indicators": total,
        "color": color
    }

def slice_df_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Slice dataframe to selected display period
    """
    if df.empty:
        return df

    last_date = df.index[-1]

    if period == "3mo":
        cutoff = last_date - pd.DateOffset(days=90)
        return df[df.index >= cutoff]

    if period == "6mo":
        cutoff = last_date - pd.DateOffset(days=180)
        return df[df.index >= cutoff]

    if period == "1y":
        cutoff = last_date - pd.DateOffset(days=365)
        return df[df.index >= cutoff]

    return df

def get_full_analysis(symbol: str, period: str = "3mo") -> dict:
    """
    Master function — runs all technical analysis

    Important:
    - Indicators like SMA/EMA/RSI/MACD/Bollinger are calculated using 1 year data
      for better accuracy.
    - Support/Resistance uses selected display period (3mo or 6mo).
    """
    cache_key = f"analysis_v2_{symbol}_{period}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Use 1 year data as base for technical indicators
    df_base = get_historical_df(symbol, period="1y")

    if df_base.empty:
        return {"error": f"No historical data found for {symbol}"}

    # Display-specific slice for support/resistance and period context
    df_display = slice_df_by_period(df_base, period)

    if df_display.empty:
        df_display = df_base

    # Indicators from full 1Y base data
    moving_averages = calculate_moving_averages(df_base)
    rsi = calculate_rsi(df_base)
    macd = calculate_macd(df_base)
    bollinger = calculate_bollinger_bands(df_base)

    # Support/Resistance from selected display window
    support_resistance = calculate_support_resistance(df_display)

    # Trend from full indicator set
    trend = calculate_overall_trend(moving_averages, rsi, macd)

    result = {
        "symbol": symbol,
        "period": period,
        "indicator_basis": "1y",
        "display_basis": period,
        "moving_averages": moving_averages,
        "rsi": rsi,
        "macd": macd,
        "bollinger_bands": bollinger,
        "support_resistance": support_resistance,
        "trend": trend
    }

    set_cache(cache_key, result, ttl_seconds=300)
    return result