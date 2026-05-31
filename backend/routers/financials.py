from fastapi import APIRouter

router = APIRouter()

@router.get("/financials/{symbol}")
def get_financials(symbol: str):
    """Placeholder — will be built in Phase 5I"""
    return {"message": "Coming soon", "symbol": symbol}