from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductStockUpdate,
    ProductUpdate,
)
from services.product_service import ProductService
from utils.exceptions import ConflictError, NotFoundError, ValidationError

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        return service.create_product(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "",
    response_model=list[ProductResponse],
    summary="List all products",
)
def list_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.list_products()


@router.get(
    "/low-stock",
    response_model=list[ProductResponse],
    summary="List products at or below a stock threshold",
)
def low_stock_products(
    threshold: int = Query(10, ge=0, description="Return products with quantity below this value"),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    try:
        return service.list_low_stock(threshold)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get a single product by id",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        return service.get_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Replace a product",
)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        return service.update_product(product_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse,
    summary="Adjust a product's stock by a signed delta",
)
def update_stock(product_id: int, payload: ProductStockUpdate, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        return service.update_stock(product_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    try:
        service.delete_product(product_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
