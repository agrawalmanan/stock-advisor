
import yfinance as yf
import os
import json
from groq import Groq
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round
from utils.yf_client import get_ticker, with_retries


def get_company_info(symbol: str) -> dict:
    """
    Get comprehensive company information
    Combines yfinance data + Groq AI generated insights
    """
    cache_key = f"company_info_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        ticker = get_ticker(symbol)
        info = with_retries(lambda: ticker.info)

        # Basic info from yfinance
        company_name = info.get("longName") or info.get("shortName") or symbol
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        summary = info.get("longBusinessSummary", "")
        website = info.get("website", "N/A")
        country = info.get("country", "India")
        city = info.get("city", "N/A")
        employees = info.get("fullTimeEmployees", "N/A")

        # Financial highlights from yfinance
        market_cap = info.get("marketCap")
        pe_ratio = safe_round(info.get("trailingPE"))
        pb_ratio = safe_round(info.get("priceToBook"))
        dividend_yield = info.get("dividendYield")
        beta = safe_round(info.get("beta"))
        debt_to_equity = safe_round(info.get("debtToEquity"))
        revenue_growth = safe_round(info.get("revenueGrowth"), 4)
        earnings_growth = safe_round(info.get("earningsGrowth"), 4)
        profit_margins = safe_round(info.get("profitMargins"), 4)
        roe = safe_round(info.get("returnOnEquity"), 4)

        # Promoter / Institutional holdings
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
        except Exception as e:
            print(f"Holdings error for {symbol}: {e}")

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
            "about": ai_about.get("about", summary),
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
                "dividend_yield": f"{safe_round(dividend_yield * 100)}%" if dividend_yield else "N/A",
                "debt_to_equity": debt_to_equity,
                "revenue_growth": f"{safe_round(revenue_growth * 100)}%" if revenue_growth and revenue_growth != "N/A" else "N/A",
                "earnings_growth": f"{safe_round(earnings_growth * 100)}%" if earnings_growth and earnings_growth != "N/A" else "N/A",
                "profit_margins": f"{safe_round(profit_margins * 100)}%" if profit_margins and profit_margins != "N/A" else "N/A",
                "roe": f"{safe_round(roe * 100)}%" if roe and roe != "N/A" else "N/A",
            },

            # AI generated key strengths and risks
            "strengths": ai_about.get("strengths", []),
            "risks": ai_about.get("risks", []),
        }

        # Cache for 24 hours
        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"Company info error for {symbol}: {e}")
        return {
            "name": symbol,
            "symbol": symbol,
            "error": str(e)
        }


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
            "about": summary,
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

        # Clean markdown
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)

        # Cache for 24 hours
        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"AI company details error: {e}")
        return {
            "about": summary,
            "products_services": [],
            "subsidiaries": [],
            "recent_highlights": [],
            "strengths": [],
            "risks": []
        }