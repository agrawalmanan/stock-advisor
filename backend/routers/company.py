from fastapi import APIRouter, Path, HTTPException
from services.company_info import get_company_info

router = APIRouter()

@router.get("/company/{symbol}")
def get_company(
    symbol: str = Path(..., description="NSE stock symbol e.g. RELIANCE")
):
    """
    Get comprehensive company information
    GET /api/company/RELIANCE
    """
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    result = get_company_info(symbol)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result