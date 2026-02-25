from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import Optional, Dict
from schema.product import Product
from service.products import (
    get_all_products,
    add_product,
    remove_product,
    update_content,
    load_products
)

router = APIRouter(prefix="/products", tags=["Products"])


# ==============================
# GET PRODUCT BY ID
# ==============================

@router.get("/{product_id}")
def get_product_by_id(
    product_id: int = Path(..., ge=1, le=1000)
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
# LIST PRODUCTS
# ==============================

@router.get("/")
def list_products(

    products=Depends(load_products),

    name: Optional[str] = Query(None),

    sort_by_price: bool = False,

    order: str = "asc",

    limit: int = Query(5, ge=1, le=50),

    offset: int = Query(0, ge=0)

):

    # SEARCH
    if name:

        needle = name.lower().strip()

        products = [
            p for p in products
            if needle in p.get("name", "").lower()
        ]

    # SORT
    if sort_by_price:

        reverse = order == "desc"

        products = sorted(
            products,
            key=lambda p: p.get("price", 0),
            reverse=reverse
        )

    total = len(products)

    products = products[offset:offset+limit]

    return {
        "total": total,
        "items": products
    }


# ==============================
# CREATE PRODUCT
# ==============================

@router.post("/", status_code=201)
def create_product(product: Product):

    try:
        return add_product(product.model_dump(mode="json"))

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==============================
# DELETE PRODUCT
# ==============================

@router.delete("/{product_id}")
def delete_product(product_id: int):

    try:
        return remove_product(product_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ==============================
# UPDATE PRODUCT
# ==============================

@router.put("/{product_id}")
def update_product(product_id: int, product: Product):

    try:

        return update_content(
            product_id,
            product.model_dump(mode="json")
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )