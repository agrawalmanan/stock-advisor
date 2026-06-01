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

    SYMBOL_ALIASES = {
        "TATAMOTORS": "TATAMTRDVR",  # Try alternate if main fails
    }

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
            sector = "Unknown"

            # Get company name
            name_el = soup.select_one("h1")
            company_name = name_el.get_text(strip=True) if name_el else clean_symbol

            # Get about text from company-info section
            about_el = soup.select_one(".company-info")
            about_text = ""
            if about_el:
                about_text = about_el.get_text(" ", strip=True)

            # Combine name + about for detection
            detect_text = f"{company_name} {about_text}".lower()

            # Detect industry from text
            industry = _detect_industry_from_text(detect_text)
            sector = _map_industry_to_sector(industry)

            # ========== PROFIT & LOSS TABLE ==========
            opm = None
            revenue_growth = None
            profit_growth = None
            net_profit_latest = None
            equity_capital = 0
            reserves = 0

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
                            if row_label.startswith("sales"):
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

                            if "borrowing" in row_label:
                                if len(cells) >= 2:
                                    total_borrowings = _to_float(cells[-1])

                            if "reserves" in row_label:
                                if len(cells) >= 2:
                                    reserves = _to_float(cells[-1]) or 0

                            if "equity capital" in row_label:
                                if len(cells) >= 2:
                                    equity_capital = _to_float(cells[-1]) or 0

                        # Calculate D/E
                        try:
                            if total_borrowings is not None:
                                total_eq = equity_capital + reserves
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


