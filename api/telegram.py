import requests
from django.conf import settings

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

def send_telegram_message(message):
    print(message)
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Повідомлення надіслано в Telegram-групу")
        return 1
    except requests.exceptions.RequestException as e:
        print(f"❌ Помилка надсилання повідомлення в Telegram: {e}")
        return 0