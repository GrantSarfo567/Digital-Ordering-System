from fastapi import APIRouter, Depends, HTTPException
from app.models.restaurant import RestaurantCreate, RestaurantResponse
from app.services.restaurant_service import (
    create_restaurant,
    get_restaurant,
    update_restaurant,
    deactivate_restaurant
)
from app.middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=RestaurantResponse)
def create(data: RestaurantCreate, current_user=Depends(get_current_user)):
    try:
        return create_restaurant(data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_one(restaurant_id: str):
    try:
        restaurant = get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update(restaurant_id: str, data: RestaurantCreate, current_user=Depends(get_current_user)):
    try:
        return update_restaurant(restaurant_id, data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{restaurant_id}")
def deactivate(restaurant_id: str, current_user=Depends(get_current_user)):
    try:
        return deactivate_restaurant(restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))