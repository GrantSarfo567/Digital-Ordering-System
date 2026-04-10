from app.core.supabase import supabase

def send_otp(phone: str):
    response = supabase.auth.sign_in_with_otp({"phone": phone})
    return response

def verify_otp(phone: str, token: str):
    response = supabase.auth.verify_otp({
        "phone": phone,
        "token": token,
        "type": "sms"
    })
    return response

def get_or_create_user(user_id: str, phone: str, name: str = None):
    # Check if user already exists
    existing = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if existing.data:
        return existing.data[0]
    
    # Create new user if not found
    new_user = {
        "id": user_id,
        "phone": phone,
        "name": name
    }
    response = supabase.table("users").insert(new_user).execute()
    return response.data[0]