def _detect_industry_from_text(text: str) -> str:
    """
    Detect industry from company description text
    Two-pass approach:
    1. First try specific multi-word phrases
    2. Then try simpler single-word keywords as fallback
    """
    text = text.lower()

    # ===== PASS 1: Specific multi-word phrases (highest accuracy) =====
    SPECIFIC_KEYWORDS = [
        ("Paints", [
            "paint company", "paints ltd", "paints limited", "wall paint",
            "decorative paint", "selling of paints", "manufacturing of paints",
            "manufacturing and selling of paints", "asian paints", "berger paints",
            "kansai nerolac", "paint manufacturer"
        ]),
        ("Steel", [
            "steel company", "steel ltd", "steel limited", "steel manufacturing",
            "integrated steel", "steel product", "iron and steel", "steel plant",
            "sponge iron plant"
        ]),
        ("Cement", [
            "cement company", "cement ltd", "cement limited", "cement manufacturer",
            "manufacturing of cement", "clinker capacity"
        ]),
        ("Jewellery", [
            "jewellery", "jewelry", "gems and jewel", "diamond company",
            "gold ornament", "precious metal"
        ]),
        ("IT Services", [
            "it services", "it consulting", "software service", "information technology",
            "consulting and business solutions", "tata consultancy", "software company",
            "software solutions", "digital transformation company"
        ]),
        ("Banking", [
            "banking company", "private sector bank", "public sector bank",
            "bank ltd", "bank limited", "banking and financial", "scheduled bank",
            "commercial bank"
        ]),
        ("Pharmaceuticals", [
            "pharmaceutical", "pharma company", "pharma ltd",
            "active pharma ingredient", "generic medicine", "bulk drug",
            "drug manufacturer", "formulations and api"
        ]),
        ("Healthcare", [
            "hospital company", "healthcare service", "diagnostic lab",
            "pathology", "medical device", "healthcare provider"
        ]),
        ("Financial Services", [
            "payment solution", "payment platform", "payment gateway",
            "fintech company", "non-banking finance", "nbfc", "finance company ltd",
            "investment & finance", "insurance company", "mutual fund",
            "asset management", "housing finance", "microfinance",
            "financial service"
        ]),
        ("Automobile", [
            "automobile company", "automotive company", "vehicle manufacturer",
            "two-wheeler", "three-wheeler", "two wheeler", "three wheeler",
            "motorcycle manufacturer", "car manufacturer", "tractor manufacturer",
            "auto component", "tyre manufacturer", "passenger vehicle",
            "commercial vehicle manufacturer"
        ]),
        ("FMCG", [
            "fmcg business", "fmcg company", "fast moving consumer",
            "personal care product", "home care product", "food product company",
            "food segment", "beverage company", "dairy product",
            "soap and detergent", "consumer goods"
        ]),
        ("Metals & Mining", [
            "aluminium company", "aluminum smelter", "copper smelter",
            "zinc company", "mining company", "ore mining",
            "production of aluminium", "production of copper",
            "aluminium and copper", "non-ferrous metal",
            "hindalco", "vedanta limited", "nalco", "hindustan copper"
        ]),
        ("Oil & Gas", [
            "oil and gas", "petroleum company", "oil refiner",
            "crude oil and natural gas", "petrochemical", "lng terminal",
            "oil exploration", "refining of crude"
        ]),
        ("Power & Utilities", [
            "power generation", "power company", "power distribution",
            "electricity generation", "thermal power", "hydro power",
            "solar energy company", "wind energy company", "renewable energy company",
            "power transmission", "power corporation"
        ]),
        ("Infrastructure", [
            "infrastructure company", "construction company",
            "engineering company", "engineering procurement",
            "capital goods", "heavy engineering", "epc company",
            "multinational conglomerate which is primarily engaged in providing engineering"
        ]),
        ("Telecom", [
            "telecom company", "telecommunication", "mobile operator",
            "broadband provider", "wireless service", "cellular operator"
        ]),
        ("Real Estate", [
            "real estate", "realty company", "property developer",
            "residential project", "township developer", "housing project"
        ]),
        ("Chemicals", [
            "chemical company", "chemical ltd", "specialty chemical",
            "agrochemical", "fertilizer company", "pesticide",
            "adhesives and sealants", "construction chemicals"
        ]),
        ("Textiles", [
            "textile company", "textile ltd", "yarn manufacturer",
            "garment manufacturer", "spinning mill"
        ]),
        ("Defence", [
            "defence equipment", "defense equipment", "defence ltd",
            "defence limited", "missile system", "ammunition manufacturer",
            "military equipment", "defence electronics", "naval shipbuilding",
            "electronic equipment and systems to the def",
            "bharat dynamics", "hindustan aeronautics", "mazagon dock"
        ]),
        ("Media & Entertainment", [
            "media company", "entertainment company", "broadcast",
            "television channel", "film production"
        ]),
        ("Retail", [
            "retail company", "retailing of apparel", "retailing of",
            "retail chain", "e-commerce company", "department store",
            "supermarket chain", "retail business"
        ]),
        ("Hotels & Tourism", [
            "hotel company", "hotel chain", "hospitality company",
            "leading hospitality", "diversified portfolio of hotels"
        ]),
        ("Logistics", [
            "logistics company", "shipping company", "freight",
            "courier company", "supply chain company"
        ]),
        ("Electronics", [
            "electronics company", "consumer electronics",
            "electronic manufacturing"
        ]),
        ("Paper & Packaging", [
            "paper company", "paper ltd", "packaging company"
        ]),
        ("Aviation", [
            "airline company", "aviation company", "aircraft operator"
        ]),
    ]

    for industry, keywords in SPECIFIC_KEYWORDS:
        for keyword in keywords:
            if keyword in text:
                return industry

    # ===== PASS 2: Simpler keywords (catches remaining) =====
    SIMPLE_KEYWORDS = [
        ("Paints", ["paints", "paint "]),
        ("Steel", ["steel "]),
        ("Cement", ["cement"]),
        ("IT Services", ["software", "infosys", "wipro", "hcl tech"]),
        ("Banking", [" bank ", " bank.", "banking"]),
        ("Pharmaceuticals", ["pharma", "drug", "medicine"]),
        ("Healthcare", ["hospital", "healthcare", "diagnostic"]),
        ("Automobile", ["motorcycle", "scooter", "vehicle", "automobile", "auto ", "tyre", "tire"]),
        ("FMCG", ["fmcg", "consumer product", "food and beverage", "personal care", "home care", "tobacco", "cigarette"]),
        ("Metals & Mining", ["aluminium", "aluminum", "copper", "zinc", "mining", "smelter"]),
        ("Oil & Gas", ["crude oil", "natural gas", "petroleum", "refinery", "refining"]),
        ("Power & Utilities", ["power plant", "electricity", "thermal", "solar", "wind energy", "power generation", "power distribution"]),
        ("Infrastructure", ["engineering", "infrastructure", "construction"]),
        ("Financial Services", ["finance", "insurance", "lending", "credit", "loan"]),
        ("Telecom", ["telecom", "mobile network"]),
        ("Real Estate", ["real estate", "realty", "property"]),
        ("Chemicals", ["chemical", "adhesive", "fertilizer", "pesticide"]),
        ("Textiles", ["textile", "apparel", "fabric", "garment"]),
        ("Defence", ["defence", "defense", "military"]),
        ("Retail", ["retail", "retailing"]),
        ("Hotels & Tourism", ["hotel", "hospitality", "resort"]),
        ("Logistics", ["logistics", "shipping", "transport", "freight"]),
        ("Aviation", ["airline", "aviation"]),
        ("Electronics", ["electronics", "appliance"]),
        ("Diversified", ["conglomerate", "diversified"]),
        ("Coal", ["coal mining", "coal production", "coal washeries"]),
    ]

    for industry, keywords in SIMPLE_KEYWORDS:
        for keyword in keywords:
            if keyword in text:
                return industry

    return "Unknown"

