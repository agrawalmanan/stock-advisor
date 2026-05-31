import time
import threading

_lock = threading.Lock()
_last_call_time = 0
MIN_INTERVAL = 2.0  # increase to 2 seconds between calls


def rate_limit():
    global _last_call_time

    with _lock:
        now = time.time()
        elapsed = now - _last_call_time

        if elapsed < MIN_INTERVAL:
            sleep_time = MIN_INTERVAL - elapsed
            time.sleep(sleep_time)

        _last_call_time = time.time()