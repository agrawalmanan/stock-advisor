from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.alert_checker import add_alert, remove_alert, get_user_alerts, check_alerts
from services.telegram_bot import send_telegram_message
import os

router = APIRouter()

class TelegramConnectRequest(BaseModel):
    uid: str
    chat_id: str
    first_name: str = "User"

class AlertRequest(BaseModel):
    symbol: str
    stock_name: str
    target_price: float
    alert_type: str  # 'above' or 'below'
    user_id: str = "default"
    chat_id: str = None


class TestMessageRequest(BaseModel):
    message: str = "🔔 Test alert from StockAdvisor! Your alerts are working."
    chat_id: str = None


@router.get("/alerts")
def list_alerts(user_id: str = None):
    """
    Get all alerts, optionally filtered by user
    GET /api/alerts?user_id=xxx
    """
    alerts = get_user_alerts(user_id)
    return {
        "count": len(alerts),
        "alerts": alerts
    }


@router.post("/alerts")
def create_alert(req: AlertRequest):
    """
    Create a new price alert
    POST /api/alerts
    """
    if req.alert_type not in ["above", "below"]:
        raise HTTPException(status_code=400, detail="alert_type must be 'above' or 'below'")

    if req.target_price <= 0:
        raise HTTPException(status_code=400, detail="target_price must be positive")

    # Normalize symbol
    symbol = req.symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    alert = add_alert(
        symbol=symbol,
        stock_name=req.stock_name,
        target_price=req.target_price,
        alert_type=req.alert_type,
        chat_id=req.chat_id or os.getenv("TELEGRAM_DEFAULT_CHAT_ID", ""),
        user_id=req.user_id
    )

    return {"message": "Alert created successfully", "alert": alert}


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: str):
    """
    Delete an alert
    DELETE /api/alerts/{alert_id}
    """
    success = remove_alert(alert_id)
    if success:
        return {"message": "Alert removed successfully"}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/alerts/check")
def trigger_check():
    """
    Manually trigger alert check (for testing)
    POST /api/alerts/check
    """
    check_alerts()
    return {"message": "Alert check completed"}


@router.post("/alerts/test")
def test_telegram(req: TestMessageRequest):
    """
    Send a test Telegram message
    POST /api/alerts/test
    """
    success = send_telegram_message(
        message=req.message,
        chat_id=req.chat_id
    )

    if success:
        return {"message": "Test message sent successfully!"}
    raise HTTPException(status_code=500, detail="Failed to send message. Check bot token and chat ID.")

@router.post("/alerts/connect")
def connect_telegram(req: TelegramConnectRequest):
    """
    Connect Telegram account
    Called by bot when user sends /start
    POST /api/alerts/connect
    """
    try:
        from firebase_admin import firestore
        db = firestore.client()

        # Save chat_id to user's document
        db.collection('users').document(req.uid).set({
            'telegram_chat_id': req.chat_id,
            'telegram_first_name': req.first_name,
            'telegram_connected_at': time.strftime("%Y-%m-%d %H:%M:%S")
        }, merge=True)

        print(f"[TELEGRAM CONNECT] User {req.uid} connected with chat_id {req.chat_id}")

        # Send welcome message
        send_welcome_message(req.chat_id, req.first_name)

        return {
            "message": "Telegram connected successfully!",
            "chat_id": req.chat_id
        }

    except Exception as e:
        print(f"[TELEGRAM CONNECT] Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect Telegram")


@router.post("/alerts/disconnect")
def disconnect_telegram(req: TelegramConnectRequest):
    """
    Disconnect Telegram account
    POST /api/alerts/disconnect
    """
    try:
        from firebase_admin import firestore
        db = firestore.client()

        db.collection('users').document(req.uid).update({
            'telegram_chat_id': firestore.DELETE_FIELD,
            'telegram_first_name': firestore.DELETE_FIELD
        })

        send_telegram_message(
            f"✅ Telegram disconnected. You won't receive alerts anymore.\n\nConnect again anytime from the app.",
            req.chat_id
        )

        return {"message": "Telegram disconnected"}

    except Exception as e:
        print(f"[TELEGRAM DISCONNECT] Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to disconnect")