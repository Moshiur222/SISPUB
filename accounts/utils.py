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

def normalize_phone(phone):
    if not phone:
        return None

    phone = phone.strip().replace(" ", "")
    
    # Remove '+' if present
    phone = phone.replace('+', '')
    
    if phone.startswith("01") and len(phone) == 11:
        return "88" + phone  # Add BD country code without '+'
    
    if phone.startswith("8801") and len(phone) == 13:
        return phone  # Already has 880 without '+'
    
    if phone.startswith("+8801") and len(phone) == 14:
        return phone[1:]  # Remove the '+'
    
    return None

def send_sms(phone, message):
    """
    Send SMS using IGL SMS API
    """
    try:
        phone = normalize_phone(phone)
        if not phone:
            print("SMS Failed: Invalid phone number format")
            return False
            
        print(f"Attempting to send SMS to: {phone}")
        print(f"Message: {message}")
        print(f"API URL: {SMS_API_URL}")
        
        payload = {
            "api_key": SMS_API_KEY,
            "contacts": phone,
            "senderid": SMS_SENDER_ID,
            "msg": message
        }
        
        print(f"Payload: {payload}")
        
        response = requests.post(SMS_API_URL, data=payload, timeout=10)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        try:
            resp_json = response.json()
            print(f"Response JSON: {resp_json}")
            
            if response.status_code == 200 and resp_json.get("code") == "445000":
                print(f"OTP sent successfully to {phone}")
                return True
            else:
                print(f"SMS API returned error: {resp_json}")
                return False
        except ValueError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to SMS API - {e}")
        print("Check if the API URL is correct and accessible")
        return False
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: SMS API took too long to respond - {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error in send_sms: {e}")
        import traceback
        traceback.print_exc()
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
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/register/'))

        # Generate new OTP
        otp = str(random.randint(100000, 999999))
        temp.otp = hash_otp(otp)
        temp.otp_created_at = timezone.now()
        temp.save()

        if send_sms(phone, f"Your new OTP is {otp}"):
            messages.success(request, "OTP resent successfully.")
        else:
            messages.error(request, "Failed to resend OTP. Try again.")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/register/'))