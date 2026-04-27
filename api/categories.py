from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import CategoryCreate, CategoryResponse, CategoryUpdate, ItemResponse
from services.category_service import CategoryService
from services.item_service import ItemService

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    return CategoryService.create_category(db, category)


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    return CategoryService.list_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    return CategoryService.get_category(db, category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Update a category."""
    return CategoryService.update_category(db, category_id, category_update)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    CategoryService.delete_category(db, category_id)


@router.get("/{category_id}/items", response_model=List[ItemResponse])
async def list_items_in_category(
    category_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
):
    """List all items that belong to a category."""
    return ItemService.list_items_by_category(db, category_id, skip=skip, limit=limit)
