from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def restaurants_root():
    return {"message": "Restaurants router working"}