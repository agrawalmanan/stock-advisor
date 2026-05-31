from fastapi import APIRouter, Path, Query, HTTPException
from services.market_data import get_stock_data, get_historical_returns, get_chart_data
from services.risk_calculator import calculate_risk
from services.stock_classifier import classify_stock

router = APIRouter()

@router.get("/stock/{symbol}")
def get_stock(
    symbol: str = Path(..., description="NSE stock symbol e.g. RELIANCE.NS")
):
    """
    Get complete live stock data
    GET /api/stock/RELIANCE.NS
    """
    # normalize symbol
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    data = get_stock_data(symbol)

    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])

    # add historical returns
    data["historical_returns"] = get_historical_returns(symbol)

    # add risk level
    data["risk"] = calculate_risk(
        beta=data.get("beta"),
        sector=data.get("sector", "Unknown"),
        week_52_high=data.get("week_52_high"),
        week_52_low=data.get("week_52_low"),
        current_price=data.get("current_price")
    )

    # add delivery vs intraday tag
    data["trade_type"] = classify_stock(
        beta=data.get("beta"),
        avg_volume=data.get("avg_volume"),
        volume=data.get("volume"),
        sector=data.get("sector", "Unknown")
    )

    return data


@router.get("/stock/{symbol}/chart")
def get_chart(
    symbol: str = Path(..., description="NSE stock symbol"),
    period: str = Query("3mo", description="Chart period: 3mo or 6mo")
):
    """
    Get candlestick chart data
    GET /api/stock/RELIANCE.NS/chart?period=3mo
    """
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    if period not in ["3mo", "6mo", "1y"]:
        period = "3mo"

    candles = get_chart_data(symbol, period)

    if not candles:
        raise HTTPException(status_code=404, detail="Chart data not available")

    return {
        "symbol": symbol,
        "period": period,
        "count": len(candles),
        "candles": candles
    }