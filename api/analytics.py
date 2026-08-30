from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.analytics import CategorySummaryRow, InventorySummary
from services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics"])


@router.get(
    "/analytics/summary",
    response_model=InventorySummary,
    summary="Python Task: totals, most expensive product, lowest stock product",
)
def inventory_summary(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.get_inventory_summary()


@router.get(
    "/reports/category-summary",
    response_model=list[CategorySummaryRow],
    summary="Database Task: category, product_count, total_stock, inventory_value (raw SQL)",
)
def category_summary(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return service.get_category_summary()
