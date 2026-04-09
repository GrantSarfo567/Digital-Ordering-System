from fastapi import FastAPI
from app.routers import auth, orders, menu, restaurants

app = FastAPI(
    title="Digital Ordering System API",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])

@app.get("/")
def root():
    return {"message": "Our Digital Ordering System API is running"}