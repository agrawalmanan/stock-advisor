import time
import yfinance as yf
from utils.rate_limiter import rate_limit

try:
    from curl_cffi import requests as curl_requests

    _session = curl_requests.Session(impersonate="chrome")
    _session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    })
except Exception as e:
    print(f"[YF SESSION] Failed to create browser session: {e}")
    _session = None


def get_ticker(symbol: str):
    rate_limit()
    if _session is not None:
        return yf.Ticker(symbol, session=_session)
    return yf.Ticker(symbol)


def with_retries(fn, max_retries=3, base_delay=2):
    last_error = None

    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            last_error = e
            msg = str(e).lower()

            if "too many requests" in msg or "rate" in msg or "429" in msg:
                wait = base_delay * (attempt + 1)
                print(f"[YF RETRY] Attempt {attempt + 1}/{max_retries}, waiting {wait}s...")
                time.sleep(wait)
                continue

            raise

    raise last_error    