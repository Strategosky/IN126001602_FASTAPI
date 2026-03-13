from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

products_db = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Pydantic model for POSTing new products
class ProductCreate(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool

# --- HELPER: GET ALL PRODUCTS ---
@app.get("/products")
def get_products():
    return {"products": products_db, "total": len(products_db)}


# --- TASK 1: ADD NEW PRODUCTS (POST) ---
@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(product: ProductCreate):
    # Check for duplicate name
    for p in products_db:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    # Auto-generate ID
    new_id = max([p["id"] for p in products_db]) + 1 if products_db else 1
    
    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }
    products_db.append(new_product)
    
    return {"message": "Product added", "product": new_product}


# --- TASK 2: RESTOCK THE USB HUB (PUT) ---
# Note: Using {product_id:int} ensures this route doesn't block /audit or /discount later!
@app.put("/products/{product_id:int}")
def update_product(product_id: int, in_stock: Optional[bool] = None, price: Optional[int] = None):
    for p in products_db:
        if p["id"] == product_id:
            if in_stock is not None:
                p["in_stock"] = in_stock
            if price is not None:
                p["price"] = price
            return p
            
    raise HTTPException(status_code=404, detail="Product not found")


# --- TASK 3: DELETE A PRODUCT ---
@app.delete("/products/{product_id:int}")
def delete_product(product_id: int):
    for i, p in enumerate(products_db):
        if p["id"] == product_id:
            deleted_name = p["name"]
            products_db.pop(i)
            return {"message": f"Product '{deleted_name}' deleted"}
            
    raise HTTPException(status_code=404, detail="Product not found")


# --- TASK 4: FULL CRUD SEQUENCE ---
# Task 4 is a workflow testing the endpoints above. To complete the sequence 
# in Swagger (POST -> GET -> PUT -> GET -> DELETE), we just need a GET single product endpoint:
@app.get("/products/{product_id:int}")
def get_single_product(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


# --- TASK 5: INVENTORY SUMMARY AUDIT ---
@app.get("/products/audit")
def get_inventory_audit():
    total_products = len(products_db)
    
    in_stock_items = [p for p in products_db if p["in_stock"]]
    in_stock_count = len(in_stock_items)
    
    out_of_stock_names = [p["name"] for p in products_db if not p["in_stock"]]
    
    # Value of in-stock items (price * 10 units each)
    total_stock_value = sum(p["price"] * 10 for p in in_stock_items)
    
    most_expensive_product = max(products_db, key=lambda x: x["price"])
    
    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive_product["name"],
            "price": most_expensive_product["price"]
        }
    }


# --- BONUS: CATEGORY-WIDE DISCOUNT ---
@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):
    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="Discount must be between 1 and 99")
        
    updated_count = 0
    for p in products_db:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated_count += 1
            
    if updated_count == 0:
        return {"message": f"No products found in category '{category}'"}
        
    return {"message": f"Successfully updated {updated_count} products in {category}"}
