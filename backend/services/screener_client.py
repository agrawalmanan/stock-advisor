import requests
import re
from bs4 import BeautifulSoup
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round

SCREENER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def _to_float(value: str):
    try:
        value = str(value).replace(",", "").replace("%", "").strip()
        if value in ["", "-", "N/A", "None"]:
            return None
        return float(value)
    except Exception:
        return None


def _extract_last_number(text: str):
    matches = re.findall(r"[-+]?\d[\d,]*\.?\d*", text.replace("₹", ""))
    if not matches:
        return None
    value = matches[-1].replace(",", "")
    return _to_float(value)


def get_screener_data(symbol: str) -> dict:
    """
    Scrape comprehensive data from Screener.in
    Returns fundamentals + sector/industry + key financial metrics
    """
    cache_key = f"screener_full_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    clean_symbol = symbol.replace(".NS", "").upper()

    urls = [
        f"https://www.screener.in/company/{clean_symbol}/consolidated/",
        f"https://www.screener.in/company/{clean_symbol}/",
    ]

    for url in urls:
        try:
            response = requests.get(url, headers=SCREENER_HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # ---- Extract Sector/Industry ----
            sector = "Unknown"
            industry = "Unknown"

            # Method 1: From company profile section
            for a in soup.select("a"):
                href = a.get("href", "")
                if "/sector/" in href:
                    industry = a.get_text(strip=True)
                    break

            # Method 2: From breadcrumb or header
            for el in soup.select(".company-info a, .sub-heading a"):
                href = el.get("href", "")
                if "/sector/" in href:
                    industry = el.get_text(strip=True)
                    break

            # Map industry to broader sector
            sector = _map_industry_to_sector(industry)

            # ---- Extract Ratios ----
            values = {}
            for li in soup.select("ul#top-ratios li"):
                spans = li.select("span")
                if len(spans) >= 2:
                    key = spans[0].get_text(" ", strip=True).lower()
                    value = spans[-1].get_text(" ", strip=True)
                    values[key] = value

            # Parse individual values
            market_cap = None
            pe_ratio = None
            book_value = None
            dividend_yield = None
            roce = None
            roe = None
            debt_to_equity = None
            promoter_holding = None
            fii_holding = None
            dii_holding = None
            revenue_growth = None
            profit_growth = None
            opm = None

            for k, v in values.items():
                if "market cap" in k:
                    market_cap = _extract_last_number(v)
                elif "stock p/e" in k:
                    pe_ratio = _extract_last_number(v)
                elif "book value" in k:
                    book_value = _extract_last_number(v)
                elif "dividend yield" in k:
                    dividend_yield = _extract_last_number(v)
                elif "roce" in k:
                    roce = _extract_last_number(v)
                elif "roe" in k:
                    roe = _extract_last_number(v)

            # ---- Extract Shareholding ----
            for table in soup.select("table"):
                for tr in table.select("tr"):
                    tds = tr.select("td")
                    if len(tds) >= 2:
                        label = tds[0].get_text(strip=True).lower()
                        val = tds[-1].get_text(strip=True)
                        if "promoter" in label and "pledge" not in label:
                            promoter_holding = _extract_last_number(val)
                        elif "fii" in label or "foreign" in label:
                            fii_holding = _extract_last_number(val)
                        elif "dii" in label or "domestic" in label:
                            dii_holding = _extract_last_number(val)

            # ---- Extract Growth from Profit & Loss ----
            for table in soup.select("table"):
                headers = [th.get_text(strip=True) for th in table.select("th")]
                if "Sales" in str(headers) or "Revenue" in str(headers):
                    for tr in table.select("tr"):
                        label_el = tr.select_one("td")
                        if label_el:
                            label = label_el.get_text(strip=True).lower()
                            tds = tr.select("td")
                            if "sales" in label or "revenue" in label:
                                if len(tds) >= 3:
                                    try:
                                        prev = _to_float(tds[-2].get_text(strip=True))
                                        curr = _to_float(tds[-1].get_text(strip=True))
                                        if prev and curr and prev > 0:
                                            revenue_growth = safe_round(((curr - prev) / prev) * 100)
                                    except Exception:
                                        pass
                            elif "net profit" in label or "profit" in label:
                                if len(tds) >= 3:
                                    try:
                                        prev = _to_float(tds[-2].get_text(strip=True))
                                        curr = _to_float(tds[-1].get_text(strip=True))
                                        if prev and curr and prev > 0:
                                            profit_growth = safe_round(((curr - prev) / prev) * 100)
                                    except Exception:
                                        pass
                            elif "opm" in label or "operating profit margin" in label:
                                if len(tds) >= 2:
                                    opm = _extract_last_number(tds[-1].get_text(strip=True))

            # ---- Extract Debt to Equity from Balance Sheet ----
            for el in soup.select(".company-ratios li, .ratio-list li"):
                text = el.get_text(" ", strip=True).lower()
                if "debt" in text and "equity" in text:
                    debt_to_equity = _extract_last_number(el.get_text(strip=True))

            result = {
                "sector": sector,
                "industry": industry,
                "market_cap_cr": market_cap,
                "pe_ratio": safe_round(pe_ratio) if pe_ratio is not None else None,
                "book_value": safe_round(book_value) if book_value is not None else None,
                "dividend_yield_pct": safe_round(dividend_yield) if dividend_yield is not None else None,
                "roce_pct": safe_round(roce) if roce is not None else None,
                "roe_pct": safe_round(roe) if roe is not None else None,
                "opm_pct": safe_round(opm) if opm is not None else None,
                "debt_to_equity": safe_round(debt_to_equity) if debt_to_equity is not None else None,
                "promoter_holding": safe_round(promoter_holding) if promoter_holding is not None else None,
                "fii_holding": safe_round(fii_holding) if fii_holding is not None else None,
                "dii_holding": safe_round(dii_holding) if dii_holding is not None else None,
                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "source": "screener"
            }

            set_cache(cache_key, result, ttl_seconds=86400)
            print(f"[SCREENER] Got data for {clean_symbol}: sector={sector}, industry={industry}")
            return result

        except Exception as e:
            print(f"[SCREENER] Error for {clean_symbol} via {url}: {e}")

    return _empty_screener_result()


def _empty_screener_result():
    return {
        "sector": "Unknown",
        "industry": "Unknown",
        "market_cap_cr": None,
        "pe_ratio": None,
        "book_value": None,
        "dividend_yield_pct": None,
        "roce_pct": None,
        "roe_pct": None,
        "opm_pct": None,
        "debt_to_equity": None,
        "promoter_holding": None,
        "fii_holding": None,
        "dii_holding": None,
        "revenue_growth": None,
        "profit_growth": None,
        "source": "screener"
    }


# Keep old function name for backward compatibility
def get_screener_fundamentals(symbol: str) -> dict:
    return get_screener_data(symbol)


def _map_industry_to_sector(industry: str) -> str:
    """Map Screener.in industry name to a broader sector"""
    industry_lower = industry.lower()

    SECTOR_MAP = {
        # Technology
        "software": "Information Technology",
        "it ": "Information Technology",
        "computer": "Information Technology",
        "digital": "Information Technology",
        "tech": "Information Technology",

        # Banking
        "bank": "Banking",
        "banking": "Banking",

        # Financial Services
        "finance": "Financial Services",
        "insurance": "Financial Services",
        "nbfc": "Financial Services",
        "capital market": "Financial Services",
        "housing finance": "Financial Services",

        # Oil & Gas
        "oil": "Oil & Gas",
        "gas": "Oil & Gas",
        "petroleum": "Oil & Gas",
        "refiner": "Oil & Gas",

        # Pharma
        "pharma": "Pharmaceuticals",
        "drug": "Pharmaceuticals",
        "healthcare": "Healthcare",
        "hospital": "Healthcare",
        "diagnostic": "Healthcare",

        # Auto
        "auto": "Automobile",
        "vehicle": "Automobile",
        "tyre": "Automobile",
        "tire": "Automobile",
        "two wheeler": "Automobile",
        "three wheeler": "Automobile",

        # FMCG
        "fmcg": "FMCG",
        "consumer": "FMCG",
        "food": "FMCG",
        "beverage": "FMCG",
        "personal care": "FMCG",
        "tobacco": "FMCG",

        # Metals
        "steel": "Metals & Mining",
        "iron": "Metals & Mining",
        "metal": "Metals & Mining",
        "mining": "Metals & Mining",
        "aluminium": "Metals & Mining",
        "copper": "Metals & Mining",
        "zinc": "Metals & Mining",

        # Cement
        "cement": "Cement",

        # Paints
        "paint": "Paints",
        "coating": "Paints",
        "decorative": "Paints",

        # Power
        "power": "Power & Utilities",
        "electric": "Power & Utilities",
        "energy": "Power & Utilities",
        "renewable": "Power & Utilities",
        "solar": "Power & Utilities",
        "wind": "Power & Utilities",

        # Infra
        "infrastructure": "Infrastructure",
        "construction": "Infrastructure",
        "engineering": "Infrastructure",
        "capital goods": "Infrastructure",

        # Telecom
        "telecom": "Telecom",
        "communication": "Telecom",

        # Real Estate
        "real estate": "Real Estate",
        "realty": "Real Estate",
        "housing": "Real Estate",

        # Textile
        "textile": "Textiles",
        "garment": "Textiles",
        "apparel": "Textiles",

        # Chemical
        "chemical": "Chemicals",
        "fertilizer": "Chemicals",
        "agrochemical": "Chemicals",
        "pesticide": "Chemicals",

        # Media
        "media": "Media & Entertainment",
        "entertainment": "Media & Entertainment",
        "broadcast": "Media & Entertainment",

        # Defence
        "defence": "Defence",
        "defense": "Defence",
        "aerospace": "Defence",

        # Aviation
        "airline": "Aviation",
        "aviation": "Aviation",

        # Retail
        "retail": "Retail",

        # Hotel
        "hotel": "Hotels & Tourism",
        "tourism": "Hotels & Tourism",
        "hospitality": "Hotels & Tourism",

        # Logistics
        "logistics": "Logistics",
        "shipping": "Logistics",
        "transport": "Logistics",

        # Paper
        "paper": "Paper",
        "packaging": "Packaging",
    }

    for keyword, sector in SECTOR_MAP.items():
        if keyword in industry_lower:
            return sector

    return industry if industry != "Unknown" else "Diversified"