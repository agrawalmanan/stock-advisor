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