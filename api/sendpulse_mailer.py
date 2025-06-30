import json
import os
from django.conf import settings
import requests
from datetime import datetime, timedelta, timezone
import base64


TOKEN_FILE = 'token.txt'
API_BASE = 'https://api.sendpulse.com'


def get_access_token():
    """Gets or updates access token and saves it to token.txt"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            expire_time = datetime.strptime(token_data['expires_at'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) < expire_time:
                return token_data['access_token']

    # Getting new token
    resp = requests.post(
        f'{API_BASE}/oauth/access_token',
        data={
            'grant_type': 'client_credentials',
            'client_id': settings.SENDPULSE_CLIENT_ID,
            'client_secret': settings.SENDPULSE_CLIENT_SECRET,
        }
    )
    resp.raise_for_status()
    token_info = resp.json()
    access_token = token_info['access_token']
    expires_in = token_info['expires_in']

    token_data = {
        'access_token': access_token,
        'expires_at': (datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)).strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)

    return access_token


def send_mail(subject, message=None, from_email=settings.SENDPULSE_FROM_EMAIL, recipient_list=[], html_message=None):
    """Sending mail with SendPulse"""
    access_token = get_access_token()

    payload = {
        "email": {
            "from": {
                "name": settings.SENDPULSE_FROM_LABEL,
                "email": from_email,
            },
            "to": [{"email": r} for r in recipient_list],
            "subject": subject,
            "text": message
        }
    }

    if html_message:
        encoded_html = base64.b64encode(html_message.encode('utf-8')).decode('utf-8')
        payload["email"]["html"] = encoded_html

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(f"{API_BASE}/smtp/emails", headers=headers, json=payload)
    response.raise_for_status()
    return response.json().get('result', False)