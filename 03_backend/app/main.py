from fastapi import FastAPI
from app.routers import auth, orders, menu, restaurants
from app.services.payments.payment_router import router as payment_router
from app.services.payments.webhooks.mtn_webhook import router as mtn_webhook_router
from app.services.payments.webhooks.webhook_router import router as webhooks_router

app = FastAPI(
    title="Digital Ordering System Backend",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])

# MTN webhook (prefixed here)
app.include_router(mtn_webhook_router, prefix="/webhooks", tags=["Webhooks"])

# Payments
app.include_router(payment_router, prefix="/payments", tags=["Payments"])

# 🔥 FIX: DO NOT add prefix here (it’s already inside webhook_router)
app.include_router(webhooks_router, tags=["Webhooks"])


@app.get("/")
def root():
    return {"message": "Our Digital Ordering System backend is up and running"}