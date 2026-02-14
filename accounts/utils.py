import requests
from django.conf import settings


def send_sms(phone, message):
    """
    Send SMS using IGLWEB / FelnaDMA SMS API
    phone format: 88017XXXXXXXX
    """
    payload = {
        "api_key": settings.SMS_API_KEY,
        "contacts": phone,
        "senderid": settings.SMS_SENDER_ID,
        "msg": message,
    }

    try:
        response = requests.post(
            settings.SMS_SEND_URL,
            data=payload,
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
