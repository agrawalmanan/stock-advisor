import os
import json
from groq import Groq
from utils.cache import get_cache, set_cache


def get_ai_advice(
    symbol: str,
    company_name: str,
    sector: str,
    current_price: float,
    change_pct: float,
    rsi: dict,
    macd: dict,
    trend: dict,
    support_resistance: dict,
    historical_returns: dict,
    news_headlines: list,
    risk: dict,
    moving_averages: dict
) -> dict:
    """
    Use Groq AI (Llama) to generate Buy/Sell/Hold advice
    with reasoning based on technical data + news
    """
    cache_key = f"advice_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "action": "HOLD",
            "confidence": 50,
            "reasons": ["AI advisor unavailable — GROQ_API_KEY not set"],
            "summary": "Unable to generate AI advice at this time"
        }

    client = Groq(api_key=api_key)

    # Build news summary for prompt
    news_summary = ""
    if news_headlines:
        news_summary = "\n".join([
            f"- {article['title']} ({article['source']})"
            for article in news_headlines[:4]
        ])
    else:
        news_summary = "No recent news available"

    # Build MA summary
    ma_summary = ""
    for key, ma in moving_averages.items():
        ma_summary += f"  {ma['label']}: {ma['value']} (Price is {ma['signal']})\n"

    # Build the prompt
    prompt = f"""
You are an expert Indian stock market analyst. Analyze the following data for {company_name} ({symbol}) 
and provide a clear BUY, SELL, or HOLD recommendation.

=== STOCK DATA ===
Company: {company_name}
Symbol: {symbol}
Sector: {sector}
Current Price: ₹{current_price}
Today's Change: {change_pct}%
Risk Level: {risk.get('level', 'N/A')}

=== TECHNICAL INDICATORS ===
Overall Trend: {trend.get('trend', 'N/A')} (Score: {trend.get('score', 'N/A')}/100)
RSI (14): {rsi.get('value', 'N/A')} → {rsi.get('signal', 'N/A')}
MACD Trend: {macd.get('trend', 'N/A')} (MACD: {macd.get('macd', 'N/A')}, Signal: {macd.get('signal', 'N/A')})

Moving Averages:
{ma_summary}

Support Levels: {support_resistance.get('support', [])}
Resistance Levels: {support_resistance.get('resistance', [])}

=== HISTORICAL RETURNS ===
1 Month: {historical_returns.get('1M', 'N/A')}%
3 Months: {historical_returns.get('3M', 'N/A')}%
6 Months: {historical_returns.get('6M', 'N/A')}%
1 Year: {historical_returns.get('1Y', 'N/A')}%
5 Years: {historical_returns.get('5Y', 'N/A')}%

=== RECENT NEWS ===
{news_summary}

=== YOUR TASK ===
Based on ALL the above data, provide your analysis in the following JSON format ONLY.
Do not write anything outside the JSON. Return valid JSON only.

{{
  "action": "BUY" or "SELL" or "HOLD",
  "confidence": <number between 50 and 95>,
  "summary": "<one sentence overall summary of the stock situation>",
  "reasons": [
    "<specific reason 1 with actual data points from above>",
    "<specific reason 2 with actual data points from above>",
    "<specific reason 3 with actual data points from above>",
    "<specific reason 4 referencing news or returns>"
  ],
  "entry_point": <suggested entry price as number, based on support levels>,
  "exit_point": <suggested exit price as number, based on resistance levels>,
  "stop_loss": <suggested stop loss price as number, slightly below nearest support>
}}

Rules:
- Use ACTUAL numbers from the data provided
- Reference specific indicators (RSI value, MACD direction, MA levels)
- Mention relevant news if available
- Entry point should be near or at support levels
- Exit point should be near resistance levels
- Stop loss should be 2-3% below nearest support
- Be specific and data-driven, not generic
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian stock market technical analyst. Always respond with valid JSON only. No markdown, no explanation outside JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # lower = more consistent, factual
            max_tokens=1000
        )

        raw_response = response.choices[0].message.content.strip()

        # Clean up response in case AI adds markdown
        if "```json" in raw_response:
            raw_response = raw_response.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_response:
            raw_response = raw_response.split("```")[1].split("```")[0].strip()

        advice = json.loads(raw_response)

        # Validate required fields
        required_fields = ["action", "confidence", "reasons", "summary"]
        for field in required_fields:
            if field not in advice:
                raise ValueError(f"Missing field: {field}")

        # Validate action
        if advice["action"] not in ["BUY", "SELL", "HOLD"]:
            advice["action"] = "HOLD"

        # Validate confidence range
        confidence = int(advice.get("confidence", 50))
        advice["confidence"] = max(50, min(95, confidence))

        # Cache for 1 hour
        set_cache(cache_key, advice, ttl_seconds=3600)
        return advice

    except json.JSONDecodeError as e:
        print(f"Groq JSON parse error: {e}")
        print(f"Raw response: {raw_response}")
        return _fallback_advice(trend, rsi, macd)

    except Exception as e:
        print(f"Groq API error: {e}")
        return _fallback_advice(trend, rsi, macd)


def _fallback_advice(trend: dict, rsi: dict, macd: dict) -> dict:
    """
    Rule-based fallback if Groq API fails
    Uses technical indicators to make a basic recommendation
    """
    score = trend.get("score", 50)

    if score >= 65:
        action = "BUY"
        confidence = 60
    elif score <= 35:
        action = "SELL"
        confidence = 60
    else:
        action = "HOLD"
        confidence = 55

    reasons = [
        f"Overall trend score is {score}/100 indicating {trend.get('trend', 'Neutral')} momentum",
        f"RSI at {rsi.get('value', 'N/A')} shows {rsi.get('signal', 'N/A')} conditions",
        f"MACD is {macd.get('trend', 'N/A')} — {'bullish crossover' if macd.get('trend') == 'Bullish' else 'bearish crossover'}",
        "AI advisor temporarily unavailable — this is a rule-based recommendation"
    ]

    return {
        "action": action,
        "confidence": confidence,
        "summary": f"Rule-based analysis suggests {action} based on technical indicators",
        "reasons": reasons,
        "entry_point": "N/A",
        "exit_point": "N/A",
        "stop_loss": "N/A"
    }