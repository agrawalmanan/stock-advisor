from fastapi import APIRouter, Path, Query, HTTPException
from services.technical import get_full_analysis

router = APIRouter()

@router.get("/analysis/{symbol}")
def get_analysis(
    symbol: str = Path(..., description="NSE stock symbol e.g. RELIANCE"),
    period: str = Query("3mo", description="Analysis period: 3mo or 6mo")
):
    """
    Get full technical analysis for a stock
    GET /api/analysis/RELIANCE?period=3mo
    """
    # Normalize symbol
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    if period not in ["3mo", "6mo"]:
        period = "3mo"

    result = get_full_analysis(symbol, period)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result

@router.get("/analysis/{symbol}/interpret")
def get_interpretation(
    symbol: str = Path(..., description="NSE stock symbol"),
    period: str = Query("3mo", description="Analysis period")
):
    """
    Get AI-generated interpretation of technical indicators
    GET /api/analysis/RELIANCE/interpret
    """
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    if period not in ["3mo", "6mo"]:
        period = "3mo"

    from services.technical import get_full_analysis
    from services.indicator_interpreter import get_indicator_interpretation

    analysis = get_full_analysis(symbol, period)
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])

    interpretation = get_indicator_interpretation(symbol, analysis)
    return interpretation