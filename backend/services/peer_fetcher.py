import yfinance as yf
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round, format_market_cap
from utils.yf_client import get_ticker, with_retries
from services.financials_calc import get_financial_metrics
import requests

# Patch yfinance session with browser headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
})

# Expanded sector → peers mapping (6 peers each)
# Updated sector → peers mapping matching new Screener sectors
SECTOR_PEERS = {
    # IT
    "IT Services": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "COFORGE.NS"],
    "Information Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS"],
    "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS"],

    # Banking
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS"],

    # Financial Services
    "Financial Services": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "SHRIRAMFIN.NS", "M&MFIN.NS", "LICHSGFIN.NS"],

    # Oil & Gas
    "Oil & Gas": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "HINDPETRO.NS", "PETRONET.NS"],

    # Pharma
    "Pharmaceuticals": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BIOCON.NS", "AUROPHARMA.NS", "LUPIN.NS", "TORNTPHARM.NS"],

    # Healthcare
    "Healthcare": ["APOLLOHOSP.NS", "FORTIS.NS", "MAXHEALTH.NS", "METROPOLIS.NS", "LALPATHLAB.NS", "STARHEALTH.NS"],

    # Auto
    "Automobile": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS"],

    # FMCG
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS"],

    # Steel
    "Steel": ["TATASTEEL.NS", "JSWSTEEL.NS", "SAIL.NS", "JINDALSTEL.NS", "APLAPOLLO.NS", "RATNAMANI.NS"],

    # Metals & Mining
    "Metals & Mining": ["HINDALCO.NS", "VEDL.NS", "NMDC.NS", "COALINDIA.NS", "NATIONALUM.NS", "MOIL.NS", "HINDCOPPER.NS"],

    # Cement
    "Cement": ["ULTRACEMCO.NS", "AMBUJACEM.NS", "ACC.NS", "SHREECEM.NS", "RAMCOCEM.NS", "DALMIACEM.NS", "JKCEMENT.NS"],

    # Paints
    "Paints": ["ASIANPAINT.NS", "BERGEPAINT.NS", "KANSAINER.NS", "AKZONOBEL.NS", "INDIGO.NS", "CENTURYTEX.NS"],

    # Power
    "Power & Utilities": ["NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS", "ADANIGREEN.NS", "NHPC.NS", "SJVN.NS", "IREDA.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "NTPC.NS", "POWERGRID.NS"],

    # Infrastructure
    "Infrastructure": ["LT.NS", "SIEMENS.NS", "ABB.NS", "BHEL.NS", "HAL.NS", "BEL.NS", "CUMMINSIND.NS"],

    # Telecom
    "Telecom": ["BHARTIARTL.NS", "IDEA.NS", "TATACOMM.NS", "INDUSTOWER.NS"],

    # Real Estate
    "Real Estate": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS"],

    # Chemicals
    "Chemicals": ["PIDILITIND.NS", "UPL.NS", "ATUL.NS", "DEEPAKFERT.NS", "GNFC.NS", "NAVINFLUOR.NS", "CLEAN.NS"],

    # Textiles
    "Textiles": ["PAGEIND.NS", "RAYMOND.NS", "ARVIND.NS", "TRIDENT.NS", "WELSPUNLIV.NS"],

    # Media
    "Media & Entertainment": ["ZEEL.NS", "SUNTV.NS", "PVR.NS", "NETWORK18.NS", "TV18BRDCST.NS"],

    # Defence
    "Defence": ["HAL.NS", "BEL.NS", "BDL.NS", "MAZAGON.NS", "GRSE.NS", "COCHINSHIP.NS"],

    # Aviation
    "Aviation": ["INDIGO.NS", "SPICEJET.NS"],

    # Hotels
    "Hotels & Tourism": ["INDHOTEL.NS", "LEMON.NS", "CHALET.NS", "EIH.NS"],

    # Logistics
    "Logistics": ["DELHIVERY.NS", "BLUEDART.NS", "CONCOR.NS", "ALLCARGO.NS", "TCI.NS"],

    # Retail
    "Retail": ["TRENT.NS", "DMART.NS", "SHOPERSTOP.NS", "VMART.NS"],

    # Electronics
    "Electronics": ["DIXON.NS", "VOLTAS.NS", "HAVELLS.NS", "CROMPTON.NS", "BLUESTARCO.NS"],

    # Jewellery
    "Jewellery": ["TITAN.NS", "KALYANKJIL.NS", "SENCO.NS", "PCJEWELLER.NS"],

    # Diversified
    "Diversified": ["RELIANCE.NS", "LT.NS", "ITC.NS", "ADANIENT.NS", "BAJAJHLDNG.NS", "TATAELXSI.NS"],

    # Paper
    "Paper & Packaging": ["BALLARPUR.NS", "TNPL.NS", "JKPAPER.NS", "STARPAPER.NS"],
}

