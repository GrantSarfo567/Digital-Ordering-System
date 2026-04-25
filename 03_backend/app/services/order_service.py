from app.core.supabase import supabase
import math
from collections import defaultdict
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.supabase import supabase


# -----------------------------
# Utilities
# -----------------------------

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    if None in [lat1, lng1, lat2, lng2]:
        raise ValueError("Invalid coordinates: None value found")

    R = 6371  # Earth's radius in km

    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_delivery_fee(distance_km: float) -> float:
    if distance_km is None:
        raise ValueError("Distance cannot be None")

    if distance_km < 0:
        raise ValueError("Distance cannot be negative")

    if distance_km <= 0.45:
        return 3.00
    elif distance_km <= 0.75:
        return 4.00
    elif distance_km <= 1.0:
        return 5.00
    elif distance_km <= 1.3:
        return 6.00
    elif distance_km <= 1.6:
        return 7.00
    elif distance_km <= 2:
        return 8.00
    elif distance_km <= 3:
        return 10.00
    elif distance_km <= 5.6:
        return 12.00
    elif distance_km <= 7:
        return 15.00
    elif distance_km <= 9:
        return 18.00
    else:
        raise Exception("Sorry, you are outside our delivery zone")


# -----------------------------
# Core Logic
# -----------------------------

def create_order(user_id: str, data: dict) -> dict:
    # 1. Validate input
    if not data or not isinstance(data, dict):
        raise Exception("Invalid request data")

    if not data.get("items"):
        raise Exception("Order must contain at least one item")

    if "delivery_lat" not in data or "delivery_lng" not in data:
        raise Exception("Delivery coordinates required")

    lat = data["delivery_lat"]
    lng = data["delivery_lng"]

    if lat is None or lng is None:
        raise Exception("Delivery coordinates cannot be null")

    if not (-90 <= lat <= 90):
        raise Exception("Invalid latitude")

    if not (-180 <= lng <= 180):
        raise Exception("Invalid longitude")

    # 2. Aggregate items
    aggregated_items = defaultdict(int)

    for item in data["items"]:
        if "menu_item_id" not in item or "quantity" not in item:
            raise Exception("Invalid item structure")

        qty = int(item["quantity"])
        if qty <= 0 or qty > 100:
            raise Exception("Invalid quantity")

        aggregated_items[str(item["menu_item_id"])] += qty

    menu_item_ids = list(aggregated_items.keys())

    # 3. Fetch restaurant
    restaurant = (
        supabase.table("restaurants")
        .select("id, latitude, longitude")
        .eq("id", data["restaurant_id"])
        .single()
        .execute()
    )

    if not restaurant.data:
        raise Exception("Restaurant not found")

    rest_lat = restaurant.data.get("latitude")
    rest_lng = restaurant.data.get("longitude")

    if rest_lat is None or rest_lng is None:
        raise Exception("Restaurant location is not set")

    # 4. Fetch menu items
    menu_items_response = (
        supabase.table("menu_items")
        .select("id, price, name, size")
        .in_("id", menu_item_ids)
        .execute()
    )

    menu_items = menu_items_response.data or []

    if len(menu_items) != len(menu_item_ids):
        raise Exception("Some menu items not found")

    menu_map = {item["id"]: item for item in menu_items}

    # 5. Compute totals
    food_total = 0.0
    validated_items = []

    for menu_item_id, quantity in aggregated_items.items():
        menu_item = menu_map[menu_item_id]

        price = menu_item.get("price")

        if price is None:
            raise Exception(f"Menu item '{menu_item.get('name')}' has no price set")

        price = float(price)

        subtotal = price * quantity
        food_total += subtotal

        validated_items.append({
            "menu_item_id": menu_item_id,
            "quantity": quantity,
            "price": price,
            "name": menu_item.get("name"),
            "size": menu_item.get("size")
        })

    # 6. Delivery
    distance = calculate_distance(lat, lng, rest_lat, rest_lng)
    delivery_fee = calculate_delivery_fee(distance)

    grand_total = round(food_total + delivery_fee, 2)

    # 7. Create order (RPC)
    rpc_response = supabase.rpc("create_order_atomic", {
        "p_user_id": user_id,
        "p_restaurant_id": data["restaurant_id"],
        "p_total": grand_total,
        "p_delivery_fee": delivery_fee,
        "p_delivery_lat": lat,
        "p_delivery_lng": lng,
        "p_delivery_location": data.get("delivery_location"),
        "p_items": validated_items,
        "p_payment_method": data["payment_method"],
    }).execute()

    if not rpc_response.data:
        raise Exception("Failed to create order")

    order_id = rpc_response.data["order_id"]

    return {
        "id": order_id,
        "user_id": user_id,
        "restaurant_id": data["restaurant_id"],
        "total": grand_total,
        "delivery_fee": delivery_fee,
        "status": "PENDING",
        "delivery_lat": lat,
        "delivery_lng": lng,
        "delivery_location": data.get("delivery_location"),
        "items": validated_items,
        "distance_km": round(distance, 2),
        
    }


