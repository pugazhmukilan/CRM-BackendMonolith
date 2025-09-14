from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional,Literal
from datetime import datetime
import re

class Customer(BaseModel):
    customer_id: str = Field(..., min_length=1, description="Unique customer identifier")
    name: str = Field(..., min_length=1, description="Customer's full name")
    email: EmailStr = Field(..., description="Customer's email address")
    totalpurchase: int = Field(..., ge=0, description="Total number of purchases")
    lastactive: int = Field(..., ge=0, description="Last active timestamp (Unix epoch seconds)")
    favitem: str = Field(..., min_length=1, description="Customer's favorite product or item")
   
    purchase_history: List[Dict] = Field(default=[], description="List of purchases with product details")
    preferred_categories: List[str] = Field(default=[], description="Preferred product categories")
    total_spent: float = Field(default=0.0, ge=0, description="Total amount spent on purchases")
    loyalty_status: str = Field(default="Bronze", description="Loyalty tier (Bronze, Silver, Gold)")
    last_purchase_date: Optional[datetime] = Field(None, description="Date of most recent purchase")

    # @field_validator("email")
    # def validate_email(cls, value):
    #     email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    #     if not re.match(email_pattern, value):
    #         raise ValueError("Invalid email format")
    #     return value

    # @field_validator("preferred_categories")
    # def validate_categories(cls, value):
    #     valid_categories = ["Electronics", "Clothing", "Books", "Home", "Toys", "Food", "Other"]
    #     for category in value:
    #         if category not in valid_categories:
    #             raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")
    #     return value

    # @field_validator("loyalty_status")
    # def validate_loyalty_status(cls, value):
    #     valid_statuses = ["Bronze", "Silver", "Gold"]
    #     if value not in valid_statuses:
    #         raise ValueError(f"Invalid loyalty status: {value}. Must be one of {valid_statuses}")
    #     return value

    # @field_validator("purchase_history")
    # def validate_purchase_history(cls, value):
    #     required_keys = {"product_id", "product_name", "category", "price", "purchase_date"}
    #     for purchase in value:
    #         if not all(key in purchase for key in required_keys):
    #             raise ValueError(f"Purchase missing required fields: {required_keys}")
    #         if not isinstance(purchase["price"], (int, float)) or purchase["price"] < 0:
    #             raise ValueError("Purchase price must be a non-negative number")
    #     return value
    




class CustomerIngestionResponse(BaseModel):
    status: Literal["success", "error"]
    message: str
    customer_id: str | None = None # Use the ID created by MongoDB