from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

# --- DATABASES ---
products_db = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

cart = []
orders_db = []
order_id_counter = 1

# --- MODELS ---
class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    delivery_address: str = Field(min_length=10)

# --- ENDPOINTS ---

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    # 1. Find the product
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    # 2. Validation
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")
        
    # 3. Check if already in cart (Update quantity if it is)
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}
            
    # 4. If new to cart, add it
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}
        
    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for i, item in enumerate(cart):
        if item["product_id"] == product_id:
            removed_name = item["product_name"]
            cart.pop(i)
            return {"message": f"{removed_name} removed from cart"}
            
    raise HTTPException(status_code=404, detail="Item not in cart")


@app.post("/cart/checkout")
def checkout(details: CheckoutRequest):
    global order_id_counter
    
    # Bonus Task Logic: Prevent checkout on empty cart
    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY: Cannot checkout with an empty cart")
        
    placed_orders = 0
    grand_total = sum(item["subtotal"] for item in cart)
    
    # Create an order for each item in the cart
    for item in cart:
        new_order = {
            "order_id": order_id_counter,
            "customer_name": details.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"]
        }
        orders_db.append(new_order)
        order_id_counter += 1
        placed_orders += 1
        
    # Clear the cart after successful checkout
    cart.clear()
    
    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders_db,
        "total_orders": len(orders_db)
    }
