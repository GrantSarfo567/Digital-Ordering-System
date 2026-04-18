from fastapi import APIRouter
from .paystack_webhook import router as paystack_router

router = APIRouter(prefix="/webhooks")

router.include_router(paystack_router)