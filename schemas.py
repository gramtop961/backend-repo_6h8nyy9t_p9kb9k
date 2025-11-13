"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Food delivery app schemas

class Restaurant(BaseModel):
    name: str = Field(..., description="Restaurant name")
    description: Optional[str] = Field(None, description="Short blurb")
    image: Optional[str] = Field(None, description="Cover image URL")
    cuisine: str = Field(..., description="Cuisine type, e.g. Italian")
    rating: float = Field(4.5, ge=0, le=5)
    delivery_time_min: int = Field(25, ge=5, le=120, description="Estimated delivery time in minutes")

class MenuItem(BaseModel):
    restaurant_id: str = Field(..., description="Restaurant ObjectId as string")
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    image: Optional[str] = None
    category: Optional[str] = Field(None, description="e.g., Mains, Sides, Drinks")

class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    quantity: int = Field(1, ge=1)
    price: float

class Order(BaseModel):
    restaurant_id: str
    customer_name: str
    address: str
    phone: str
    items: List[OrderItem]
    total: float
    status: str = Field("pending", description="pending|confirmed|delivered|canceled")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
