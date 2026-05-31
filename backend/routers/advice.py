from fastapi import APIRouter, Path, HTTPException
from services.market_data import get_stock_data, get_historical_returns
from services.technical import get_full_analysis
from services.news_fetcher import get_stock_news
from services.groq_ai import get_ai_advice
from services.peer_fetcher import get_peer_data

router = APIRouter()

@router.get("/advice/{symbol}")
def get_advice(
    symbol: str = Path(..., description="NSE stock symbol e.g. RELIANCE")
):
    """
    Get AI-powered Buy/Sell/Hold advice for a stock
    Combines: live data + technical analysis + news + Groq AI
    GET /api/advice/RELIANCE
    """
    # Normalize symbol
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    # Step 1: Get stock data
    stock_data = get_stock_data(symbol)
    if "error" in stock_data:
        raise HTTPException(status_code=404, detail=stock_data["error"])

    # Step 2: Get technical analysis (use 3mo for advice)
    analysis = get_full_analysis(symbol, period="3mo")
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])

    # Step 3: Get historical returns
    returns = get_historical_returns(symbol)

    # Step 4: Get recent news headlines
    news = get_stock_news(symbol, stock_data.get("name", ""))

    # Step 5: Get peer comparison data
    # NEW
    peer_result = get_peer_data(
        peer_symbols=stock_data.get("peers", []),
        exclude_symbol=symbol,
        sector=stock_data.get("sector", "")
    )
    peers = peer_result.get("peers", [])
    industry_median = peer_result.get("industry_median", {})

    # Step 6: Call Groq AI with all data
    advice = get_ai_advice(
        symbol=symbol,
        company_name=stock_data.get("name", symbol),
        sector=stock_data.get("sector", "Unknown"),
        current_price=stock_data.get("current_price", 0),
        change_pct=stock_data.get("change_pct", 0),
        rsi=analysis.get("rsi", {}),
        macd=analysis.get("macd", {}),
        trend=analysis.get("trend", {}),
        support_resistance=analysis.get("support_resistance", {}),
        historical_returns=returns,
        news_headlines=news,
        risk=stock_data.get("risk", {}),
        moving_averages=analysis.get("moving_averages", {})
    )

    return {
        "symbol": symbol,
        "company": stock_data.get("name", symbol),
        "sector": stock_data.get("sector", "Unknown"),
        "current_price": stock_data.get("current_price"),
        "advice": advice,
        "peers": peers,
        "industry_median": industry_median,
        "analysis_used": {
            "rsi": analysis.get("rsi", {}),
            "macd": analysis.get("macd", {}),
            "trend": analysis.get("trend", {}),
            "support_resistance": analysis.get("support_resistance", {})
        }
    }