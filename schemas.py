"""
Database Schemas for O'Plaisir

Each Pydantic model represents a collection in MongoDB (collection name = lowercase class name).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in EUR")
    category: str = Field(..., description="Product category")
    tag: Optional[str] = Field(None, description="Product tag such as bestseller/new")
    image: Optional[str] = Field(None, description="Primary image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")

class Testimonial(BaseModel):
    name: str = Field(..., description="Customer name")
    message: str = Field(..., description="Customer feedback message")
    rating: int = Field(5, ge=1, le=5, description="Star rating 1-5")
    avatar: Optional[str] = Field(None, description="Avatar image URL")

class NewsletterSubscriber(BaseModel):
    email: EmailStr = Field(..., description="Subscriber email")

# You can add more collections as you expand the project:
# - Category, Collection, Order, Wishlist, etc.
