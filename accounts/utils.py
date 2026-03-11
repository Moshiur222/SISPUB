import random
import re
import hashlib
import requests
from django.core.cache import cache


SMS_API_URL = "http://sms.iglweb.com/api/v1/send"
SMS_API_KEY = "4451773204203151773204203"
SMS_SENDER_ID = "01844532630"


# ---------------- PHONE NORMALIZE ----------------
def normalize_phone(mobile):
    if not mobile:
        return None

    cleaned = re.sub(r'\D', '', str(mobile))

    if len(cleaned) == 11 and cleaned.startswith('01'):
        return '88' + cleaned

    if len(cleaned) == 13 and cleaned.startswith('8801'):
        return cleaned

    return None


# ---------------- OTP GENERATE ----------------
def generate_otp():
    otp = random.randint(100000, 999999)
    otp_str = str(otp)
    return f"{otp_str[:3]}-{otp_str[3:]}"


# ---------------- HASH OTP ----------------
def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()


# ---------------- SEND SMS ----------------
def send_sms(mobile, message):

    payload = {
        "api_key": SMS_API_KEY,
        "contacts": mobile,
        "senderid": SMS_SENDER_ID,
        "msg": message
    }

    try:
        response = requests.post(SMS_API_URL, data=payload, timeout=10)

        if response.status_code == 200:
            return True

        return False

    except Exception as e:
        print("SMS Error:", e)
        return False


# ---------------- SEND OTP ----------------
def send_otp(mobile):

    mobile = normalize_phone(mobile)

    if not mobile:
        return False, "Invalid phone number"

    otp_key = f"otp:{mobile}"
    otp_count_key = f"otp_count:{mobile}"

    # Check daily OTP limit
    otp_count = cache.get(otp_count_key, 0)

    if otp_count >= 2:
        return False, "OTP limit reached. Only 2 OTP allowed in 24 hours."

    # Check if OTP already exists
    if cache.get(otp_key):
        return False, "OTP already sent. Please wait 5 minutes."

    # Generate OTP
    otp = generate_otp()
    otp_clean = otp.replace("-", "")

    # Save OTP (5 minutes)
    cache.set(otp_key, hash_otp(otp_clean), timeout=300)

    # Increase daily count
    cache.set(otp_count_key, otp_count + 1, timeout=86400)

    # Send SMS
    if send_sms(mobile, f"""Welcome to SiSPAB, Your OTP Is: {otp}, Expire for 5 Min, Don't Share With Any One.
SISPAB.org"""):
        return True, otp

    return False, "Failed to send OTP"


# ---------------- RESEND OTP ----------------
def resend_otp(mobile):

    mobile = normalize_phone(mobile)

    if not mobile:
        return False, "Invalid phone number"

    otp_key = f"otp:{mobile}"

    # If previous OTP still valid
    if cache.get(otp_key):
        return False, "Please wait until OTP expires (5 minutes)."

    return send_otp(mobile)


# ---------------- VERIFY OTP ----------------
def verify_otp(mobile, user_otp):

    mobile = normalize_phone(mobile)

    if not mobile:
        return False, "Invalid phone number"

    otp_key = f"otp:{mobile}"

    saved_otp = cache.get(otp_key)

    if not saved_otp:
        return False, "OTP expired"

    user_otp = user_otp.replace("-", "")

    if hash_otp(user_otp) != saved_otp:
        return False, "Invalid OTP"

    # Delete OTP after success
    cache.delete(otp_key)

    return True, "OTP verified"