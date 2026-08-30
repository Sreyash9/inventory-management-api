"""
Data-access layer for Category.

Contains no business rules -- only queries and persistence calls.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.category import Category
from schemas.category import CategoryCreate


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: CategoryCreate) -> Category:
        category = Category(name=data.name)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Category]:
        stmt = select(Category)
        return list(self.db.execute(stmt).scalars().all())
