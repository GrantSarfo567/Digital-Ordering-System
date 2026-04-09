from app.core.supabase import supabase

def create_restaurant(data: dict):
    response = supabase.table("restaurants").insert(data).execute()
    return response.data[0]

def get_restaurant(restaurant_id: str):
    response = supabase.table("restaurants").select("*").eq("id", restaurant_id).single().execute()
    return response.data

def update_restaurant(restaurant_id: str, data: dict):
    response = supabase.table("restaurants").update(data).eq("id", restaurant_id).execute()
    return response.data[0]

def deactivate_restaurant(restaurant_id: str):
    response = supabase.table("restaurants").update({"is_active": False}).eq("id", restaurant_id).execute()
    return response.data[0]