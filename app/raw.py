# /app/main.py
# ==============================
# FASTAPI LEARNING FILE
# Covers:
# - Basic Routes
# - Path Parameters
# - Query Parameters
# - Pagination
# - Sorting
# - HTTPException
# - Request Body
# ==============================

from fastapi import FastAPI, HTTPException, Path, Query, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, Optional, List
from service.products import get_all_products, add_product, remove_product, update_content, load_products
from schema.product import Product
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI(
    title="FastAPI Learning Project",
    description="Learning FastAPI Concepts",
    version="1.0"
)

# ==============================
# 1 BASIC ROUTE
# ==============================

# @app.middleware("http")
# async def lifecycle(request: Request, call_next):
#     print("Before Request")
#     response = await call_next(request)
#     print("After Request")
#     return response

def common_logic():
    return "Hi There"

@app.get("/", response_model=dict)
def root(dep=Depends(common_logic)):
    URL_PATH = os.getenv("BASE_URL")
    # return {
    #     "message": "Welcome to FastAPI",
    #     "dependency": dep,
    #     "data_path": URL_PATH
    # }
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to FastAPI",
            "dependency": dep,
            "data_path": URL_PATH
        }
    )


# ==============================
# 2 PATH PARAMETERS
# ==============================

@app.get("/products/{product_id}", response_model=Dict)
def get_product_by_id(
        product_id: int = Path(
            ...,
            ge=1,
            le=1000,
            description="Product ID",
            example=10
        )
):

    products = get_all_products()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# ==============================
# 3 QUERY PARAMETERS
# ==============================

@app.get("/products", response_model=Dict)
def list_products(
        dep=Depends(load_products),

        # Search
        name: Optional[str] = Query(
            default=None,
            min_length=1,
            max_length=50,
            description="Search product by name",
            example="Laptop"
        ),

        # Sorting
        sort_by_price: bool = Query(
            default=False,
            description="Sort by price"
        ),

        order: str = Query(
            default="asc",
            description="asc or desc"
        ),

        # Pagination
        limit: int = Query(
            default=5,
            ge=1,
            le=50,
            description="Number of products"
        ),

        offset: int = Query(
            default=0,
            ge=0,
            description="Pagination offset"
        )
):

    products = dep

    # SEARCH
    if name:
        needle = name.strip().lower()

        products = [
            p for p in products
            if needle in p.get("name", "").lower()
        ]

    if not products:
        raise HTTPException(
            status_code=404,
            detail="No products found"
        )

    # SORT
    if sort_by_price:
        reverse = order == "desc"

        products = sorted(
            products,
            key=lambda p: p.get("price", 0),
            reverse=reverse
        )

    # PAGINATION
    total = len(products)

    products = products[offset:offset+limit]

    return {
        "total": total,
        "items": products
    }


# ==============================
# 4 REQUEST BODY (POST)
# ==============================

@app.post("/products", status_code=201)
def create_product(product: Product):

    try:
        return add_product(product.model_dump(mode="json"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==============================
# 4 REQUEST BODY (DELETE)
# ==============================

@app.delete("/products/{product_id}")
def delete_product(product_id: int = Path(..., description="Product ID", example="1")):
    
    try:
        return remove_product(product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==============================
# 4 REQUEST BODY (PUT)
# ==============================

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: Product
):
    
    try:
        return update_content(
            product_id,
            product.model_dump(mode="json")
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
# ==============================
# 5 VALIDATION EXAMPLES
# ==============================

@app.get("/test-validation")
def validation_example(

        age: int = Query(ge=18, le=60),

        rating: float = Query(ge=0, le=5),

        username: str = Query(min_length=3)

):

    return {
        "age": age,
        "rating": rating,
        "username": username
    }# /app/service/products.py
# ==============================
# DATA SERVICE
# ==============================

import json
from pathlib import Path
from typing import List, Dict

from fastapi import HTTPException

DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"
# DATA_FILE = Path(__file__).parent.parent / "data" / "dummy.json"


def load_products() -> List[Dict]:

    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_all_products() -> List[Dict]:

    return load_products()

def save_products(products: List[Dict]):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def add_product(product: Dict) -> Dict:

    products = get_all_products()

    # Duplicate name check
    if any(p["name"].lower() == product["name"].lower() for p in products):

        raise HTTPException(
            status_code=400,
            detail="Product already exists"
        )

    products.append(product)

    save_products(products)

    return product


def remove_product(id: int) -> str:
    products = get_all_products()

    for idx, p in enumerate(products):
        if p["id"] == id:
            deleted = products.pop(idx)
            save_products(products)
            return {
                "message": "Product deleted successfully",
                "data": deleted
            }

def update_content(product_id: int, updated_data: Dict):

    products = get_all_products()

    for idx, product in enumerate(products):

        if product["id"] == product_id:

            # Update product fields
            products[idx].update(updated_data)

            # Save updated list
            save_products(products)

            return products[idx]

    raise ValueError("Product not found")# /app/schema/product.py
# ==============================
# PYDANTIC LEARNING FILE
# Covers:
# - BaseModel
# - Field
# - Annotated
# - Validators
# - Computed Fields
# ==============================

from pydantic import BaseModel, Field, AnyUrl, field_validator, computed_field, model_validator
from typing import Annotated, List, Optional


class Product(BaseModel):

    id: Annotated[int, Field(
        ge=1,
        le=1000,
        description="Product ID",
        example=10
    )]

    name: Annotated[str, Field(
        min_length=2,
        max_length=50,
        example="Laptop"
    )]

    category: str

    price: Annotated[float, Field(
        ge=0
    )]

    rating: Annotated[float, Field(
        ge=0,
        le=5
    )]

    stock: int

    brand: str


    # ==========================
    # OPTIONAL FIELDS : Below are example for learning
    # ==========================

    # tags: Optional[List[str]] = Field(
    #     default=None,
    #     description="Product tags",
    #     example=["Electronics", "Tech"]
    # )


    # image_urls: List[AnyUrl] = Field(
    #     default=[],
    #     description="Product Images"
    # )


    # ==========================
    # FIELD VALIDATOR : Validates one field
    # ==========================

    @field_validator("name", mode="after")
    @classmethod
    def name_must_be_clean(cls, value: str):

        if value.strip() == "":
            raise ValueError("Name cannot be empty")

        return value

    # ==========================
    # MODEL VALIDATOR : Validates entire object
    # ==========================

    
    @model_validator(mode="after")
    @classmethod
    def validate_business_rules(cls, model: "Product"):

        if model.rating < 1.0 and model.stock < 100:
            raise ValueError(
                "Product rating is too low and stock is insufficient"
            )

        return model


    # ==========================
    # COMPUTED FIELD
    # ==========================

    @computed_field
    def in_stock(self) -> bool:
        return self.stock > 0

    @computed_field
    def is_popular(self) -> bool:
        return self.rating >= 4.5


    @computed_field
    def price_with_tax(self) -> float:
        return round(self.price * 1.18, 2)