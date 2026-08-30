from typing import Optional

from pydantic import BaseModel


class ProductBrief(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    quantity: int


class InventorySummary(BaseModel):
    total_products: int
    total_quantity: int
    total_inventory_value: float
    most_expensive_product: Optional[ProductBrief] = None
    lowest_stock_product: Optional[ProductBrief] = None


class CategorySummaryRow(BaseModel):
    category_id: int
    category_name: str
    product_count: int
    total_stock: int
    inventory_value: float
