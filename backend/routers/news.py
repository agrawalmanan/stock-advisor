from fastapi import APIRouter, Path, HTTPException
from services.news_fetcher import get_stock_news
from services.market_data import get_stock_data

router = APIRouter()

@router.get("/news/{symbol}")
def get_news(
    symbol: str = Path(..., description="NSE stock symbol e.g. RELIANCE")
):
    """
    Get recent news for a stock
    GET /api/news/RELIANCE
    """
    # Normalize symbol
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    # Get company name for better news search
    stock_data = get_stock_data(symbol)
    company_name = stock_data.get("name", "") if "error" not in stock_data else ""

    news = get_stock_news(symbol, company_name)

    if not news:
        return {
            "symbol": symbol,
            "company": company_name,
            "count": 0,
            "articles": [],
            "message": "No recent news found"
        }

    return {
        "symbol": symbol,
        "company": company_name,
        "count": len(news),
        "articles": news
    }