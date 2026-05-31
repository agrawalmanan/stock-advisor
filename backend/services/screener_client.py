import requests
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


def get_screener_fundamentals(symbol: str) -> dict:
    """
    Scrape fundamentals from Screener.in
    Works well for Indian listed companies.
    """
    cache_key = f"screener_fundamentals_{symbol}"
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

            # Main ratio boxes
            values = {}
            for li in soup.select("ul#top-ratios li"):
                name_el = li.select_one("span.name")
                value_el = li.select_one("span.value, span.nowrap")
                if not name_el or not value_el:
                    continue

                key = " ".join(name_el.get_text(" ", strip=True).split()).lower()
                value = " ".join(value_el.get_text(" ", strip=True).split())
                values[key] = value

            # Fallback selectors in case structure varies
            if not values:
                for li in soup.select("li"):
                    text = li.get_text(" ", strip=True).lower()
                    if "market cap" in text:
                        values["market cap"] = li.get_text(" ", strip=True)
                    elif "stock p/e" in text:
                        values["stock p/e"] = li.get_text(" ", strip=True)
                    elif "book value" in text:
                        values["book value"] = li.get_text(" ", strip=True)
                    elif "dividend yield" in text:
                        values["dividend yield"] = li.get_text(" ", strip=True)

            # Extract by matching label starts
            market_cap = None
            pe_ratio = None
            book_value = None
            dividend_yield = None
            roce = None
            roe = None

            for k, v in values.items():
                if k.startswith("market cap"):
                    market_cap = _extract_last_number(v)
                elif k.startswith("stock p/e"):
                    pe_ratio = _extract_last_number(v)
                elif k.startswith("book value"):
                    book_value = _extract_last_number(v)
                elif k.startswith("dividend yield"):
                    dividend_yield = _extract_last_number(v)
                elif k.startswith("roce"):
                    roce = _extract_last_number(v)
                elif k.startswith("roe"):
                    roe = _extract_last_number(v)

            result = {
                "market_cap_cr": market_cap,       # in crore
                "pe_ratio": safe_round(pe_ratio) if pe_ratio is not None else None,
                "book_value": safe_round(book_value) if book_value is not None else None,
                "dividend_yield_pct": safe_round(dividend_yield) if dividend_yield is not None else None,
                "roce_pct": safe_round(roce) if roce is not None else None,
                "roe_pct": safe_round(roe) if roe is not None else None,
                "source": "screener"
            }

            set_cache(cache_key, result, ttl_seconds=86400)  # 24h
            return result

        except Exception as e:
            print(f"[SCREENER] Error for {symbol} via {url}: {e}")

    return {
        "market_cap_cr": None,
        "pe_ratio": None,
        "book_value": None,
        "dividend_yield_pct": None,
        "roce_pct": None,
        "roe_pct": None,
        "source": "screener"
    }


def _extract_last_number(text: str):
    """
    Pull the last numeric value from text like:
    'Market Cap ₹ 81,73,000 Cr.'
    """
    import re

    matches = re.findall(r"[-+]?\d[\d,]*\.?\d*", text.replace("₹", ""))
    if not matches:
        return None

    value = matches[-1].replace(",", "")
    return _to_float(value)