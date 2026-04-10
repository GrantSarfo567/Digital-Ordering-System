from app.core.supabase import supabase

def create_menu_item(restaurant_id: str, data: dict):
    data["restaurant_id"] = restaurant_id
    response = supabase.table("menu_items").insert(data).execute()
    return response.data[0]

def get_menu_items(restaurant_id: str):
    response = supabase.table("menu_items").select("*").eq("restaurant_id", restaurant_id).eq("is_available", True).execute()
    return response.data

def get_menu_item(menu_item_id: str):
    response = supabase.table("menu_items").select("*").eq("id", menu_item_id).single().execute()
    return response.data

def update_menu_item(menu_item_id: str, data: dict):
    response = supabase.table("menu_items").update(data).eq("id", menu_item_id).execute()
    return response.data[0]

def delete_menu_item(menu_item_id: str):
    response = supabase.table("menu_items").update({"is_available": False}).eq("id", menu_item_id).execute()
    return response.data[0]