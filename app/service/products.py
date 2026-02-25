import json
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


# ==============================
# LOAD
# ==============================

def load_products() -> List[Dict]:

    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================
# SAVE
# ==============================

def save_products(products: List[Dict]):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)


# ==============================
# GET ALL
# ==============================

def get_all_products():

    return load_products()


# ==============================
# ADD
# ==============================

def add_product(product: Dict):

    products = get_all_products()

    if any(
        p["name"].lower() == product["name"].lower()
        for p in products
    ):
        raise ValueError("Product already exists")

    products.append(product)

    save_products(products)

    return product


# ==============================
# DELETE
# ==============================

def remove_product(product_id: int):

    products = get_all_products()

    for i, p in enumerate(products):

        if p["id"] == product_id:

            deleted = products.pop(i)

            save_products(products)

            return {
                "message": "Deleted successfully",
                "data": deleted
            }

    raise ValueError("Product not found")


# ==============================
# UPDATE
# ==============================

def update_content(product_id: int, updated_data: Dict):

    products = get_all_products()

    for i, p in enumerate(products):

        if p["id"] == product_id:

            products[i].update(updated_data)

            save_products(products)

            return products[i]

    raise ValueError("Product not found")