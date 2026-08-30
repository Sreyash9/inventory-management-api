from sqlalchemy.orm import Session

from models.category import Category
from repositories.category_repository import CategoryRepository
from schemas.category import CategoryCreate
from utils.exceptions import ConflictError


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def create_category(self, data: CategoryCreate) -> Category:
        existing = self.repo.get_by_name(data.name)
        if existing is not None:
            raise ConflictError(f"Category with name '{data.name}' already exists.")
        return self.repo.create(data)

    def list_categories(self) -> list[Category]:
        return self.repo.list_all()
