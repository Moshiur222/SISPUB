# views.py (backend)
import random
import hashlib
import requests
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import  HttpResponseRedirect
from .models import TempMember # adjust imports as needed

SMS_API_URL = "http://sms.iglweb.com/api/v1/send"
SMS_API_KEY = "4451764741797151764741797"
SMS_SENDER_ID = "01844532630"

import re

def normalize_phone(mobile):
    if not mobile:
        return None
    cleaned = re.sub(r'\D', '', str(mobile))
    if len(cleaned) == 11 and cleaned.startswith('01'):
        return '88' + cleaned
    if len(cleaned) == 13 and cleaned.startswith('8801'):
        return cleaned
    return None

def send_sms(mobile, message):
    try:
        phone = normalize_phone(mobile)
        
        if not phone:
            # Using f-string to see the actual malformed input
            print(f"SMS Failed: '{mobile}' is an invalid phone number format")
            return False
            
        print(f"Attempting to send SMS to: {phone}")
        
        payload = {
            "api_key": SMS_API_KEY,
            "contacts": phone, 
            "senderid": SMS_SENDER_ID,
            "msg": message
        }
        
        response = requests.post(SMS_API_URL, data=payload, timeout=10)
        
        if response.status_code == 200:
            try:
                resp_json = response.json()
                # IGL success code is often "445000"
                if str(resp_json.get("code")) == "445000":
                    print(f"OTP sent successfully to {phone}")
                    return True
                else:
                    print(f"IGL API Error: {resp_json}")
                    return False
            except ValueError:
                # Fallback if API returns plain text instead of JSON
                if "success" in response.text.lower() or "445000" in response.text:
                    return True
                print(f"Non-JSON response from IGL: {response.text}")
                return False
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Unexpected Error in send_sms: {e}")
        return False

def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

@csrf_exempt
def resend_otp(request):
    if request.method == "POST":
        phone = normalize_phone(request.POST.get("phone"))
        try:
            temp = TempMember.objects.get(phone=phone)
        except TempMember.DoesNotExist:
            messages.error(request, "Invalid request.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/registration/'))

        # Generate new OTP
        otp = str(random.randint(100000, 999999))
        temp.otp = hash_otp(otp)
        temp.otp_created_at = timezone.now()
        temp.save()

        if send_sms(phone, f"Your new OTP is {otp}"):
            messages.success(request, "OTP resent successfully.")
        else:
            messages.error(request, "Failed to resend OTP. Try again.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/registration/'))