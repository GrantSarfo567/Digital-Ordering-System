from app.core.supabase import supabase

def send_otp(phone: str):
    response = supabase.auth.sign_in_with_otp({"phone": phone})
    return response

def verify_otp(phone: str, token: str):
    response = supabase.auth.sign_in_with_otp({
        "phone": phone,
        "token": token,
        "type": "sms"
    })
    return response