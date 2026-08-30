from sqlalchemy.orm import Session

from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from schemas.product import ProductCreate, ProductUpdate, ProductStockUpdate
from utils.exceptions import ConflictError, NotFoundError, ValidationError


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)

    def _ensure_category_exists(self, category_id: int) -> None:
        if self.category_repo.get_by_id(category_id) is None:
            raise ValidationError(f"Category with id {category_id} does not exist.")

    def create_product(self, data: ProductCreate) -> Product:
        self._ensure_category_exists(data.category_id)
        if self.repo.get_by_sku(data.sku) is not None:
            raise ConflictError(f"Product with SKU '{data.sku}' already exists.")
        return self.repo.create(data)

    def get_product(self, product_id: int) -> Product:
        product = self.repo.get_by_id(product_id)
        if product is None:
            raise NotFoundError(f"Product with id {product_id} not found.")
        return product

    def list_products(self) -> list[Product]:
        return self.repo.list_all()

    def list_low_stock(self, threshold: int) -> list[Product]:
        if threshold < 0:
            raise ValidationError("threshold must be a non-negative integer.")
        return self.repo.list_low_stock(threshold)

    def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        self._ensure_category_exists(data.category_id)

        sku_owner = self.repo.get_by_sku(data.sku)
        if sku_owner is not None and sku_owner.id != product_id:
            raise ConflictError(f"Product with SKU '{data.sku}' already exists.")

        return self.repo.update_full(product, data)

    def update_stock(self, product_id: int, data: ProductStockUpdate) -> Product:
        product = self.get_product(product_id)
        new_quantity = product.quantity + data.change
        if new_quantity < 0:
            raise ValidationError(
                f"Cannot apply change {data.change}: resulting quantity "
                f"({new_quantity}) would be negative. Current stock is {product.quantity}."
            )
        return self.repo.update_quantity(product, new_quantity)

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repo.delete(product)
