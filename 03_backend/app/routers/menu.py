from fastapi import APIRouter, Depends, HTTPException
from app.models.menu import MenuItemCreate, MenuItemResponse
from app.services.menu_service import (
    create_menu_item,
    get_menu_items,
    get_menu_item,
    update_menu_item,
    delete_menu_item
)
from app.middleware.auth import get_current_user
from typing import List

router = APIRouter()

@router.post("/{restaurant_id}", response_model=MenuItemResponse)
def create(restaurant_id: str, data: MenuItemCreate, current_user=Depends(get_current_user)):
    try:
        return create_menu_item(restaurant_id, data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{restaurant_id}", response_model=List[MenuItemResponse])
def get_all(restaurant_id: str):
    try:
        return get_menu_items(restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/item/{menu_item_id}", response_model=MenuItemResponse)
def get_one(menu_item_id: str):
    try:
        item = get_menu_item(menu_item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")
        return item
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/item/{menu_item_id}", response_model=MenuItemResponse)
def update(menu_item_id: str, data: MenuItemCreate, current_user=Depends(get_current_user)):
    try:
        return update_menu_item(menu_item_id, data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/item/{menu_item_id}")
def delete(menu_item_id: str, current_user=Depends(get_current_user)):
    try:
        return delete_menu_item(menu_item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))