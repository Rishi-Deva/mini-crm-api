def test_clients_require_auth(client):
    assert client.get("/clients").status_code == 401


def test_register_and_login(client):
    r = client.post("/auth/register", json={"username": "anna", "password": "secret123"})
    assert r.status_code == 201
    r = client.post("/auth/login", data={"username": "anna", "password": "secret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_username(client):
    data = {"username": "anna", "password": "secret123"}
    client.post("/auth/register", json=data)
    assert client.post("/auth/register", json=data).status_code == 409


def test_wrong_password(client):
    client.post("/auth/register", json={"username": "anna", "password": "secret123"})
    r = client.post("/auth/login", data={"username": "anna", "password": "wrong-pass"})
    assert r.status_code == 401


def test_client_crud(auth_client):
    r = auth_client.post("/clients", json={"name": "Иван", "phone": "+995555000111"})
    assert r.status_code == 201
    client_id = r.json()["id"]

    assert len(auth_client.get("/clients").json()) == 1

    r = auth_client.put(f"/clients/{client_id}", json={"name": "Пётр"})
    assert r.status_code == 200
    assert r.json()["name"] == "Пётр"

    assert auth_client.delete(f"/clients/{client_id}").status_code == 204
    assert auth_client.get("/clients").json() == []


def test_deal_for_missing_client(auth_client):
    r = auth_client.post("/deals", json={"client_id": 999, "title": "X"})
    assert r.status_code == 404


def test_negative_amount_rejected(auth_client):
    cid = auth_client.post("/clients", json={"name": "Иван"}).json()["id"]
    r = auth_client.post("/deals", json={"client_id": cid, "title": "X", "amount": -5})
    assert r.status_code == 422


def test_deals_filter_by_status(auth_client):
    cid = auth_client.post("/clients", json={"name": "Иван"}).json()["id"]
    auth_client.post("/deals", json={"client_id": cid, "title": "A", "status": "new"})
    auth_client.post("/deals", json={"client_id": cid, "title": "B", "status": "closed"})

    all_deals = auth_client.get("/deals").json()
    assert len(all_deals) == 2

    closed = auth_client.get("/deals", params={"status": "closed"}).json()
    assert len(closed) == 1
    assert closed[0]["title"] == "B"


def test_cannot_delete_client_with_deals(auth_client):
    cid = auth_client.post("/clients", json={"name": "Иван"}).json()["id"]
    auth_client.post("/deals", json={"client_id": cid, "title": "A"})
    assert auth_client.delete(f"/clients/{cid}").status_code == 409
