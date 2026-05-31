import time
import threading

_lock = threading.Lock()
_last_call_time = 0
MIN_INTERVAL = 2.5  # 2.5 seconds between Yahoo calls


def rate_limit():
    global _last_call_time

    with _lock:
        now = time.time()
        elapsed = now - _last_call_time

        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)

        _last_call_time = time.time()