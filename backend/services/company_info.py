import os
import json
from groq import Groq
from services.nse_client import get_fast_quote, get_fast_fundamentals
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round


def get_company_info(symbol: str) -> dict:
    """
    Get comprehensive company information
    Uses fast Yahoo APIs + Groq AI generated insights
    """
    cache_key = f"company_info_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        # Get basic info from fast APIs (no rate limit issues)
        fast_quote = get_fast_quote(symbol)
        fundamentals = get_fast_fundamentals(symbol)

        company_name = (
            fast_quote.get("name") or
            fundamentals.get("name") or
            symbol.replace(".NS", "")
        )
        sector = fundamentals.get("sector") or "Unknown"
        industry = fundamentals.get("industry") or "Unknown"

        # Try to get extra info from yfinance (cached 24 hrs)
        yf_extra = _get_yf_extra_info(symbol)

        summary = yf_extra.get("summary", "")
        website = yf_extra.get("website", "N/A")
        city = yf_extra.get("city", "N/A")
        country = yf_extra.get("country", "India")
        employees = yf_extra.get("employees", "N/A")

        # Use sector/industry from yfinance if fast API didn't have it
        if sector == "Unknown":
            sector = yf_extra.get("sector", "Unknown")
        if industry == "Unknown":
            industry = yf_extra.get("industry", "Unknown")

        # Financial highlights
        pe_ratio = fundamentals.get("pe_ratio") or safe_round(yf_extra.get("trailingPE"))
        pb_ratio = fundamentals.get("pb_ratio") or safe_round(yf_extra.get("priceToBook"))
        beta = fundamentals.get("beta") or safe_round(yf_extra.get("beta"))
        dividend_yield = fundamentals.get("dividend_yield")
        debt_to_equity = safe_round(yf_extra.get("debtToEquity"))
        revenue_growth = safe_round(yf_extra.get("revenueGrowth"), 4)
        earnings_growth = safe_round(yf_extra.get("earningsGrowth"), 4)
        profit_margins = safe_round(yf_extra.get("profitMargins"), 4)
        roe = safe_round(yf_extra.get("returnOnEquity"), 4)

        # Holdings
        promoter_holding = yf_extra.get("promoter_holding", "N/A")
        fii_holding = yf_extra.get("fii_holding", "N/A")
        dii_holding = yf_extra.get("dii_holding", "N/A")

        # Get AI-generated detailed info
        ai_about = get_ai_company_details(company_name, sector, industry, summary)

        result = {
            "name": company_name,
            "symbol": symbol,
            "sector": sector,
            "industry": industry,
            "summary": summary,
            "website": website,
            "country": country,
            "city": city,
            "employees": employees,

            # AI generated
            "about": ai_about.get("about", summary or f"{company_name} is a company listed on NSE India."),
            "products_services": ai_about.get("products_services", []),
            "subsidiaries": ai_about.get("subsidiaries", []),
            "recent_highlights": ai_about.get("recent_highlights", []),

            # Key Points
            "key_points": {
                "promoter_holding": promoter_holding,
                "fii_holding": fii_holding,
                "dii_holding": dii_holding,
                "pe_ratio": pe_ratio,
                "pb_ratio": pb_ratio,
                "beta": beta,
                "dividend_yield": f"{safe_round(float(dividend_yield) * 100)}%" if dividend_yield and dividend_yield != "N/A" else "N/A",
                "debt_to_equity": debt_to_equity,
                "revenue_growth": f"{safe_round(float(revenue_growth) * 100)}%" if revenue_growth and revenue_growth != "N/A" else "N/A",
                "earnings_growth": f"{safe_round(float(earnings_growth) * 100)}%" if earnings_growth and earnings_growth != "N/A" else "N/A",
                "profit_margins": f"{safe_round(float(profit_margins) * 100)}%" if profit_margins and profit_margins != "N/A" else "N/A",
                "roe": f"{safe_round(float(roe) * 100)}%" if roe and roe != "N/A" else "N/A",
            },

            # AI generated strengths and risks
            "strengths": ai_about.get("strengths", []),
            "risks": ai_about.get("risks", []),
        }

        # Cache for 24 hours
        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"Company info error for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "name": symbol.replace(".NS", ""),
            "symbol": symbol,
            "error": str(e)
        }


