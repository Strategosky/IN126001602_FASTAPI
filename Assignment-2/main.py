from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# --- DATABASE ---
products_db = [
    {"id": 1, "name": "Laptop", "price": 55000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 1500, "category": "Accessories", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 12000, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Keyboard", "price": 2500, "category": "Accessories", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 6500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 3500, "category": "Electronics", "in_stock": False}
]

feedback_db = []
orders_db = []
order_id_counter = 1

# --- TASK 1: FILTER PRODUCTS BY MINIMUM PRICE ---
@app.get("/products/filter")
def filter_products(min_price: Optional[int] = None, max_price: Optional[int] = None, category: Optional[str] = None):
    filtered = products_db
    
    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]
    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]
    if category is not None:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]
        
    return filtered

# --- TASK 2: GET ONLY PRICE OF A PRODUCT ---
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for p in products_db:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    return {"error": "Product not found"}

# --- TASK 3: ACCEPT CUSTOMER FEEDBACK (Pydantic Validation) ---
class CustomerFeedback(BaseModel):
    customer_name: str = Field(min_length=2)
    product_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=300)

@app.post("/feedback")
def submit_feedback(feedback: CustomerFeedback):
    feedback_db.append(feedback.model_dump())
    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback.model_dump(),
        "total_feedback": len(feedback_db)
    }

# --- TASK 4: PRODUCT SUMMARY DASHBOARD ---
@app.get("/products/summary")
def get_product_summary():
    total = len(products_db)
    in_stock_count = len([p for p in products_db if p["in_stock"]])
    out_of_stock_count = len([p for p in products_db if not p["in_stock"]])
    
    best_deal = min(products_db, key=lambda x: x["price"])
    premium_pick = max(products_db, key=lambda x: x["price"])
    
    unique_categories = list({p["category"] for p in products_db})
    
    return {
        "total_products": total,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {"name": premium_pick["name"], "price": premium_pick["price"]},
        "cheapest": {"name": best_deal["name"], "price": best_deal["price"]},
        "categories": unique_categories
    }

# --- TASK 5: VALIDATE & PLACE BULK ORDER ---
class OrderItem(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(min_length=2)
    contact_email: str = Field(min_length=5)
    items: List[OrderItem] = Field(min_length=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0
    
    for item in order.items:
        # Find product in the database
        product = next((p for p in products_db if p["id"] == item.product_id), None)
        
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({
                "product": product["name"],
                "qty": item.quantity,
                "subtotal": subtotal
            })
            
    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# --- BONUS: ORDER STATUS TRACKER ---
class SimpleOrder(BaseModel):
    item_name: str
    quantity: int

@app.post("/orders")
def create_order(order: SimpleOrder):
    global order_id_counter
    new_order = {
        "id": order_id_counter,
        "item_name": order.item_name,
        "quantity": order.quantity,
        "status": "pending"  # Starts as pending per instructions
    }
    orders_db.append(new_order)
    order_id_counter += 1
    return new_order

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for o in orders_db:
        if o["id"] == order_id:
            return o
    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for o in orders_db:
        if o["id"] == order_id:
            o["status"] = "confirmed"  # Changes status to confirmed
            return {"message": "Order confirmed", "order": o}
    return {"error": "Order not found"}
