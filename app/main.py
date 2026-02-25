from fastapi import FastAPI
from api.products import router as product_router

app = FastAPI(
    title="FastAPI Learning Project",
    description="Learning FastAPI Concepts",
    version="1.0"
)

app.include_router(product_router)