from fastapi import APIRouter, Query
from services.stock_mapper import search_stocks

router = APIRouter()

@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Stock name or symbol to search")):
    """
    Search for NSE stocks by name or symbol
    Used for autocomplete in frontend
    GET /api/search?q=reliance
    """
    results = search_stocks(query=q, limit=10)

    if not results:
        return {
            "query": q,
            "count": 0,
            "results": []
        }

    return {
        "query": q,
        "count": len(results),
        "results": results
    }