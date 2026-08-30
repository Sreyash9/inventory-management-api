def _create_product(client, category_id, **overrides):
    payload = {
        "name": "Wireless Mouse",
        "sku": "SKU-001",
        "category_id": category_id,
        "price": 19.99,
        "quantity": 50,
    }
    payload.update(overrides)
    return client.post("/products", json=payload)


def test_inventory_summary_empty(client):
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_products"] == 0
    assert body["total_quantity"] == 0
    assert body["total_inventory_value"] == 0
    assert body["most_expensive_product"] is None
    assert body["lowest_stock_product"] is None


def test_inventory_summary_calculations(client, category):
    _create_product(client, category["id"], sku="SKU-A", price=10.0, quantity=5)
    _create_product(client, category["id"], sku="SKU-B", price=100.0, quantity=1)
    _create_product(client, category["id"], sku="SKU-C", price=50.0, quantity=20)

    response = client.get("/analytics/summary")
    assert response.status_code == 200
    body = response.json()

    assert body["total_products"] == 3
    assert body["total_quantity"] == 26  # 5 + 1 + 20
    assert body["total_inventory_value"] == 1150.0  # 10*5 + 100*1 + 50*20
    assert body["most_expensive_product"]["sku"] == "SKU-B"
    assert body["lowest_stock_product"]["sku"] == "SKU-B"  # quantity=1 is lowest


def test_category_summary_report(client):
    cat_a = client.post("/categories", json={"name": "Electronics"}).json()
    cat_b = client.post("/categories", json={"name": "Empty Category"}).json()

    _create_product(client, cat_a["id"], sku="SKU-A", price=10.0, quantity=5)
    _create_product(client, cat_a["id"], sku="SKU-B", price=20.0, quantity=3)

    response = client.get("/reports/category-summary")
    assert response.status_code == 200
    rows = {row["category_name"]: row for row in response.json()}

    assert rows["Electronics"]["product_count"] == 2
    assert rows["Electronics"]["total_stock"] == 8
    assert rows["Electronics"]["inventory_value"] == 110.0  # 10*5 + 20*3

    # Category with no products should still appear, with zeros
    assert rows["Empty Category"]["product_count"] == 0
    assert rows["Empty Category"]["total_stock"] == 0
    assert rows["Empty Category"]["inventory_value"] == 0
