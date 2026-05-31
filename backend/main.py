from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from routers import search, stock, analysis, news, advice, company, peers, financials, alerts

load_dotenv()

# Background scheduler for price alerts
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from services.alert_checker import check_alerts
    scheduler.add_job(check_alerts, 'interval', minutes=5, id='price_alert_checker')
    scheduler.start()
    print("[SCHEDULER] Price alert checker started — runs every 5 minutes")
    yield
    # Shutdown
    scheduler.shutdown()
    print("[SCHEDULER] Shutdown")


app = FastAPI(
    title="Indian Stock Advisor API",
    description="Live stock data, technical analysis and AI advice for NSE stocks",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://stock-advisor-lilac.vercel.app",  # will update after deploy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routers
app.include_router(search.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(advice.router, prefix="/api")

# New routers
app.include_router(company.router, prefix="/api")
app.include_router(peers.router, prefix="/api")
app.include_router(financials.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")    

@app.get("/")
def root():
    return {"message": "Stock Advisor API is running"}

@app.get("/debug/fundamentals/{symbol}")
def debug_fundamentals(symbol: str):
    import requests

    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    results = {}

    # Test v8 chart API
    try:
        r = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            headers=headers, timeout=10
        )
        results["v8_chart"] = {
            "status": r.status_code,
            "works": r.status_code == 200
        }
        if r.status_code == 200:
            data = r.json()
            meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
            results["v8_data"] = {
                "price": meta.get("regularMarketPrice"),
                "name": meta.get("longName"),
            }
    except Exception as e:
        results["v8_chart"] = {"error": str(e)}

    # Test v6 quote
    try:
        r = requests.get(
            f"https://query1.finance.yahoo.com/v6/finance/quote?symbols={symbol}",
            headers=headers, timeout=10
        )
        results["v6_query1"] = {"status": r.status_code}
        if r.status_code == 200:
            q = r.json().get("quoteResponse", {}).get("result", [{}])[0]
            results["v6_data"] = {
                "marketCap": q.get("marketCap"),
                "trailingPE": q.get("trailingPE"),
                "beta": q.get("beta"),
            }
    except Exception as e:
        results["v6_query1"] = {"error": str(e)}

    # Test v6 query2
    try:
        r = requests.get(
            f"https://query2.finance.yahoo.com/v6/finance/quote?symbols={symbol}",
            headers=headers, timeout=10
        )
        results["v6_query2"] = {"status": r.status_code}
        if r.status_code == 200:
            q = r.json().get("quoteResponse", {}).get("result", [{}])[0]
            results["v6_query2_data"] = {
                "marketCap": q.get("marketCap"),
                "trailingPE": q.get("trailingPE"),
                "beta": q.get("beta"),
            }
    except Exception as e:
        results["v6_query2"] = {"error": str(e)}

    # Test v7 query1
    try:
        r = requests.get(
            f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}",
            headers=headers, timeout=10
        )
        results["v7_query1"] = {"status": r.status_code}
    except Exception as e:
        results["v7_query1"] = {"error": str(e)}

    # Test v7 query2
    try:
        r = requests.get(
            f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={symbol}",
            headers=headers, timeout=10
        )
        results["v7_query2"] = {"status": r.status_code}
        if r.status_code == 200:
            q = r.json().get("quoteResponse", {}).get("result", [{}])[0]
            results["v7_query2_data"] = {
                "marketCap": q.get("marketCap"),
                "trailingPE": q.get("trailingPE"),
                "beta": q.get("beta"),
            }
    except Exception as e:
        results["v7_query2"] = {"error": str(e)}

    return results