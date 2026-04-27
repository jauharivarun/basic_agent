from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime

class ItemBase(BaseModel):
    """Base model for Item"""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Item price (must be positive)")

class ItemCreate(ItemBase):
    """Model for creating an item"""
    category_id: Optional[int] = Field(
        None,
        ge=1,
        description="Optional category ID this item belongs to",
    )

class ItemUpdate(BaseModel):
    """Model for updating an item (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, ge=1)

class ItemResponse(ItemBase):
    """Model for item response"""
    id: int
    created_at: datetime
    category_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base model for Category."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")


class CategoryCreate(CategoryBase):
    """Model for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Model for updating a category (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryResponse(CategoryBase):
    """Model for category response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Standard error response — every error in the API returns this shape
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope returned for all error responses."""
    status_code: int = Field(..., description="HTTP status code")
    error: str = Field(..., description="Short error type, e.g. 'Not Found'")
    detail: Any = Field(..., description="Human-readable explanation or validation details")