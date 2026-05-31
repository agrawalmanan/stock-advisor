import json
import os

# Load sector risk scores
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SECTOR_RISK_PATH = os.path.join(_BASE_DIR, "data", "sector_risk.json")

with open(_SECTOR_RISK_PATH, "r") as f:
    SECTOR_RISK = json.load(f)


def calculate_risk(
    beta,
    sector: str,
    week_52_high,
    week_52_low,
    current_price
) -> dict:
    """
    Calculate risk score (0-100) and level (Low/Medium/High)
    Based on: beta + sector risk + 52wk volatility
    """
    score = 0
    weights = {"beta": 40, "sector": 35, "volatility": 25}

    # --- Beta Score (0-40) ---
    try:
        beta = float(beta)
        if beta <= 0.5:
            beta_score = 10
        elif beta <= 1.0:
            beta_score = 20
        elif beta <= 1.5:
            beta_score = 30
        else:
            beta_score = 40
    except (TypeError, ValueError):
        beta_score = 20  # default medium
    score += beta_score

    # --- Sector Risk Score (0-35) ---
    sector_base = SECTOR_RISK.get(sector, 50)
    sector_score = int((sector_base / 100) * weights["sector"])
    score += sector_score

    # --- 52 Week Volatility Score (0-25) ---
    try:
        high = float(week_52_high)
        low = float(week_52_low)
        price = float(current_price)
        if high > 0 and low > 0:
            volatility_pct = ((high - low) / low) * 100
            if volatility_pct < 20:
                vol_score = 5
            elif volatility_pct < 40:
                vol_score = 12
            elif volatility_pct < 60:
                vol_score = 18
            else:
                vol_score = 25
        else:
            vol_score = 12
    except (TypeError, ValueError):
        vol_score = 12
    score += vol_score

    # --- Map score to level ---
    if score <= 35:
        level = "Low"
        color = "green"
    elif score <= 60:
        level = "Medium"
        color = "yellow"
    else:
        level = "High"
        color = "red"

    return {
        "score": score,
        "level": level,
        "color": color,
        "max_score": 100
    }