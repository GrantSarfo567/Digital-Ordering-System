from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def menu_root():
    return {"message": "Menu router working"}