from fastapi import APIRouter
from .paystack_webhook import router as paystack_router

router = APIRouter()

router.include_router(paystack_router, prefix="/paystack")