def _map_industry_to_sector(industry: str) -> str:
    """Map detected industry name directly to sector"""
    industry_lower = industry.lower()

    # EXACT matches first — industry name IS the sector
    EXACT_MAP = {
        "steel": "Steel",
        "it services": "IT Services",
        "banking": "Banking",
        "paints": "Paints",
        "cement": "Cement",
        "coal": "Metals & Mining",
        "pharmaceuticals": "Pharmaceuticals",
        "healthcare": "Healthcare",
        "automobile": "Automobile",
        "fmcg": "FMCG",
        "chemicals": "Chemicals",
        "textiles": "Textiles",
        "telecom": "Telecom",
        "real estate": "Real Estate",
        "aviation": "Aviation",
        "retail": "Retail",
        "logistics": "Logistics",
        "defence": "Defence",
        "diversified": "Diversified",
        "metals & mining": "Metals & Mining",
        "financial services": "Financial Services",
        "power & utilities": "Power & Utilities",
        "infrastructure": "Infrastructure",
        "media & entertainment": "Media & Entertainment",
        "electronics": "Electronics",
        "paper & packaging": "Paper & Packaging",
        "hotels & tourism": "Hotels & Tourism",
        "jewellery": "Jewellery",
        "oil & gas": "Oil & Gas",
    }

    if industry_lower in EXACT_MAP:
        return EXACT_MAP[industry_lower]

    # Keyword fallback — ORDER MATTERS
    KEYWORD_MAP = [
        ("steel", "Steel"),
        ("paint", "Paints"),
        ("coating", "Paints"),
        ("cement", "Cement"),
        ("jewel", "Jewellery"),
        ("airline", "Aviation"),
        ("aviation", "Aviation"),
        ("payment", "Financial Services"),
        ("fintech", "Financial Services"),
        ("software", "IT Services"),
        ("computer", "IT Services"),
        ("bank", "Banking"),
        ("pharma", "Pharmaceuticals"),
        ("drug", "Pharmaceuticals"),
        ("hospital", "Healthcare"),
        ("diagnostic", "Healthcare"),
        ("two wheeler", "Automobile"),
        ("three wheeler", "Automobile"),
        ("automobile", "Automobile"),
        ("tyre", "Automobile"),
        ("fmcg", "FMCG"),
        ("biscuit", "FMCG"),
        ("beverage", "FMCG"),
        ("tobacco", "FMCG"),
        ("aluminium", "Metals & Mining"),
        ("aluminum", "Metals & Mining"),
        ("copper", "Metals & Mining"),
        ("zinc", "Metals & Mining"),
        ("mining", "Metals & Mining"),
        ("metal", "Metals & Mining"),
        ("oil", "Oil & Gas"),
        ("petroleum", "Oil & Gas"),
        ("refiner", "Oil & Gas"),
        ("power", "Power & Utilities"),
        ("electricity", "Power & Utilities"),
        ("renewable", "Power & Utilities"),
        ("solar", "Power & Utilities"),
        ("infrastructure", "Infrastructure"),
        ("construction", "Infrastructure"),
        ("capital goods", "Infrastructure"),
        ("finance", "Financial Services"),
        ("insurance", "Financial Services"),
        ("nbfc", "Financial Services"),
        ("lending", "Financial Services"),
        ("telecom", "Telecom"),
        ("real estate", "Real Estate"),
        ("realty", "Real Estate"),
        ("textile", "Textiles"),
        ("garment", "Textiles"),
        ("chemical", "Chemicals"),
        ("fertilizer", "Chemicals"),
        ("media", "Media & Entertainment"),
        ("entertainment", "Media & Entertainment"),
        ("defence", "Defence"),
        ("defense", "Defence"),
        ("aerospace", "Defence"),
        ("retail", "Retail"),
        ("hotel", "Hotels & Tourism"),
        ("hospitality", "Hotels & Tourism"),
        ("logistics", "Logistics"),
        ("shipping", "Logistics"),
        ("paper", "Paper & Packaging"),
        ("packaging", "Paper & Packaging"),
        ("electronic", "Electronics"),
        ("coal", "Metals & Mining"),
        ("diversified", "Diversified"),
    ]

    for keyword, sector in KEYWORD_MAP:
        if keyword in industry_lower:
            return sector

    return industry if industry not in ["Unknown", ""] else "Diversified"