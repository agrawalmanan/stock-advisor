import os
import json
from groq import Groq
from utils.cache import get_cache, set_cache


def get_indicator_interpretation(symbol: str, analysis: dict) -> dict:
    """
    Generate AI interpretation of all technical indicators
    specific to this stock's current data
    """
    cache_key = f"interpret_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Build static explanations
    static = get_static_explanations()

    # Build dynamic AI interpretation
    dynamic = get_ai_interpretation(symbol, analysis)

    result = {
        "symbol": symbol,
        "static": static,
        "dynamic": dynamic
    }

    set_cache(cache_key, result, ttl_seconds=3600)
    return result


def get_static_explanations() -> dict:
    """
    Static educational content about each indicator
    """
    return {
        "sma": {
            "title": "Simple Moving Average (SMA)",
            "what": "SMA calculates the average closing price over a specific number of days. For example, SMA 20 is the average of the last 20 days' closing prices.",
            "how_to_read": [
                "Price ABOVE SMA → Bullish signal (uptrend)",
                "Price BELOW SMA → Bearish signal (downtrend)",
                "SMA 20 & 50 → Short-term trend",
                "SMA 100 & 200 → Long-term trend",
                "Golden Cross: SMA 50 crosses above SMA 200 → Strong buy signal",
                "Death Cross: SMA 50 crosses below SMA 200 → Strong sell signal"
            ]
        },
        "ema": {
            "title": "Exponential Moving Average (EMA)",
            "what": "EMA is similar to SMA but gives more weight to recent prices, making it react faster to price changes. It's more responsive than SMA.",
            "how_to_read": [
                "Price ABOVE EMA → Bullish momentum",
                "Price BELOW EMA → Bearish momentum",
                "EMA reacts faster than SMA to recent price changes",
                "Short-term traders prefer EMA over SMA",
                "EMA 20 crossing above EMA 50 → Buy signal",
                "EMA 20 crossing below EMA 50 → Sell signal"
            ]
        },
        "rsi": {
            "title": "Relative Strength Index (RSI)",
            "what": "RSI measures the speed and magnitude of price changes on a scale of 0 to 100. It helps identify if a stock is overbought or oversold.",
            "how_to_read": [
                "RSI > 70 → Overbought (stock may be overvalued, potential sell)",
                "RSI < 30 → Oversold (stock may be undervalued, potential buy)",
                "RSI 40-60 → Neutral zone",
                "RSI trending up → Increasing bullish momentum",
                "RSI trending down → Increasing bearish momentum",
                "Divergence: Price makes new high but RSI doesn't → Potential reversal"
            ]
        },
        "macd": {
            "title": "MACD (Moving Average Convergence Divergence)",
            "what": "MACD shows the relationship between two EMAs (12-day and 26-day). It consists of the MACD line, Signal line, and Histogram. It helps identify trend direction and momentum.",
            "how_to_read": [
                "MACD line ABOVE signal line → Bullish (buy signal)",
                "MACD line BELOW signal line → Bearish (sell signal)",
                "Histogram positive & growing → Strong bullish momentum",
                "Histogram negative & growing → Strong bearish momentum",
                "MACD crossing above zero → Bullish trend confirmation",
                "MACD crossing below zero → Bearish trend confirmation"
            ]
        },
        "bollinger": {
            "title": "Bollinger Bands",
            "what": "Bollinger Bands consist of a middle band (SMA 20) and two outer bands at 2 standard deviations. They measure volatility and identify overbought/oversold conditions.",
            "how_to_read": [
                "Price near UPPER band → Overbought (may fall)",
                "Price near LOWER band → Oversold (may rise)",
                "Price at MIDDLE band → Neutral",
                "Bands WIDENING → High volatility",
                "Bands NARROWING → Low volatility (breakout coming)",
                "Price breaking outside bands → Strong momentum move"
            ]
        },
        "support_resistance": {
            "title": "Support & Resistance Levels",
            "what": "Support is a price level where buying pressure prevents further decline. Resistance is a price level where selling pressure prevents further rise. These are key levels for entry/exit decisions.",
            "how_to_read": [
                "Price approaching SUPPORT → Potential bounce (buy opportunity)",
                "Price breaking BELOW support → Bearish breakdown (sell signal)",
                "Price approaching RESISTANCE → Potential rejection (sell opportunity)",
                "Price breaking ABOVE resistance → Bullish breakout (buy signal)",
                "S1 is nearest support, S3 is strongest",
                "R1 is nearest resistance, R3 is strongest"
            ]
        }
    }


def get_ai_interpretation(symbol: str, analysis: dict) -> dict:
    """
    Use Groq AI to generate stock-specific interpretation
    of current indicator values
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "AI interpretation unavailable"}

    client = Groq(api_key=api_key)

    # Build data summary
    mas = analysis.get("moving_averages", {})
    rsi = analysis.get("rsi", {})
    macd = analysis.get("macd", {})
    bb = analysis.get("bollinger_bands", {})
    sr = analysis.get("support_resistance", {})
    trend = analysis.get("trend", {})

    ma_text = "\n".join([
        f"  {v['label']}: {v['value']} (Price is {v['signal']})"
        for k, v in mas.items()
    ])

    prompt = f"""
You are a stock market educator. Explain what the current technical indicators mean for {symbol} in simple English that a beginner can understand.

Current Data:
Moving Averages:
{ma_text}

RSI (14): {rsi.get('value', 'N/A')} → {rsi.get('signal', 'N/A')}
MACD: {macd.get('macd', 'N/A')} (Signal: {macd.get('signal', 'N/A')}) → {macd.get('trend', 'N/A')}
Bollinger Bands: Upper={bb.get('upper', 'N/A')}, Middle={bb.get('middle', 'N/A')}, Lower={bb.get('lower', 'N/A')} → {bb.get('signal', 'N/A')}
Support Levels: {sr.get('support', [])}
Resistance Levels: {sr.get('resistance', [])}
Current Price: {sr.get('current_price', 'N/A')}
Overall Trend: {trend.get('trend', 'N/A')} (Score: {trend.get('score', 'N/A')}/100)

Return valid JSON only:
{{
    "sma_interpretation": "<what the SMA values specifically mean for this stock right now, 2-3 sentences>",
    "ema_interpretation": "<what the EMA values specifically mean for this stock right now, 2-3 sentences>",
    "rsi_interpretation": "<what the RSI value specifically means, is it overbought/oversold, what should investor do, 2-3 sentences>",
    "macd_interpretation": "<what the MACD values mean, is momentum building or fading, 2-3 sentences>",
    "bollinger_interpretation": "<what the Bollinger Band position means, is volatility high/low, 2-3 sentences>",
    "support_resistance_interpretation": "<what the S/R levels mean for entry/exit, where are key levels, 2-3 sentences>",
    "overall_summary": "<overall summary of what all indicators together suggest, 3-4 sentences>"
}}

Rules:
- Use actual numbers from the data
- Explain in simple English a beginner can understand
- Be specific to this stock, not generic
- Return valid JSON only
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a stock market educator. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )

        raw = response.choices[0].message.content.strip()

        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        return json.loads(raw)

    except Exception as e:
        print(f"AI interpretation error: {e}")
        return {
            "overall_summary": "AI interpretation temporarily unavailable. Please refer to the static explanations for each indicator."
        }