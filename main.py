from fastapi import FastAPI

from api import categories, products, analytics

app = FastAPI(
    title="Inventory Management API",
    description=(
        "A simple learning project demonstrating a layered FastAPI + "
        "PostgreSQL + SQLAlchemy architecture (routes -> services -> "
        "repositories -> models)."
    ),
    version="1.0.0",
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "message": "Inventory API is running. Visit /docs for Swagger UI."}
