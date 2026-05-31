import requests
import os


def send_telegram_message(message: str, chat_id: str = None) -> bool:
    """
    Send a message via Telegram Bot
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN not set")
        return False

    if not chat_id:
        chat_id = os.getenv("TELEGRAM_DEFAULT_CHAT_ID")

    if not chat_id:
        print("No chat_id provided")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if data.get("ok"):
            print(f"[TELEGRAM] Message sent to {chat_id}")
            return True
        else:
            print(f"[TELEGRAM] Error: {data}")
            return False

    except Exception as e:
        print(f"[TELEGRAM] Send error: {e}")
        return False


def send_price_alert(
    stock_name: str,
    symbol: str,
    target_price: float,
    current_price: float,
    alert_type: str,
    chat_id: str = None
) -> bool:
    """
    Send a formatted price alert message
    """
    emoji = "🟢" if alert_type == "above" else "🔴"
    direction = "above" if alert_type == "above" else "below"

    message = f"""
{emoji} <b>PRICE ALERT TRIGGERED!</b>

<b>Stock:</b> {stock_name} ({symbol.replace('.NS', '')})
<b>Alert Type:</b> Price went {direction} target
<b>Target Price:</b> ₹{target_price:.2f}
<b>Current Price:</b> ₹{current_price:.2f}

⏰ <i>Alert triggered just now</i>
📊 <a href="https://www.google.com/finance/quote/{symbol.replace('.NS', '')}:NSE">View on Google Finance</a>
"""

    return send_telegram_message(message.strip(), chat_id)

def send_welcome_message(chat_id: str, user_name: str) -> bool:
    """Send welcome message when user connects Telegram"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return False

    message = f"""
✅ <b>Telegram Connected!</b>

Hi {user_name}! 👋

You're now connected to <b>StockAdvisor Alerts</b>.

📊 How it works:
• Set price alerts on any stock page
• When price hits your target → you get instant notification here
• Manage alerts from the Portfolio page

You can disconnect anytime by sending /stop to this bot.

Happy investing! 🚀
"""

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("ok", False)
    except Exception:
        return False