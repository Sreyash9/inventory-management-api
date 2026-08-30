def test_create_category_success(client):
    response = client.post("/categories", json={"name": "Groceries"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Groceries"
    assert "id" in body


def test_create_category_duplicate_name_fails(client):
    client.post("/categories", json={"name": "Groceries"})
    response = client.post("/categories", json={"name": "Groceries"})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_category_empty_name_fails_validation(client):
    response = client.post("/categories", json={"name": ""})
    assert response.status_code == 422


def test_list_categories(client):
    client.post("/categories", json={"name": "Groceries"})
    client.post("/categories", json={"name": "Electronics"})
    response = client.get("/categories")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert set(names) == {"Groceries", "Electronics"}
