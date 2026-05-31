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
        value = str(value).replace(",", "").replace("%", "").replace("₹", "").strip()
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

            # ========== TOP RATIOS ==========
            market_cap = None
            pe_ratio = None
            book_value = None
            dividend_yield = None
            roce = None
            roe = None
            face_value = None

            for li in soup.select("ul#top-ratios li"):
                spans = li.select("span")
                if len(spans) >= 2:
                    label = spans[0].get_text(strip=True).lower()
                    value = spans[-1].get_text(strip=True)

                    if "market cap" in label:
                        market_cap = _extract_last_number(value)
                    elif "stock p/e" in label:
                        pe_ratio = _to_float(value)
                    elif "book value" in label:
                        book_value = _to_float(value)
                    elif "dividend yield" in label:
                        dividend_yield = _to_float(value)
                    elif "roce" in label:
                        roce = _to_float(value)
                    elif "roe" in label:
                        roe = _to_float(value)
                    elif "face value" in label:
                        face_value = _to_float(value)

            # ========== INDUSTRY/SECTOR ==========
            industry = "Unknown"
            # Try company info section
            company_info = soup.select_one(".company-info")
            if company_info:
                for a in company_info.select("a"):
                    href = a.get("href", "")
                    if "/sector/" in href:
                        industry = a.get_text(strip=True)
                        break

            # Fallback: search all links
            if industry == "Unknown":
                for a in soup.select("a"):
                    href = a.get("href", "")
                    if "/sector/" in href:
                        industry = a.get_text(strip=True)
                        break

            sector = _map_industry_to_sector(industry)

            # ========== PROFIT & LOSS TABLE ==========
            opm = None
            revenue_growth = None
            profit_growth = None
            net_profit_latest = None

            for section in soup.select("section"):
                heading = section.select_one("h2")
                if not heading:
                    continue
                h_text = heading.get_text(strip=True).lower()

                # Profit & Loss (Annual)
                if "profit" in h_text and "loss" in h_text and "quarter" not in h_text:
                    table = section.select_one("table")
                    if table:
                        for tr in table.select("tr"):
                            cells = [td.get_text(strip=True) for td in tr.select("td, th")]
                            if not cells:
                                continue

                            row_label = cells[0].lower()

                            # OPM %
                            if "opm" in row_label:
                                if len(cells) >= 2:
                                    opm = _to_float(cells[-1])

                            # Sales for revenue growth
                            if "sales" in row_label:
                                if len(cells) >= 3:
                                    prev_sales = _to_float(cells[-2])
                                    curr_sales = _to_float(cells[-1])
                                    if prev_sales and curr_sales and prev_sales > 0:
                                        revenue_growth = safe_round(((curr_sales - prev_sales) / prev_sales) * 100)

                            # Net Profit for earnings growth
                            if "net profit" in row_label:
                                if len(cells) >= 3:
                                    prev_profit = _to_float(cells[-2])
                                    curr_profit = _to_float(cells[-1])
                                    if prev_profit and curr_profit and prev_profit > 0:
                                        profit_growth = safe_round(((curr_profit - prev_profit) / prev_profit) * 100)
                                    if len(cells) >= 2:
                                        net_profit_latest = _to_float(cells[-1])

            # ========== BALANCE SHEET TABLE ==========
            debt_to_equity = None
            total_borrowings = None
            total_equity = None

            for section in soup.select("section"):
                heading = section.select_one("h2")
                if not heading:
                    continue
                h_text = heading.get_text(strip=True).lower()

                if "balance" in h_text and "sheet" in h_text:
                    table = section.select_one("table")
                    if table:
                        for tr in table.select("tr"):
                            cells = [td.get_text(strip=True) for td in tr.select("td, th")]
                            if not cells:
                                continue

                            row_label = cells[0].lower()

                            # Borrowings
                            if "borrowing" in row_label:
                                if len(cells) >= 2:
                                    total_borrowings = _to_float(cells[-1])

                            # Equity + Reserves
                            if "reserves" in row_label:
                                if len(cells) >= 2:
                                    reserves = _to_float(cells[-1])

                            if "equity capital" in row_label:
                                if len(cells) >= 2:
                                    equity_capital = _to_float(cells[-1])

                        # Calculate D/E
                        try:
                            if total_borrowings is not None:
                                total_eq = (equity_capital or 0) + (reserves or 0)
                                if total_eq > 0:
                                    debt_to_equity = safe_round(total_borrowings / total_eq)
                        except Exception:
                            pass

            # ========== SHAREHOLDING ==========
            promoter_holding = None
            fii_holding = None
            dii_holding = None

            for section in soup.select("section"):
                heading = section.select_one("h2")
                if not heading:
                    continue
                if "holding" in heading.get_text(strip=True).lower():
                    table = section.select_one("table")
                    if table:
                        for tr in table.select("tr"):
                            cells = [td.get_text(strip=True) for td in tr.select("td, th")]
                            if len(cells) >= 2:
                                label = cells[0].lower()
                                val = _to_float(cells[-1])
                                if "promoter" in label and "pledge" not in label:
                                    promoter_holding = val
                                elif "fii" in label or "foreign" in label:
                                    fii_holding = val
                                elif "dii" in label or "domestic" in label:
                                    dii_holding = val

            # ========== PROFIT MARGIN ==========
            profit_margin = None
            if net_profit_latest and market_cap:
                # Approximate: we have sales from P&L
                pass  # We'll use OPM instead

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
                "debt_to_equity": debt_to_equity,
                "promoter_holding": safe_round(promoter_holding) if promoter_holding is not None else None,
                "fii_holding": safe_round(fii_holding) if fii_holding is not None else None,
                "dii_holding": safe_round(dii_holding) if dii_holding is not None else None,
                "revenue_growth": revenue_growth,
                "profit_growth": profit_growth,
                "source": "screener"
            }

            set_cache(cache_key, result, ttl_seconds=86400)
            print(f"[SCREENER] Got data for {clean_symbol}: sector={sector}, industry={industry}, opm={opm}, d/e={debt_to_equity}, rev_growth={revenue_growth}")
            return result

        except Exception as e:
            print(f"[SCREENER] Error for {clean_symbol} via {url}: {e}")
            import traceback
            traceback.print_exc()

    return _empty_screener_result()