def _get_yf_extra_info(symbol: str) -> dict:
    """
    Get extra info from yfinance — heavily cached (24 hrs)
    This is the only place we use yfinance library for company info
    If it fails, we just skip — no crash
    """
    cache_key = f"yf_extra_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        from utils.yf_client import get_ticker, with_retries
        from utils.rate_limiter import rate_limit

        rate_limit()
        ticker = get_ticker(symbol)
        info = with_retries(lambda: ticker.info) or {}

        # Extract holdings
        promoter_holding = "N/A"
        fii_holding = "N/A"
        dii_holding = "N/A"

        try:
            holders = ticker.major_holders
            if holders is not None and not holders.empty:
                for _, row in holders.iterrows():
                    label = str(row.iloc[1]).lower() if len(row) > 1 else ""
                    value = row.iloc[0]
                    if "insider" in label or "promoter" in label:
                        promoter_holding = safe_round(float(str(value).replace('%', '')))
                    elif "institution" in label:
                        fii_holding = safe_round(float(str(value).replace('%', '')))
        except Exception:
            pass

        result = {
            "summary": info.get("longBusinessSummary", ""),
            "website": info.get("website", "N/A"),
            "city": info.get("city", "N/A"),
            "country": info.get("country", "India"),
            "employees": info.get("fullTimeEmployees", "N/A"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "trailingPE": info.get("trailingPE"),
            "priceToBook": info.get("priceToBook"),
            "beta": info.get("beta"),
            "debtToEquity": info.get("debtToEquity"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "profitMargins": info.get("profitMargins"),
            "returnOnEquity": info.get("returnOnEquity"),
            "promoter_holding": promoter_holding,
            "fii_holding": fii_holding,
            "dii_holding": dii_holding,
        }

        # Cache 24 hours
        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"[YF EXTRA] Error for {symbol}: {e}")
        # Return empty — don't crash
        empty = {
            "summary": "",
            "website": "N/A",
            "city": "N/A",
            "country": "India",
            "employees": "N/A",
            "sector": None,
            "industry": None,
            "promoter_holding": "N/A",
            "fii_holding": "N/A",
            "dii_holding": "N/A",
        }
        # Cache empty result for 1 hour so we don't keep retrying
        set_cache(cache_key, empty, ttl_seconds=3600)
        return empty


def get_ai_company_details(company_name: str, sector: str, industry: str, summary: str) -> dict:
    """
    Use Groq AI to generate detailed company information
    """
    cache_key = f"ai_company_{company_name}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "about": summary or f"{company_name} is a company listed on NSE India.",
            "products_services": [],
            "subsidiaries": [],
            "recent_highlights": [],
            "strengths": [],
            "risks": []
        }

    client = Groq(api_key=api_key)

    prompt = f"""
You are a financial analyst. Provide detailed information about {company_name} (Indian stock market company).
Sector: {sector}, Industry: {industry}

Company summary from records: {summary[:500] if summary else 'Not available'}

Return valid JSON only with this exact structure:
{{
    "about": "<2-3 paragraph description of what the company does, its history, and current position in the market. Keep it around 150-200 words.>",
    "products_services": [
        "<product/service 1>",
        "<product/service 2>",
        "<product/service 3>",
        "<product/service 4>",
        "<product/service 5>"
    ],
    "subsidiaries": [
        "<subsidiary/brand 1>",
        "<subsidiary/brand 2>",
        "<subsidiary/brand 3>",
        "<subsidiary/brand 4>"
    ],
    "recent_highlights": [
        "<recent highlight or achievement 1>",
        "<recent highlight or achievement 2>",
        "<recent highlight or achievement 3>"
    ],
    "strengths": [
        "<key strength 1>",
        "<key strength 2>",
        "<key strength 3>"
    ],
    "risks": [
        "<key risk 1>",
        "<key risk 2>",
        "<key risk 3>"
    ]
}}

Rules:
- Use factual, accurate information only
- Focus on Indian market context
- Be specific, not generic
- Return valid JSON only, no markdown
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Always respond with valid JSON only."
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

        result = json.loads(raw)
        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"AI company details error: {e}")
        return {
            "about": summary or f"{company_name} is a company listed on NSE India in the {sector} sector.",
            "products_services": [],
            "subsidiaries": [],
            "recent_highlights": [],
            "strengths": [],
            "risks": []
        }