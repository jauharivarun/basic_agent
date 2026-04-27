from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models import ItemCreate, ItemUpdate, ItemResponse
from services.item_service import ItemService

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item.

    - **name**: Item name (required, 1-100 characters)
    - **description**: Item description (optional, max 500 characters)
    - **price**: Item price (required, must be positive)
    - **category_id**: Optional category to link this item to
    """
    return ItemService.create_item(db, item)


@router.get("/", response_model=List[ItemResponse])
async def list_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, min_length=1, description="Search in name/description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    sort_by: Literal["id", "name", "price", "created_at"] = Query(
        "id",
        description="Field used for sorting",
    ),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
    db: Session = Depends(get_db),
):
    """
    List all items with optional filtering and pagination.

    - **skip**: Number of items to skip (for pagination)
    - **limit**: Maximum number of items to return (1-100)
    - **search**: Optional text search in item name/description
    - **min_price**: Optional minimum price filter
    - **max_price**: Optional maximum price filter
    - **sort_by**: Sort field (`id`, `name`, `price`, `created_at`)
    - **order**: Sort order (`asc` or `desc`)
    """
    return ItemService.list_items(
        db,
        skip=skip,
        limit=limit,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
    )


@router.get("/stats/count", response_model=dict)
async def get_item_count(db: Session = Depends(get_db)):
    """Get total number of items"""
    return {"total_items": ItemService.get_total_count(db)}


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Get a specific item by ID.

    - **item_id**: The ID of the item to retrieve
    """
    return ItemService.get_item(db, item_id)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)
):
    """
    Update an item. Only provided fields will be updated.

    - **item_id**: The ID of the item to update
    - **item_update**: Fields to update (all optional)
    - **category_id**: Optional category ID to move item into
    """
    return ItemService.update_item(db, item_id, item_update)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete an item.

    - **item_id**: The ID of the item to delete
    """
    ItemService.delete_item(db, item_id)
