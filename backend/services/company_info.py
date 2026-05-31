import os
import json
from groq import Groq
from services.nse_client import get_fast_quote, get_fast_fundamentals
from services.screener_client import get_screener_data
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round


def get_company_info(symbol: str) -> dict:
    cache_key = f"company_info_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        fast_quote = get_fast_quote(symbol)
        screener = get_screener_data(symbol)

        company_name = fast_quote.get("name") or symbol.replace(".NS", "")
        sector = screener.get("sector") or "Unknown"
        industry = screener.get("industry") or "Unknown"

        yf_extra = _get_yf_extra_info(symbol)
        summary = yf_extra.get("summary", "")
        website = yf_extra.get("website", "N/A")
        city = yf_extra.get("city", "N/A")
        country = yf_extra.get("country", "India")
        employees = yf_extra.get("employees", "N/A")

        if sector == "Unknown":
            sector = yf_extra.get("sector") or "Unknown"
        if industry == "Unknown":
            industry = yf_extra.get("industry") or "Unknown"

        ai_about = get_ai_company_details(company_name, sector, industry, summary)

        # Build key points from screener + yfinance
        promoter = screener.get("promoter_holding")
        fii = screener.get("fii_holding")
        dii = screener.get("dii_holding")
        pe = screener.get("pe_ratio")
        bv = screener.get("book_value")
        div_yield = screener.get("dividend_yield_pct")
        roce = screener.get("roce_pct")
        roe = screener.get("roe_pct")
        dte = screener.get("debt_to_equity")
        rev_growth = screener.get("revenue_growth")
        profit_growth = screener.get("profit_growth")
        opm = screener.get("opm_pct")

        # Fallbacks from yfinance
        beta = safe_round(yf_extra.get("beta"))
        profit_margins = yf_extra.get("profitMargins")

        # Compute PB
        current_price = fast_quote.get("current_price")
        pb_ratio = None
        if bv and current_price:
            try:
                pb_ratio = safe_round(float(current_price) / float(bv))
            except Exception:
                pass

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

            "about": ai_about.get("about", summary or f"{company_name} is listed on NSE India."),
            "products_services": ai_about.get("products_services", []),
            "subsidiaries": ai_about.get("subsidiaries", []),
            "recent_highlights": ai_about.get("recent_highlights", []),

            "key_points": {
                "promoter_holding": f"{promoter}%" if promoter is not None else "N/A",
                "fii_holding": f"{fii}%" if fii is not None else "N/A",
                "dii_holding": f"{dii}%" if dii is not None else "N/A",
                "pe_ratio": pe if pe is not None else "N/A",
                "pb_ratio": pb_ratio if pb_ratio is not None else "N/A",
                "beta": beta if beta is not None else "N/A",
                "dividend_yield": f"{div_yield}%" if div_yield is not None else "N/A",
                "debt_to_equity": screener.get("debt_to_equity") if screener.get("debt_to_equity") is not None else "N/A",
                "revenue_growth": f"{screener.get('revenue_growth')}%" if screener.get("revenue_growth") is not None else "N/A",
                "earnings_growth": f"{screener.get('profit_growth')}%" if screener.get("profit_growth") is not None else "N/A",
                "profit_margins": f"{screener.get('opm_pct')}%" if screener.get("opm_pct") is not None else "N/A",
                "roe": f"{roe}%" if roe is not None else "N/A",
            },

            "strengths": ai_about.get("strengths", []),
            "risks": ai_about.get("risks", []),
        }

        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"Company info error for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return {"name": symbol.replace(".NS", ""), "symbol": symbol, "error": str(e)}


def _get_yf_extra_info(symbol: str) -> dict:
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

        result = {
            "summary": info.get("longBusinessSummary", ""),
            "website": info.get("website", "N/A"),
            "city": info.get("city", "N/A"),
            "country": info.get("country", "India"),
            "employees": info.get("fullTimeEmployees", "N/A"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "beta": info.get("beta"),
            "profitMargins": info.get("profitMargins"),
        }

        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"[YF EXTRA] Error for {symbol}: {e}")
        empty = {
            "summary": "", "website": "N/A", "city": "N/A",
            "country": "India", "employees": "N/A",
            "sector": None, "industry": None,
            "beta": None, "profitMargins": None,
        }
        set_cache(cache_key, empty, ttl_seconds=3600)
        return empty


def get_ai_company_details(company_name, sector, industry, summary):
    cache_key = f"ai_company_{company_name}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "about": summary or f"{company_name} is listed on NSE India.",
            "products_services": [], "subsidiaries": [],
            "recent_highlights": [], "strengths": [], "risks": []
        }

    client = Groq(api_key=api_key)

    prompt = f"""
You are a financial analyst. Provide detailed information about {company_name} (Indian stock market company).
Sector: {sector}, Industry: {industry}
Company summary: {summary[:500] if summary else 'Not available'}

Return valid JSON only:
{{
    "about": "<150-200 word description>",
    "products_services": ["<product 1>","<product 2>","<product 3>","<product 4>","<product 5>"],
    "subsidiaries": ["<subsidiary 1>","<subsidiary 2>","<subsidiary 3>","<subsidiary 4>"],
    "recent_highlights": ["<highlight 1>","<highlight 2>","<highlight 3>"],
    "strengths": ["<strength 1>","<strength 2>","<strength 3>"],
    "risks": ["<risk 1>","<risk 2>","<risk 3>"]
}}
Rules: factual, Indian market context, specific not generic, valid JSON only.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Financial analyst. Valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3, max_tokens=1500
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
            "about": summary or f"{company_name} is in the {sector} sector.",
            "products_services": [], "subsidiaries": [],
            "recent_highlights": [], "strengths": [], "risks": []
        }