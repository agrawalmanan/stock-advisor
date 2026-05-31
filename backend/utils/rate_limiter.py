import time
import threading

_lock = threading.Lock()
_last_call_time = 0
MIN_INTERVAL = 1.0  # minimum 1 second between yfinance calls


def rate_limit():
    """
    Ensures minimum interval between yfinance API calls
    Prevents rate limiting from Yahoo Finance
    """
    global _last_call_time

    with _lock:
        now = time.time()
        elapsed = now - _last_call_time

        if elapsed < MIN_INTERVAL:
            sleep_time = MIN_INTERVAL - elapsed
            time.sleep(sleep_time)

        _last_call_time = time.time()