import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Restaurant, MenuItem, Order, OrderItem, User, Product

app = FastAPI(title="Food Delivery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Food Delivery API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Utility to convert ObjectId to string in results

def _stringify_id(doc):
    if isinstance(doc, dict) and doc.get("_id") is not None:
        doc["_id"] = str(doc["_id"])
    return doc

# Seed sample data if collections are empty
@app.post("/seed")
def seed_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    collections = db.list_collection_names()
    created = {"restaurants": 0, "menuitem": 0}

    if "restaurant" not in collections or db["restaurant"].count_documents({}) == 0:
        sample_restaurants = [
            Restaurant(name="Pasta Palace", cuisine="Italian", description="Homemade pasta and sauces", image="https://images.unsplash.com/photo-1521389508051-d7ffb5dc8bbf", rating=4.6, delivery_time_min=30),
            Restaurant(name="Sushi Express", cuisine="Japanese", description="Fresh nigiri and rolls", image="https://images.unsplash.com/photo-1544025162-d76694265947", rating=4.8, delivery_time_min=25),
            Restaurant(name="Spice Route", cuisine="Indian", description="Curries, biryani and more", image="https://images.unsplash.com/photo-1604908554027-0f2f74a9cfc7", rating=4.5, delivery_time_min=35),
        ]
        for r in sample_restaurants:
            create_document("restaurant", r)
            created["restaurants"] += 1

    if "menuitem" not in collections or db["menuitem"].count_documents({}) == 0:
        # Fetch restaurants to link menu items
        restaurants = list(db["restaurant"].find())
        if restaurants:
            first = restaurants[0]["_id"]
            second = restaurants[1]["_id"] if len(restaurants) > 1 else first
            third = restaurants[2]["_id"] if len(restaurants) > 2 else first
            items = [
                MenuItem(restaurant_id=str(first), name="Spaghetti Carbonara", description="Creamy sauce with pancetta", price=14.99, image="https://images.unsplash.com/photo-1603133872878-684f208fb86a", category="Mains"),
                MenuItem(restaurant_id=str(first), name="Margherita Pizza", description="Classic tomatoes and mozzarella", price=12.5, image="https://images.unsplash.com/photo-1548365328-9f547fb09530", category="Mains"),
                MenuItem(restaurant_id=str(second), name="Salmon Nigiri (6)", description="Fresh cut salmon over rice", price=11.99, image="https://images.unsplash.com/photo-1562158070-1a4f3f8f7c21", category="Sushi"),
                MenuItem(restaurant_id=str(third), name="Chicken Tikka Masala", description="Charred chicken in spicy sauce", price=13.75, image="https://images.unsplash.com/photo-1604908177031-842fa9a316d2", category="Mains"),
            ]
            for i in items:
                create_document("menuitem", i)
                created["menuitem"] += 1

    return {"seeded": created}

# Public endpoints

@app.get("/restaurants")
def list_restaurants():
    docs = get_documents("restaurant")
    return [_stringify_id(d) for d in docs]

@app.get("/restaurants/{restaurant_id}/menu")
def list_menu(restaurant_id: str):
    try:
        # Ensure valid ObjectId string when filtering menu item references
        _ = ObjectId(restaurant_id)
    except Exception:
        pass
    docs = get_documents("menuitem", {"restaurant_id": restaurant_id})
    return [_stringify_id(d) for d in docs]

class CreateOrder(BaseModel):
    restaurant_id: str
    customer_name: str
    address: str
    phone: str
    items: List[OrderItem]

@app.post("/orders")
def create_order(payload: CreateOrder):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Compute total server-side for trustworthiness
    total = sum(item.price * item.quantity for item in payload.items)
    order = Order(
        restaurant_id=payload.restaurant_id,
        customer_name=payload.customer_name,
        address=payload.address,
        phone=payload.phone,
        items=payload.items,
        total=round(total, 2),
        status="pending",
    )
    oid = create_document("order", order)
    return {"order_id": oid, "status": "pending", "total": order.total}

# Schema endpoint for database viewer
@app.get("/schema")
def get_schema():
    from schemas import User, Product, Restaurant, MenuItem, Order, OrderItem
    # Return class names so the viewer can introspect installed schemas
    return {
        "collections": [
            "user",
            "product",
            "restaurant",
            "menuitem",
            "order",
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
