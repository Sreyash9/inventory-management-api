"""
Populate the database with sample categories and products.

Usage:
    python3 seed_data.py

Safe to re-run: existing categories/SKUs are skipped rather than duplicated.
"""
from db.database import SessionLocal
from models.category import Category
from models.product import Product

CATEGORIES = ["Electronics", "Groceries", "Stationery", "Furniture"]

PRODUCTS = [
    # name, sku, category, price, quantity
    ("Wireless Mouse", "ELEC-001", "Electronics", 19.99, 50),
    ("Mechanical Keyboard", "ELEC-002", "Electronics", 89.50, 15),
    ("USB-C Charger", "ELEC-003", "Electronics", 24.00, 3),
    ("Basmati Rice 5kg", "GROC-001", "Groceries", 12.75, 100),
    ("Olive Oil 1L", "GROC-002", "Groceries", 8.40, 6),
    ("Ballpoint Pen (Pack of 10)", "STAT-001", "Stationery", 4.99, 200),
    ("A4 Notebook", "STAT-002", "Stationery", 3.25, 8),
    ("Office Chair", "FURN-001", "Furniture", 149.99, 2),
    ("Standing Desk", "FURN-002", "Furniture", 299.00, 1),
]


def run():
    db = SessionLocal()
    try:
        name_to_category: dict[str, Category] = {}
        for name in CATEGORIES:
            existing = db.query(Category).filter(Category.name == name).first()
            if existing is None:
                existing = Category(name=name)
                db.add(existing)
                db.commit()
                db.refresh(existing)
                print(f"Created category: {name}")
            else:
                print(f"Category already exists, skipping: {name}")
            name_to_category[name] = existing

        for name, sku, category_name, price, quantity in PRODUCTS:
            existing = db.query(Product).filter(Product.sku == sku).first()
            if existing is not None:
                print(f"Product SKU already exists, skipping: {sku}")
                continue
            product = Product(
                name=name,
                sku=sku,
                category_id=name_to_category[category_name].id,
                price=price,
                quantity=quantity,
            )
            db.add(product)
            db.commit()
            print(f"Created product: {name} ({sku})")

        print("\nSeeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
