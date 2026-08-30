"""
Analytics service.

Deliberately computes the "Python Task" figures (totals, most expensive
product, lowest stock product) in plain Python using loops/comprehensions
over ORM objects already fetched from the DB, rather than delegating the
math to SQL aggregate functions -- this is what the exercise is testing.

The "Database Task" (category, product_count, total_stock, inventory_value)
is delegated to ProductRepository.get_category_summary(), which is answered
with hand-written SQL (JOIN + GROUP BY) instead of Python.
"""
from sqlalchemy.orm import Session

from models.product import Product
from repositories.product_repository import ProductRepository
from schemas.analytics import CategorySummaryRow, InventorySummary, ProductBrief


def _to_brief(product: Product) -> ProductBrief:
    return ProductBrief(
        id=product.id,
        name=product.name,
        sku=product.sku,
        price=float(product.price),
        quantity=product.quantity,
    )


class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_inventory_summary(self) -> InventorySummary:
        products = self.repo.list_all()

        if not products:
            return InventorySummary(
                total_products=0,
                total_quantity=0,
                total_inventory_value=0.0,
                most_expensive_product=None,
                lowest_stock_product=None,
            )

        # --- Loops / comprehensions doing the actual work ---

        total_products = len(products)

        total_quantity = sum(p.quantity for p in products)

        # price * quantity per product, summed via comprehension
        total_inventory_value = sum(float(p.price) * p.quantity for p in products)

        most_expensive = products[0]
        for p in products:
            if float(p.price) > float(most_expensive.price):
                most_expensive = p

        lowest_stock = products[0]
        for p in products:
            if p.quantity < lowest_stock.quantity:
                lowest_stock = p

        return InventorySummary(
            total_products=total_products,
            total_quantity=total_quantity,
            total_inventory_value=round(total_inventory_value, 2),
            most_expensive_product=_to_brief(most_expensive),
            lowest_stock_product=_to_brief(lowest_stock),
        )

    def get_category_summary(self) -> list[CategorySummaryRow]:
        rows = self.repo.get_category_summary()
        return [
            CategorySummaryRow(
                category_id=row["category_id"],
                category_name=row["category_name"],
                product_count=row["product_count"],
                total_stock=int(row["total_stock"]),
                inventory_value=float(row["inventory_value"]),
            )
            for row in rows
        ]
