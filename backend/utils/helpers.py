import time


def retry_on_rate_limit(func, max_retries=3, initial_delay=2):
    """
    Retry a function if it hits rate limits
    Exponential backoff: 2s, 4s, 8s
    """
    for attempt in range(max_retries):
        try:
            result = func()
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "too many" in error_msg or "429" in error_msg:
                delay = initial_delay * (2 ** attempt)
                print(f"[RATE LIMIT] Attempt {attempt + 1}/{max_retries}, waiting {delay}s...")
                time.sleep(delay)
            else:
                raise e

    # Last attempt without catching
    return func()

def format_market_cap(value: float) -> str:
    """Convert raw market cap number to readable Indian format"""
    if value is None:
        return "N/A"
    if value >= 1_00_00_00_00_000:  # 1 Lakh Crore+
        return f"₹{value / 1_00_00_00_00_000:.2f}L Cr"
    elif value >= 1_00_00_00_000:  # 1000 Crore+
        return f"₹{value / 1_00_00_00_000:.2f} Cr"
    elif value >= 1_00_00_000:  # 1 Crore+
        return f"₹{value / 1_00_00_000:.2f} Cr"
    else:
        return f"₹{value:,.0f}"


def format_volume(value: float) -> str:
    """Convert volume to readable format"""
    if value is None:
        return "N/A"
    if value >= 1_00_00_000:
        return f"{value / 1_00_00_000:.2f} Cr"
    elif value >= 1_00_000:
        return f"{value / 1_00_000:.2f} L"
    else:
        return f"{value:,.0f}"


def safe_round(value, digits=2):
    """Safely round a value, return N/A if None"""
    try:
        if value is None:
            return "N/A"
        return round(float(value), digits)
    except (TypeError, ValueError):
        return "N/A"


def safe_get(dictionary: dict, *keys, default="N/A"):
    """Safely get nested dict value"""
    try:
        result = dictionary
        for key in keys:
            result = result[key]
        if result is None:
            return default
        return result
    except (KeyError, TypeError):
        return default