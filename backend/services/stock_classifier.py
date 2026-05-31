def classify_stock(beta, avg_volume, volume, sector: str) -> dict:
    """
    Classify stock as better for Delivery or Intraday trading
    Based on: beta, volume patterns, sector
    """
    score = 0  # higher = more intraday suitable

    # --- Beta check ---
    try:
        beta = float(beta)
        if beta > 1.3:
            score += 3  # high beta = volatile = intraday friendly
        elif beta > 1.0:
            score += 2
        elif beta > 0.7:
            score += 1
    except (TypeError, ValueError):
        score += 1

    # --- Volume check ---
    try:
        avg_vol = float(avg_volume)
        if avg_vol > 5_000_000:
            score += 3  # high liquidity = intraday friendly
        elif avg_vol > 1_000_000:
            score += 2
        elif avg_vol > 500_000:
            score += 1
    except (TypeError, ValueError):
        score += 1

    # --- Sector check ---
    intraday_sectors = ["Metals & Mining", "Aviation", "Real Estate", "Conglomerate"]
    delivery_sectors = ["FMCG", "Pharmaceuticals", "Information Technology"]

    if sector in intraday_sectors:
        score += 2
    elif sector in delivery_sectors:
        score -= 1

    # --- Decision ---
    if score >= 6:
        return {
            "type": "Intraday",
            "label": "Intraday Suitable",
            "description": "High volatility & liquidity makes this stock suitable for short-term intraday trading",
            "color": "orange"
        }
    elif score >= 3:
        return {
            "type": "Both",
            "label": "Delivery & Intraday",
            "description": "This stock is suitable for both delivery and intraday trading",
            "color": "blue"
        }
    else:
        return {
            "type": "Delivery",
            "label": "Delivery (Long-term)",
            "description": "Low volatility & stable growth makes this stock better for long-term delivery",
            "color": "green"
        }