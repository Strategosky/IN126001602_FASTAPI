from fastapi import FastAPI

app = FastAPI()

# Database with 7 products
products_db = [
    {"id": 1, "name": "Laptop", "price": 55000, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 1500, "category": "Accessories", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 12000, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Keyboard", "price": 2500, "category": "Accessories", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 6500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 3500, "category": "Electronics", "in_stock": False}
]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Store API. Visit /docs to see the Swagger UI."}

# --- TASK 1: GET ALL PRODUCTS ---
@app.get("/products")
def get_products():
    return {
        "products": products_db,
        "total": len(products_db)
    }

# --- TASK 2: CATEGORY FILTER ENDPOINT ---
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products_db if p["category"].lower() == category_name.lower()]
    
    if not result:
        return {"error": "No products found in this category"}
    
    return {
        "category": category_name.capitalize(),
        "total": len(result),
        "products": result
    }

# --- TASK 3: IN-STOCK PRODUCTS ENDPOINT ---
@app.get("/products/instock")
def get_in_stock_products():
    available_products = [p for p in products_db if p["in_stock"]]
    return {
        "in_stock_products": available_products,
        "count": len(available_products)
    }

# --- TASK 4: STORE SUMMARY ENDPOINT ---
@app.get("/store/summary")
def get_store_summary():
    total = len(products_db)
    in_stock_count = len([p for p in products_db if p["in_stock"]])
    out_of_stock_count = len([p for p in products_db if not p["in_stock"]])
    
    # Use a set comprehension to get unique categories, then convert back to a list
    unique_categories = list({p["category"] for p in products_db})
    
    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": in_stock_count,
        "out_of_stock": out_of_stock_count,
        "categories": unique_categories
    }

# --- TASK 5: SEARCH PRODUCTS BY NAME ---
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    # Convert keyword to lowercase for case-insensitive comparison
    keyword_lower = keyword.lower()
    
    # Filter products where the keyword exists in the product name
    matched_products = [
        p for p in products_db 
        if keyword_lower in p["name"].lower()
    ]
    
    # If no products match, return the specified message
    if not matched_products:
        return {"message": "No products matched your search"}
    
    # Return the matched products and the count
    return {
        "count": len(matched_products),
        "results": matched_products
    }

# --- BONUS TASK: CHEAPEST & MOST EXPENSIVE PRODUCT ---
@app.get("/products/deals")
def get_deals():
    # Use min() and max() with a lambda function to compare based on the "price" key
    best_deal = min(products_db, key=lambda x: x["price"])
    premium_pick = max(products_db, key=lambda x: x["price"])
    
    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }
