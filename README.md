# Inventory API

A small learning project: a FastAPI + PostgreSQL inventory management API
with a clean, layered architecture (routes → services → repositories →
models), Alembic migrations, and a Pytest test suite.

No authentication, no domain complexity — this is deliberately scoped as
a focused exercise in FastAPI + SQLAlchemy + PostgreSQL fundamentals:
CRUD, foreign keys, JOINs, GROUP BY/aggregation, query parameters, and
Python data-crunching over ORM results.

---

## 1. Project Overview

**Entities**

- `categories` — `id`, `name`
- `products` — `id`, `name`, `sku`, `category_id` (FK → categories), `price`,
  `quantity`, `created_at`, `updated_at`

**What it does**

- Full CRUD on products, simple create/list on categories
- Stock adjustment via a signed delta (`PATCH /products/{id}/stock`), with a
  guard against going negative
- A low-stock filter (`GET /products/low-stock?threshold=...`)
- An analytics endpoint that computes totals, most-expensive product, and
  lowest-stock product **in Python** using loops/comprehensions over ORM
  objects (the "Python Task")
- A reporting endpoint that runs **hand-written raw SQL** (JOIN + GROUP BY)
  to roll up product counts, stock, and inventory value per category (the
  "Database Task")

**Project structure**

```
inventory_api/
├── main.py                  # FastAPI app, router registration
├── api/                     # Thin route handlers (HTTP concerns only)
│   ├── categories.py
│   ├── products.py
│   └── analytics.py
├── services/                 # Business logic, validation, calculations
│   ├── category_service.py
│   ├── product_service.py
│   └── analytics_service.py  # Python Task + orchestrates Database Task
├── repositories/              # DB access only (queries, persistence)
│   ├── category_repository.py
│   └── product_repository.py # includes the raw SQL category report
├── models/                   # SQLAlchemy ORM models
│   ├── category.py
│   └── product.py
├── schemas/                  # Pydantic request/response models
│   ├── category.py
│   ├── product.py
│   └── analytics.py
├── db/                       # Engine/session/config
│   ├── config.py
│   └── database.py
├── utils/
│   └── exceptions.py          # Domain exceptions (NotFound/Conflict/Validation)
├── alembic/                   # DB migrations
│   └── versions/
├── sql/
│   └── important_queries.sql  # Standalone copy of key raw SQL queries
├── tests/                     # Pytest suite (SQLite-backed, see note below)
├── seed_data.py                # Sample data loader
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md
```

**Route → Service → Repository flow**

Route handlers in `api/` never touch the database or contain business
rules — they parse the request, call a service method, and translate
domain exceptions (`NotFoundError`, `ConflictError`, `ValidationError`)
into the right HTTP status code. `services/` hold validation and business
logic (e.g. "a product can't be created for a category that doesn't
exist", "stock can't go negative"). `repositories/` hold only DB
queries/persistence, including the one raw-SQL query used for the
category report.

---

## 2. Installation

**Requirements:** Python 3.11+, PostgreSQL (locally installed or reachable).

```bash
# 1. Clone / unzip the project, then from the project root:
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 3. Environment / Configuration

Copy the example env file and adjust it to match your local PostgreSQL
credentials:

```bash
cp .env.example .env
```

`.env`:

```
DATABASE_URL=postgresql+psycopg2://inventory_user:inventory_pass@localhost:5432/inventory_db
```

Configuration is loaded via `pydantic-settings` in `db/config.py` — no
credentials are hard-coded anywhere in source.

---

## 4. PostgreSQL Database Setup

If you don't already have a database/user, create them (adjust
credentials to match your `.env`):

```bash
sudo -u postgres psql -c "CREATE USER inventory_user WITH PASSWORD 'inventory_pass';"
sudo -u postgres psql -c "CREATE DATABASE inventory_db OWNER inventory_user;"
```

Apply migrations to create the schema:

```bash
alembic upgrade head
```

This creates the `categories` and `products` tables, including the
foreign key (`products.category_id → categories.id`, `ON DELETE CASCADE`)
and unique constraints on `categories.name` and `products.sku`.

**(Optional) Load sample data:**

```bash
python3 seed_data.py
```

This inserts 4 categories and 9 products (safe to re-run — it skips
records that already exist).

---

## 5. Running the Application

```bash
uvicorn main:app --reload
```

- API base URL: `http://127.0.0.1:8000`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 6. Running Tests

```bash
pytest -v
```

**Design decision:** tests run against an **in-memory SQLite** database
(configured in `tests/conftest.py`), not PostgreSQL, even though the
application targets PostgreSQL at runtime. This keeps the suite fast,
fully isolated, and runnable on any machine without a live Postgres
service (useful for CI or quick local checks). Because the schema here
is simple (no Postgres-specific types/functions in the ORM-mapped
tables), SQLAlchemy's dialect abstraction makes this safe. The one
Postgres-specific piece — the raw SQL category report — is still
exercised through the same SQLite connection in `test_analytics.py`
since the query only uses standard SQL (JOIN, GROUP BY, COALESCE) that
both dialects support.

The suite covers **26 tests**, both success and failure paths, across
categories, products, stock adjustment, deletion, low-stock filtering,
and both analytics endpoints (empty-state and populated-state).

---

## 7. API Endpoint Summary

| Method | Path                              | Description                                                   |
|--------|-----------------------------------|-----------------------------------------------------------------|
| POST   | `/categories`                     | Create a category                                              |
| GET    | `/categories`                     | List all categories                                             |
| POST   | `/products`                       | Create a product                                                 |
| GET    | `/products`                       | List all products                                                 |
| GET    | `/products/{id}`                  | Get a single product                                              |
| PUT    | `/products/{id}`                  | Replace a product (full update)                                   |
| PATCH  | `/products/{id}/stock`            | Adjust stock by a signed delta (`{"change": -5}` or `{"change": 20}`) |
| DELETE | `/products/{id}`                  | Delete a product                                                    |
| GET    | `/products/low-stock?threshold=N` | List products with `quantity < threshold` (default `threshold=10`)  |
| GET    | `/analytics/summary`              | **Python Task**: totals, most expensive product, lowest-stock product |
| GET    | `/reports/category-summary`       | **Database Task**: raw SQL — category, product_count, total_stock, inventory_value |

Full interactive documentation, including request/response schemas and
example payloads, is available at `/docs`.

### Example error responses

| Scenario                                   | Status |
|---------------------------------------------|--------|
| Product/category not found                   | 404    |
| Duplicate SKU / duplicate category name        | 409    |
| Invalid `category_id` on create/update           | 400    |
| Stock change would go negative                     | 400    |
| Invalid request body (e.g. negative price)           | 422 (Pydantic validation) |

---

## 8. Database Deliverables

- **Migrations:** `alembic/versions/d0140d1362f5_create_categories_and_products_tables.py`
  — creates both tables, the FK, and unique indexes. Generated via
  `alembic revision --autogenerate` and verified by applying it to a real
  local PostgreSQL instance.
- **Important SQL queries:** see [`sql/important_queries.sql`](sql/important_queries.sql).
  The primary one (category rollup: product_count, total_stock,
  inventory_value) is also embedded and actually executed in
  `repositories/product_repository.py::get_category_summary`.
- **Seed data:** run `python3 seed_data.py` after migrating (see §4).

---

## 9. API Testing via Swagger UI

With the app running, open `http://127.0.0.1:8000/docs`. Suggested
success/failure cases to try (matching what the automated tests cover):

**Successful cases**
- `POST /categories` with a new name → `201`
- `POST /products` with a valid `category_id` and unique `sku` → `201`
- `GET /products/{id}` for an existing product → `200`
- `PATCH /products/{id}/stock` with `{"change": 10}` → `200`, quantity increases
- `GET /products/low-stock?threshold=10` → `200`, filtered list
- `GET /analytics/summary` and `GET /reports/category-summary` → `200`

**Unsuccessful cases**
- `POST /categories` with a name that already exists → `409`
- `POST /products` with a non-existent `category_id` → `400`
- `POST /products` with a `sku` that already exists → `409`
- `POST /products` with `price: -5` → `422` (Pydantic validation)
- `GET /products/{id}` for a non-existent id → `404`
- `PATCH /products/{id}/stock` with a `change` that would push quantity
  below zero → `400`
- `DELETE /products/{id}` twice in a row → `204` then `404`

---

## 10. Important Design Decisions

1. **Layered architecture.** Routes stay thin and only handle HTTP
   concerns; business rules live in `services/`; all SQL/ORM queries
   live in `repositories/`. This keeps route functions readable and
   makes business logic unit-testable independent of FastAPI.

2. **Domain exceptions, not HTTP exceptions, in the service layer.**
   `services/` raise `NotFoundError` / `ConflictError` / `ValidationError`
   (plain Python exceptions in `utils/exceptions.py`). Only the `api/`
   layer knows about HTTP status codes and converts these into
   `HTTPException`s. This keeps the service layer framework-agnostic.

3. **Stock adjustment is a signed delta, not an absolute set.**
   `PATCH /products/{id}/stock` takes `{"change": ±N}` rather than a new
   absolute quantity. This models a realistic "restock" / "sell" /
   "adjust" operation and makes it natural to guard against the
   resulting quantity going negative — a state check that wouldn't be
   meaningful with a `PUT`-style absolute replacement (which is why
   full replacement lives on `PUT /products/{id}` instead).

4. **The "Python Task" is intentionally done in Python, not SQL.**
   `AnalyticsService.get_inventory_summary` pulls all products via the
   ORM and then computes totals/most-expensive/lowest-stock using plain
   loops and comprehensions, per the stated goal of exercising that
   skill — even though `SUM()`/`MAX()`/`ORDER BY ... LIMIT 1` could do
   this faster in the database.

5. **The "Database Task" is intentionally raw SQL, not the ORM query
   builder.** `ProductRepository.get_category_summary` uses
   `sqlalchemy.text()` with a hand-written `LEFT JOIN` + `GROUP BY` +
   `COALESCE`, per the stated goal of exercising manual SQL. A `LEFT
   JOIN` (not `INNER JOIN`) is used so categories with zero products
   still appear in the report, with `0` rather than `NULL` for the
   aggregates.

6. **Tests run on SQLite, the app runs on PostgreSQL.** See §6 for the
   reasoning — this is a common, pragmatic tradeoff for small services
   with no Postgres-specific SQL in the ORM-mapped path.

7. **Unique constraints at the DB layer, checked pre-emptively in the
   service layer.** Both `categories.name` and `products.sku` are
   unique-indexed in the schema (belt) and explicitly checked in the
   service before insert (suspenders), so API consumers get a clean
   `409 Conflict` with a clear message instead of a raw database
   integrity-error stack trace.

8. **`ON DELETE CASCADE` on the category → product FK.** Deleting a
   category deletes its products rather than leaving orphaned rows or
   failing with a FK violation. For a real production system this would
   likely instead be a soft-delete or a blocking constraint, but for
   this learning project's scope, cascade keeps behavior simple and
   predictable.
