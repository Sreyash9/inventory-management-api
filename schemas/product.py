from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    category_id: int = Field(..., gt=0)
    price: float = Field(..., gt=0, description="Unit price, must be greater than 0")
    quantity: int = Field(0, ge=0, description="Current stock quantity, cannot be negative")


class ProductUpdate(BaseModel):
    """Full replacement payload for PUT /products/{id}."""

    name: str = Field(..., min_length=1, max_length=150)
    sku: str = Field(..., min_length=1, max_length=50)
    category_id: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class ProductStockUpdate(BaseModel):
    """Payload for PATCH /products/{id}/stock.

    `change` is a signed delta applied to the current quantity
    (e.g. -5 to remove 5 units, +20 to restock 20 units).
    """

    change: int = Field(..., description="Signed quantity delta to apply, e.g. -5 or +20")


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    category_id: int
    price: float
    quantity: int
    created_at: datetime
    updated_at: datetime