# -----------------------------
# Get single order (FIXED)
# -----------------------------

def get_order(order_id: str) -> dict:
    response = (
        supabase.table("orders")
        .select("*, order_items(*)")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not response.data:
        raise Exception("Order not found")

    return response.data


# -----------------------------
# Get order history
# -----------------------------

def get_order_history(user_id: str) -> list:
    response = (
        supabase.table("orders")
        .select("*, order_items(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


# -----------------------------
# Update order status
# -----------------------------

def update_order_status(order_id: str, new_status: str, user_id: str) -> dict:
    # Normalize
    new_status = new_status.upper()

    # -------------------------
    # GET ORDER
    # -------------------------
    order_response = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not order_response.data:
        raise HTTPException(status_code=404, detail="Order not found")

    order = order_response.data
    current_status = order["status"].upper()

    # -------------------------
    # GET USER ROLE
    # -------------------------
    user_response = (
        supabase.table("users")
        .select("role")
        .eq("id", user_id)
        .single()
        .execute()
    )

    if not user_response.data:
        raise HTTPException(status_code=404, detail="User not found")

    role = user_response.data["role"]

    # -------------------------
    # VALID TRANSITIONS
    # -------------------------
    valid_transitions = {
        "PENDING": ["PAID", "CONFIRMED", "CANCELLED"],
        "PAID": ["CONFIRMED"],
        "CONFIRMED": ["PREPARING", "CANCELLED"],
        "PREPARING": ["OUT_FOR_DELIVERY"],
        "OUT_FOR_DELIVERY": ["DELIVERED"],
        "DELIVERED": [],
        "CANCELLED": [],
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} to {new_status}"
        )

    # -------------------------
    # ROLE RULES
    # -------------------------
    if new_status in ["CONFIRMED", "PREPARING", "OUT_FOR_DELIVERY"]:
        if role not in ["admin", "developer"]:
            raise HTTPException(
                status_code=403,
                detail="Only admin can perform this action"
            )

    if new_status == "DELIVERED":
        if role not in ["rider", "developer"]:
            raise HTTPException(
                status_code=403,
                detail="Only rider can mark as delivered"
            )

    # -------------------------
    # TIMESTAMP HANDLING
    # -------------------------
    now = datetime.now(timezone.utc).isoformat()

    update_data = {
        "status": new_status,
        "updated_at": now
    }

    if new_status == "PAID" and not order.get("paid_at"):
        update_data["paid_at"] = now

    elif new_status == "CONFIRMED" and not order.get("confirmed_at"):
        update_data["confirmed_at"] = now

    elif new_status == "PREPARING" and not order.get("preparing_at"):
        update_data["preparing_at"] = now

    elif new_status == "OUT_FOR_DELIVERY" and not order.get("out_for_delivery_at"):
        update_data["out_for_delivery_at"] = now

    elif new_status == "DELIVERED" and not order.get("delivered_at"):
        update_data["delivered_at"] = now

    elif new_status == "CANCELLED" and not order.get("cancelled_at"):
        update_data["cancelled_at"] = now

    # -------------------------
    # UPDATE ORDER
    # -------------------------
    updated = (
        supabase.table("orders")
        .update(update_data)
        .eq("id", order_id)
        .execute()
    )

    if not updated.data:
        raise HTTPException(status_code=500, detail="Failed to update order")

    return updated.data[0]