import random
import hashlib
import requests
import re
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from .models import *


SMS_API_URL = "http://sms.iglweb.com/api/v1/send"
SMS_API_KEY = "4451764741797151764741797"
SMS_SENDER_ID = "01844532630"


# ------------------ PHONE NORMALIZE ------------------
def normalize_phone(mobile):
    if not mobile:
        return None

    cleaned = re.sub(r'\D', '', str(mobile))

    if len(cleaned) == 11 and cleaned.startswith('01'):
        return '88' + cleaned

    if len(cleaned) == 13 and cleaned.startswith('8801'):
        return cleaned

    return None


# ------------------ SEND SMS ------------------
def send_sms(mobile, message):
    try:
        phone = normalize_phone(mobile)

        if not phone:
            print(f"Invalid phone format: {mobile}")
            return False

        payload = {
            "api_key": SMS_API_KEY,
            "contacts": phone,
            "senderid": SMS_SENDER_ID,
            "msg": message
        }

        response = requests.post(SMS_API_URL, data=payload, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                if str(data.get("code")) == "445000":
                    print(f"SMS sent to {phone}")
                    return True
                else:
                    print("API error:", data)
                    return False
            except:
                if "success" in response.text.lower():
                    return True
                return False
        else:
            print("HTTP error:", response.text)
            return False

    except Exception as e:
        print("SMS Error:", e)
        return False


# ------------------ HASH OTP ------------------
def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()


# ================== RESEND OTP (SEPARATE API) ==================
@csrf_exempt
def resend_otp(request):
    if request.method == "POST":

        phone = normalize_phone(request.POST.get("phone"))

        try:
            temp = TempMember.objects.get(phone=phone)
        except TempMember.DoesNotExist:
            messages.error(request, "Invalid request.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/registration/'))

        otp = str(random.randint(100000, 999999))
        temp.otp = hash_otp(otp)
        temp.otp_created_at = timezone.now()
        temp.save()

        if send_sms(phone, f"Your OTP is {otp}"):
            messages.success(request, "OTP resent successfully.")
        else:
            messages.error(request, "Failed to resend OTP.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/registration/'))