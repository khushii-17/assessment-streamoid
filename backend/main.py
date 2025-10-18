from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up and connecting to database...")
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(title="Product Catalog Backend Project", lifespan=lifespan)

from backend.routes import products
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Product Catalog Backend Project!"}
