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