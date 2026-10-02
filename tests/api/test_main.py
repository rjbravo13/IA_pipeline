from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_predict_existing_customer():
    response = client.get("/predict/C0001")

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == "C0001"
    assert data["at_risk"] in [0, 1]
    assert data["prediction"] in [
        "Cliente en riesgo",
        "Cliente no está en riesgo",
    ]

    assert 0 <= data["risk_probability"] <= 1


def test_predict_customer_not_found():
    response = client.get("/predict/C9999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Cliente C9999 no encontrado."