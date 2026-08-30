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


def test_create_product_success(client, category):
    response = _create_product(client, category["id"])
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Wireless Mouse"
    assert body["quantity"] == 50
    assert "created_at" in body and "updated_at" in body


def test_create_product_invalid_category_fails(client):
    response = _create_product(client, category_id=9999)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]


def test_create_product_duplicate_sku_fails(client, category):
    _create_product(client, category["id"])
    response = _create_product(client, category["id"])
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_product_negative_price_fails_validation(client, category):
    response = _create_product(client, category["id"], price=-5)
    assert response.status_code == 422


def test_create_product_negative_quantity_fails_validation(client, category):
    response = _create_product(client, category["id"], quantity=-1)
    assert response.status_code == 422


def test_get_product_success(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.get(f"/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-001"


def test_get_product_not_found(client):
    response = client.get("/products/9999")
    assert response.status_code == 404


def test_list_products(client, category):
    _create_product(client, category["id"], sku="SKU-001")
    _create_product(client, category["id"], sku="SKU-002")
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_product_success(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.put(
        f"/products/{created['id']}",
        json={
            "name": "Wireless Mouse Pro",
            "sku": "SKU-001",
            "category_id": category["id"],
            "price": 29.99,
            "quantity": 40,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Wireless Mouse Pro"
    assert body["price"] == 29.99


def test_update_product_not_found(client, category):
    response = client.put(
        "/products/9999",
        json={
            "name": "Ghost",
            "sku": "GHOST-1",
            "category_id": category["id"],
            "price": 1,
            "quantity": 1,
        },
    )
    assert response.status_code == 404


def test_update_product_invalid_category_fails(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.put(
        f"/products/{created['id']}",
        json={
            "name": "Wireless Mouse",
            "sku": "SKU-001",
            "category_id": 9999,
            "price": 19.99,
            "quantity": 50,
        },
    )
    assert response.status_code == 400


def test_patch_stock_increase_success(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.patch(f"/products/{created['id']}/stock", json={"change": 10})
    assert response.status_code == 200
    assert response.json()["quantity"] == 60


def test_patch_stock_decrease_success(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.patch(f"/products/{created['id']}/stock", json={"change": -20})
    assert response.status_code == 200
    assert response.json()["quantity"] == 30


def test_patch_stock_below_zero_fails(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.patch(f"/products/{created['id']}/stock", json={"change": -1000})
    assert response.status_code == 400
    assert "negative" in response.json()["detail"]


def test_patch_stock_not_found(client):
    response = client.patch("/products/9999/stock", json={"change": 5})
    assert response.status_code == 404


def test_delete_product_success(client, category):
    created = _create_product(client, category["id"]).json()
    response = client.delete(f"/products/{created['id']}")
    assert response.status_code == 204

    follow_up = client.get(f"/products/{created['id']}")
    assert follow_up.status_code == 404


def test_delete_product_not_found(client):
    response = client.delete("/products/9999")
    assert response.status_code == 404


def test_low_stock_filters_correctly(client, category):
    _create_product(client, category["id"], sku="SKU-LOW", quantity=3)
    _create_product(client, category["id"], sku="SKU-HIGH", quantity=100)

    response = client.get("/products/low-stock", params={"threshold": 10})
    assert response.status_code == 200
    skus = [p["sku"] for p in response.json()]
    assert skus == ["SKU-LOW"]


def test_low_stock_default_threshold(client, category):
    _create_product(client, category["id"], sku="SKU-LOW", quantity=5)
    _create_product(client, category["id"], sku="SKU-HIGH", quantity=50)

    response = client.get("/products/low-stock")  # default threshold=10
    assert response.status_code == 200
    skus = [p["sku"] for p in response.json()]
    assert skus == ["SKU-LOW"]
