from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.category import CategoryCreate, CategoryResponse
from services.category_service import CategoryService
from utils.exceptions import ConflictError

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    try:
        return service.create_category(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="List all categories",
)
def list_categories(db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.list_categories()
