from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def orders_root():
    return {"message": "Orders router working"}