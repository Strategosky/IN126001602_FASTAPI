from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import math

app = FastAPI()

# --- DATABASES ---
products_db = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

orders_db = []

# --- HELPER ROUTE TO CREATE FAKE ORDERS FOR TESTING ---
class OrderCreate(BaseModel):
    customer_name: str
    product_name: str

@app.post("/orders")
def create_order(order: OrderCreate):
    new_order = {
        "order_id": len(orders_db) + 1,
        "customer_name": order.customer_name,
        "product_name": order.product_name
    }
    orders_db.append(new_order)
    return new_order



@app.get("/products/search")
def search_products(keyword: str):
    results = [p for p in products_db if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}
    
    is_descending = True if order.lower() == "desc" else False
    sorted_items = sorted(products_db, key=lambda x: x[sort_by], reverse=is_descending)
    return sorted_items

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):
    total = len(products_db)
    total_pages = math.ceil(total / limit) if total > 0 else 0
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_products": total,
        "products": products_db[start:end]
    }



# --- TASK 4: SEARCH THE ORDERS LIST ---
@app.get("/orders/search")
def search_orders(customer_name: str):
    results = [o for o in orders_db if customer_name.lower() in o["customer_name"].lower()]
    
    if not results:
        return {"message": f"No orders found for customer: {customer_name}"}
        
    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }

# --- TASK 5: SORT PRODUCTS BY CATEGORY THEN PRICE ---
@app.get("/products/sort-by-category")
def sort_products_by_category():
    # Tuples allow sorting by primary key (category), then secondary key (price)
    sorted_items = sorted(products_db, key=lambda x: (x["category"], x["price"]))
    return sorted_items

# --- SEARCH + SORT + PAGINATE IN ONE ---
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None, 
    sort_by: str = "price", 
    order: str = "asc", 
    page: int = 1, 
    limit: int = 4
):
    # 1. Filter
    filtered = products_db
    if keyword:
        filtered = [p for p in filtered if keyword.lower() in p["name"].lower()]
        
    # 2. Sort
    if sort_by in ["price", "name"]:
        is_descending = True if order.lower() == "desc" else False
        filtered = sorted(filtered, key=lambda x: x[sort_by], reverse=is_descending)
        
    # 3. Paginate
    total_found = len(filtered)
    total_pages = math.ceil(total_found / limit) if total_found > 0 else 0
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_found": total_found,
        "products": filtered[start:end]
    }

# --- BONUS: PAGINATE THE ORDERS LIST ---
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    total = len(orders_db)
    total_pages = math.ceil(total / limit) if total > 0 else 0
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_orders": total,
        "orders": orders_db[start:end]
    }
