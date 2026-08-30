"""
Data-access layer for Product.

Contains no business rules -- only queries and persistence calls.
The raw, hand-written SQL for the "Database Task" (category rollup
report) lives here as `get_category_summary`.
"""
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProductCreate) -> Product:
        product = Product(
            name=data.name,
            sku=data.sku,
            category_id=data.category_id,
            price=data.price,
            quantity=data.quantity,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        stmt = select(Product).where(Product.sku == sku)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Product]:
        stmt = select(Product)
        return list(self.db.execute(stmt).scalars().all())

    def list_low_stock(self, threshold: int) -> list[Product]:
        stmt = select(Product).where(Product.quantity < threshold)
        return list(self.db.execute(stmt).scalars().all())

    def update_full(self, product: Product, data: ProductUpdate) -> Product:
        product.name = data.name
        product.sku = data.sku
        product.category_id = data.category_id
        product.price = data.price
        product.quantity = data.quantity
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_quantity(self, product: Product, new_quantity: int) -> Product:
        product.quantity = new_quantity
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

    def get_category_summary(self) -> list[dict]:
        """
        Hand-written SQL (not the ORM query builder) for:
        category, product_count, total_stock, inventory_value.

        Uses a LEFT JOIN so categories with zero products still show up
        with product_count=0 / total_stock=0 / inventory_value=0.
        """
        sql = text(
            """
            SELECT
                c.id                                       AS category_id,
                c.name                                      AS category_name,
                COUNT(p.id)                                  AS product_count,
                COALESCE(SUM(p.quantity), 0)                 AS total_stock,
                COALESCE(SUM(p.price * p.quantity), 0)       AS inventory_value
            FROM categories c
            LEFT JOIN products p ON p.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name;
            """
        )
        result = self.db.execute(sql)
        return [dict(row._mapping) for row in result]
