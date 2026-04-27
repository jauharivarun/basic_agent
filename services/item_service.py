from datetime import datetime
from typing import List, Optional

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from db_models import Category, Item
from exceptions import bad_request, not_found
from models import ItemCreate, ItemUpdate, ItemResponse


class ItemService:
    """Persistence for items using SQLite via SQLAlchemy."""

    @staticmethod
    def create_item(db: Session, item: ItemCreate) -> ItemResponse:
        if item.category_id is not None and db.get(Category, item.category_id) is None:
            raise not_found("Category", item.category_id)
        row = Item(
            name=item.name,
            description=item.description,
            price=item.price,
            created_at=datetime.now(),
            category_id=item.category_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return ItemResponse.model_validate(row)

    @staticmethod
    def get_item(db: Session, item_id: int) -> ItemResponse:
        """Raises AppError (404) if the item does not exist."""
        row = db.get(Item, item_id)
        if not row:
            raise not_found("Item", item_id)
        return ItemResponse.model_validate(row)

    @staticmethod
    def list_items(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> List[ItemResponse]:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise bad_request("min_price cannot be greater than max_price")

        stmt = select(Item)

        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Item.name.ilike(term),
                    Item.description.ilike(term),
                )
            )

        if min_price is not None:
            stmt = stmt.where(Item.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Item.price <= max_price)

        sort_column = {
            "id": Item.id,
            "name": Item.name,
            "price": Item.price,
            "created_at": Item.created_at,
        }.get(sort_by, Item.id)
        sort_expression = desc(sort_column) if order == "desc" else asc(sort_column)
        stmt = stmt.order_by(sort_expression)

        stmt = stmt.offset(skip).limit(limit)
        rows = db.scalars(stmt).all()
        return [ItemResponse.model_validate(r) for r in rows]

    @staticmethod
    def update_item(db: Session, item_id: int, item_update: ItemUpdate) -> ItemResponse:
        """Raises AppError (404) if the item does not exist."""
        row = db.get(Item, item_id)
        if not row:
            raise not_found("Item", item_id)
        updates = item_update.model_dump(exclude_unset=True)
        category_id = updates.get("category_id")
        if category_id is not None and db.get(Category, category_id) is None:
            raise not_found("Category", category_id)
        for key, value in updates.items():
            setattr(row, key, value)
        db.commit()
        db.refresh(row)
        return ItemResponse.model_validate(row)

    @staticmethod
    def delete_item(db: Session, item_id: int) -> None:
        """Raises AppError (404) if the item does not exist."""
        row = db.get(Item, item_id)
        if not row:
            raise not_found("Item", item_id)
        db.delete(row)
        db.commit()

    @staticmethod
    def get_total_count(db: Session) -> int:
        return db.scalar(select(func.count()).select_from(Item)) or 0

    @staticmethod
    def list_items_by_category(
        db: Session,
        category_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> List[ItemResponse]:
        if db.get(Category, category_id) is None:
            raise not_found("Category", category_id)
        stmt = (
            select(Item)
            .where(Item.category_id == category_id)
            .order_by(Item.id)
            .offset(skip)
            .limit(limit)
        )
        rows = db.scalars(stmt).all()
        return [ItemResponse.model_validate(r) for r in rows]