def _empty_screener_result():
    return {
        "sector": "Unknown", "industry": "Unknown",
        "market_cap_cr": None, "pe_ratio": None, "book_value": None,
        "dividend_yield_pct": None, "roce_pct": None, "roe_pct": None,
        "opm_pct": None, "debt_to_equity": None,
        "promoter_holding": None, "fii_holding": None, "dii_holding": None,
        "revenue_growth": None, "profit_growth": None,
        "source": "screener"
    }


def get_screener_fundamentals(symbol: str) -> dict:
    return get_screener_data(symbol)


def _map_industry_to_sector(industry: str) -> str:
    industry_lower = industry.lower()

    SECTOR_MAP = {
        "software": "Information Technology",
        "it ": "Information Technology",
        "computer": "Information Technology",
        "digital": "Information Technology",
        "tech": "Information Technology",
        "bank": "Banking",
        "banking": "Banking",
        "finance": "Financial Services",
        "insurance": "Financial Services",
        "nbfc": "Financial Services",
        "capital market": "Financial Services",
        "housing finance": "Financial Services",
        "oil": "Oil & Gas",
        "gas": "Oil & Gas",
        "petroleum": "Oil & Gas",
        "refiner": "Oil & Gas",
        "pharma": "Pharmaceuticals",
        "drug": "Pharmaceuticals",
        "healthcare": "Healthcare",
        "hospital": "Healthcare",
        "diagnostic": "Healthcare",
        "auto": "Automobile",
        "vehicle": "Automobile",
        "tyre": "Automobile",
        "two wheeler": "Automobile",
        "three wheeler": "Automobile",
        "fmcg": "FMCG",
        "consumer": "FMCG",
        "food": "FMCG",
        "beverage": "FMCG",
        "personal care": "FMCG",
        "tobacco": "FMCG",
        "steel": "Metals & Mining",
        "iron": "Metals & Mining",
        "metal": "Metals & Mining",
        "mining": "Metals & Mining",
        "aluminium": "Metals & Mining",
        "copper": "Metals & Mining",
        "zinc": "Metals & Mining",
        "cement": "Cement",
        "paint": "Paints",
        "coating": "Paints",
        "decorative": "Paints",
        "power": "Power & Utilities",
        "electric": "Power & Utilities",
        "energy": "Power & Utilities",
        "renewable": "Power & Utilities",
        "solar": "Power & Utilities",
        "wind": "Power & Utilities",
        "infrastructure": "Infrastructure",
        "construction": "Infrastructure",
        "engineering": "Infrastructure",
        "capital goods": "Infrastructure",
        "telecom": "Telecom",
        "communication": "Telecom",
        "real estate": "Real Estate",
        "realty": "Real Estate",
        "textile": "Textiles",
        "garment": "Textiles",
        "apparel": "Textiles",
        "chemical": "Chemicals",
        "fertilizer": "Chemicals",
        "agrochemical": "Chemicals",
        "pesticide": "Chemicals",
        "media": "Media & Entertainment",
        "entertainment": "Media & Entertainment",
        "broadcast": "Media & Entertainment",
        "defence": "Defence",
        "defense": "Defence",
        "aerospace": "Defence",
        "airline": "Aviation",
        "aviation": "Aviation",
        "retail": "Retail",
        "hotel": "Hotels & Tourism",
        "tourism": "Hotels & Tourism",
        "hospitality": "Hotels & Tourism",
        "logistics": "Logistics",
        "shipping": "Logistics",
        "transport": "Logistics",
        "paper": "Paper",
        "packaging": "Packaging",
        "diversified": "Diversified",
    }

    for keyword, sector in SECTOR_MAP.items():
        if keyword in industry_lower:
            return sector

    return industry if industry != "Unknown" else "Diversified"