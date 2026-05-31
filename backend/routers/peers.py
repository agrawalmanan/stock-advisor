from fastapi import APIRouter, Path, HTTPException
from services.peer_fetcher import get_peer_data
from services.market_data import get_stock_data

router = APIRouter()

@router.get("/peers/{symbol}")
def get_peers(
    symbol: str = Path(..., description="NSE stock symbol e.g. RELIANCE")
):
    """
    Get enhanced peer comparison data with ROCE, OPM
    GET /api/peers/RELIANCE
    """
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    # Get stock data for sector
    stock_data = get_stock_data(symbol)
    sector = stock_data.get("sector", "Unknown") if "error" not in stock_data else "Unknown"

    result = get_peer_data(
        peer_symbols=[],
        exclude_symbol=symbol,
        sector=sector
    )

    if not result["peers"]:
        return {
            "symbol": symbol,
            "sector": sector,
            "count": 0,
            "peers": [],
            "industry_median": {}
        }

    return {
        "symbol": symbol,
        "sector": sector,
        "count": len(result["peers"]),
        "peers": result["peers"],
        "industry_median": result["industry_median"]
    }