def get_peers_by_sector(sector: str, exclude_symbol: str, limit: int = 6) -> list:
    """Find peer symbols from same sector"""
    # Direct match first
    peers = SECTOR_PEERS.get(sector, [])

    # If no direct match, try related sectors
    if not peers:
        RELATED_SECTORS = {
            "Steel": "Metals & Mining",
            "Metals & Mining": "Steel",
            "Oil & Gas": "Energy",
            "Energy": "Oil & Gas",
            "IT Services": "Information Technology",
            "Information Technology": "IT Services",
            "Power & Utilities": "Energy",
            "Pharmaceuticals": "Healthcare",
            "Healthcare": "Pharmaceuticals",
            "Paper & Packaging": "FMCG",
        }
        related = RELATED_SECTORS.get(sector)
        if related:
            peers = SECTOR_PEERS.get(related, [])

    # Remove the stock itself
    peers = [p for p in peers if p != exclude_symbol]
    return peers[:limit]


def get_peer_data(peer_symbols: list, exclude_symbol: str = "", sector: str = "") -> dict:
    """
    Fetch detailed data for peer stocks including ROCE and OPM
    Returns peers list + industry median
    """
    # If no peers provided, find by sector
    if not peer_symbols and sector:
        peer_symbols = get_peers_by_sector(sector, exclude_symbol)

    if not peer_symbols:
        return {"peers": [], "industry_median": {}}

    cache_key = f"peers_enhanced_{'_'.join(sorted(peer_symbols[:6]))}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    peers = []

    for symbol in peer_symbols[:6]:
        try:
            if not symbol.endswith(".NS"):
                symbol = symbol + ".NS"

            if symbol == exclude_symbol:
                continue

            ticker = get_ticker(symbol)
            info = with_retries(lambda: ticker.info)

            if not info:
                continue

            current_price = info.get("regularMarketPrice") or info.get("currentPrice")
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")

            change_pct = "N/A"
            if current_price and prev_close:
                change_pct = safe_round(
                    ((float(current_price) - float(prev_close)) / float(prev_close)) * 100
                )

            # Get financial metrics (ROCE, OPM)
            financials = get_financial_metrics(symbol)

            peers.append({
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "current_price": safe_round(current_price),
                "change_pct": change_pct,
                "market_cap": format_market_cap(info.get("marketCap")),
                "market_cap_raw": info.get("marketCap", 0),
                "pe_ratio": financials.get("pe_ratio", "N/A"),
                "roce_pct": financials.get("roce_pct", "N/A"),
                "opm_pct": financials.get("opm_pct", "N/A"),
                "week_52_high": safe_round(info.get("fiftyTwoWeekHigh")),
                "week_52_low": safe_round(info.get("fiftyTwoWeekLow")),
                "sector": info.get("sector", "N/A"),
            })

        except Exception as e:
            print(f"Peer fetch error for {symbol}: {e}")
            continue

    # Calculate Industry Median
    industry_median = calculate_industry_median(peers)

    result = {
        "peers": peers,
        "industry_median": industry_median
    }

    # Cache for 10 minutes (peer data takes long to fetch)
    set_cache(cache_key, result, ttl_seconds=600)
    return result


def calculate_industry_median(peers: list) -> dict:
    """
    Calculate median of P/E, ROCE%, OPM% across all peers
    """
    import statistics

    def get_valid_numbers(key):
        vals = []
        for p in peers:
            v = p.get(key)
            if v != "N/A" and v is not None:
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
        return vals

    pe_values = get_valid_numbers("pe_ratio")
    roce_values = get_valid_numbers("roce_pct")
    opm_values = get_valid_numbers("opm_pct")
    price_values = get_valid_numbers("current_price")
    change_values = get_valid_numbers("change_pct")

    return {
        "pe_ratio": safe_round(statistics.median(pe_values)) if pe_values else "N/A",
        "roce_pct": safe_round(statistics.median(roce_values)) if roce_values else "N/A",
        "opm_pct": safe_round(statistics.median(opm_values)) if opm_values else "N/A",
        "current_price": safe_round(statistics.median(price_values)) if price_values else "N/A",
        "change_pct": safe_round(statistics.median(change_values)) if change_values else "N/A",
        "market_cap": "Median",
    }