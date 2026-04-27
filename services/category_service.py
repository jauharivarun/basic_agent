from datetime import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db_models import Category
from exceptions import conflict, not_found
from models import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    """Persistence for categories using SQLite via SQLAlchemy."""

    @staticmethod
    def create_category(db: Session, category: CategoryCreate) -> CategoryResponse:
        existing = db.scalar(select(Category).where(func.lower(Category.name) == category.name.lower()))
        if existing:
            raise conflict(f"Category with name '{category.name}' already exists")
        row = Category(
            name=category.name,
            description=category.description,
            created_at=datetime.now(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return CategoryResponse.model_validate(row)

    @staticmethod
    def list_categories(db: Session) -> List[CategoryResponse]:
        rows = db.scalars(select(Category).order_by(Category.name)).all()
        return [CategoryResponse.model_validate(r) for r in rows]

    @staticmethod
    def get_category(db: Session, category_id: int) -> CategoryResponse:
        row = db.get(Category, category_id)
        if not row:
            raise not_found("Category", category_id)
        return CategoryResponse.model_validate(row)

    @staticmethod
    def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> CategoryResponse:
        row = db.get(Category, category_id)
        if not row:
            raise not_found("Category", category_id)
        updates = category_update.model_dump(exclude_unset=True)
        if "name" in updates:
            existing = db.scalar(
                select(Category).where(
                    func.lower(Category.name) == updates["name"].lower(),
                    Category.id != category_id,
                )
            )
            if existing:
                raise conflict(f"Category with name '{updates['name']}' already exists")
        for key, value in updates.items():
            setattr(row, key, value)
        db.commit()
        db.refresh(row)
        return CategoryResponse.model_validate(row)

    @staticmethod
    def delete_category(db: Session, category_id: int) -> None:
        row = db.get(Category, category_id)
        if not row:
            raise not_found("Category", category_id)
        db.delete(row)
        db.commit()
