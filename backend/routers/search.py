from fastapi import APIRouter, Query
from services.stock_mapper import search_stocks

router = APIRouter()

@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Stock name or symbol to search")):
    """
    Search for NSE stocks by name or symbol
    """
    results = search_stocks(query=q, limit=10)

    if not results:
        return {
            "query": q,
            "count": 0,
            "results": []
        }

    # Replace "Unknown" sector with something useful
    for r in results:
        if r.get("sector") == "Unknown":
            r["sector"] = _guess_sector_from_name(r.get("name", ""))

    return {
        "query": q,
        "count": len(results),
        "results": results
    }


def _guess_sector_from_name(name: str) -> str:
    """Quick sector guess from company name"""
    name_lower = name.lower()

    QUICK_MAP = {
        "bank": "Banking",
        "pharma": "Pharma",
        "infosys": "IT",
        "tcs": "IT",
        "wipro": "IT",
        "hcl": "IT",
        "tech": "IT",
        "software": "IT",
        "steel": "Metals",
        "iron": "Metals",
        "metal": "Metals",
        "cement": "Cement",
        "paint": "Paints",
        "power": "Power",
        "energy": "Energy",
        "oil": "Oil & Gas",
        "gas": "Oil & Gas",
        "petro": "Oil & Gas",
        "auto": "Auto",
        "motor": "Auto",
        "tyre": "Auto",
        "finance": "Finance",
        "insurance": "Finance",
        "housing": "Finance",
        "food": "FMCG",
        "consumer": "FMCG",
        "hotel": "Hotels",
        "pharma": "Pharma",
        "drug": "Pharma",
        "health": "Healthcare",
        "hospital": "Healthcare",
        "chemical": "Chemicals",
        "fertiliz": "Chemicals",
        "textile": "Textiles",
        "real": "Real Estate",
        "infra": "Infra",
        "construction": "Infra",
        "telecom": "Telecom",
        "media": "Media",
        "jewel": "Jewellery",
        "gold": "Jewellery",
        "diamond": "Jewellery",
        "logistics": "Logistics",
        "shipping": "Logistics",
        "airline": "Aviation",
        "aviation": "Aviation",
        "defence": "Defence",
        "defense": "Defence",
        "retail": "Retail",
        "electric": "Power",
        "solar": "Power",
    }

    for keyword, sector in QUICK_MAP.items():
        if keyword in name_lower:
            return sector

    return "NSE"