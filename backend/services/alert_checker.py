import json
import os
import time
import yfinance as yf
from services.telegram_bot import send_price_alert
from utils.helpers import safe_round

ALERTS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "alerts.json"
)


def load_alerts() -> list:
    """Load alerts from JSON file"""
    try:
        if os.path.exists(ALERTS_FILE):
            with open(ALERTS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading alerts: {e}")
    return []


def save_alerts(alerts: list):
    """Save alerts to JSON file"""
    try:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
    except Exception as e:
        print(f"Error saving alerts: {e}")


def get_user_chat_id(user_id: str) -> str:
    """Get Telegram chat ID for a user from Firestore"""
    try:
        from firebase_admin import firestore
        db = firestore.client()
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            return data.get('telegram_chat_id') or os.getenv("TELEGRAM_DEFAULT_CHAT_ID")
    except Exception as e:
        print(f"Error getting chat_id for {user_id}: {e}")
    return os.getenv("TELEGRAM_DEFAULT_CHAT_ID")


def add_alert(
    symbol: str,
    stock_name: str,
    target_price: float,
    alert_type: str,
    user_id: str = "default",
    chat_id: str = None
):
    """Add alert — uses user's chat_id from Firestore if available"""
    alerts = load_alerts()

    # Resolve chat_id: user-specific > provided > default
    if not chat_id:
        chat_id = get_user_chat_id(user_id)

    alert = {
        "id": f"{symbol}_{alert_type}_{target_price}_{int(time.time())}",
        "symbol": symbol,
        "stock_name": stock_name,
        "target_price": target_price,
        "alert_type": alert_type,
        "chat_id": chat_id,
        "user_id": user_id,
        "active": True,
        "triggered": False,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "triggered_at": None
    }

    alerts.append(alert)
    save_alerts(alerts)
    print(f"[ALERT] Added: {stock_name} {alert_type} ₹{target_price} → chat {chat_id}")
    return alert


def remove_alert(alert_id: str) -> bool:
    """Remove an alert by ID"""
    alerts = load_alerts()
    alerts = [a for a in alerts if a["id"] != alert_id]
    save_alerts(alerts)
    print(f"[ALERT] Removed: {alert_id}")
    return True


def get_user_alerts(user_id: str = None) -> list:
    """Get all alerts, optionally filtered by user"""
    alerts = load_alerts()
    if user_id:
        return [a for a in alerts if a.get("user_id") == user_id]
    return alerts


def check_alerts():
    """
    Check all active alerts against current prices
    Called periodically by the scheduler
    """
    alerts = load_alerts()
    active_alerts = [a for a in alerts if a.get("active") and not a.get("triggered")]

    if not active_alerts:
        return

    print(f"[ALERT CHECKER] Checking {len(active_alerts)} active alerts...")

    # Group by symbol to minimize API calls
    symbols = list(set(a["symbol"] for a in active_alerts))

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current_price = info.get("regularMarketPrice") or info.get("currentPrice")

            if not current_price:
                continue

            current_price = float(current_price)

            # Check each alert for this symbol
            symbol_alerts = [a for a in active_alerts if a["symbol"] == symbol]

            for alert in symbol_alerts:
                target = float(alert["target_price"])
                alert_type = alert["alert_type"]
                triggered = False

                if alert_type == "above" and current_price >= target:
                    triggered = True
                elif alert_type == "below" and current_price <= target:
                    triggered = True

                if triggered:
                    print(f"[ALERT TRIGGERED] {alert['stock_name']} hit ₹{current_price} (target: {alert_type} ₹{target})")

                    # Send Telegram notification
                    send_price_alert(
                        stock_name=alert["stock_name"],
                        symbol=symbol,
                        target_price=target,
                        current_price=current_price,
                        alert_type=alert_type,
                        chat_id=get_user_chat_id(alert.get("user_id", "default"))
                    )

                    # Mark as triggered
                    alert["triggered"] = True
                    alert["active"] = False
                    alert["triggered_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            print(f"[ALERT CHECKER] Error checking {symbol}: {e}")

    # Save updated alerts
    save_alerts(alerts)