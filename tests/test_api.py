"""
Suite de testes automatizados para a API do Classificador BBC.
Executa validacoes de inferencia, endpoints de saude e tratamento de erros.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Inicializa o cliente executando o ciclo de vida (lifespan) da aplicacao."""
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    """Valida se o endpoint de saude retorna status 200 e confirma carregamento do modelo."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "classes" in data
    assert len(data["classes"]) == 5


def test_predict_endpoint_valid_business(client):
    """Valida inferencia direta para texto tipicamente corporativo/financeiro."""
    payload = {
        "text": "Shares rose sharply on the London stock exchange today following unexpected corporate profits."
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_category"] == "business"
    assert "confidence" in data
    assert "probabilities" in data
    assert "json_output" in data
    assert len(data["probabilities"]) == 5


def test_predict_endpoint_short_text_error(client):
    """Valida que textos excessivamente curtos sao rejeitados com HTTP 422."""
    payload = {"text": "hi"}
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422


def test_scrape_endpoint_invalid_domain(client):
    """Valida que URLs fora da BBC News sao rejeitadas com erro 400."""
    payload = {"url": "https://www.google.com"}
    response = client.post("/api/scrape-and-predict", json=payload)
    assert response.status_code == 400
    assert "bbc.com" in response.json()["detail"].lower()


def test_scrape_endpoint_portuguese_rejection(client):
    """Valida que URLs em lingua portuguesa sao orientadas a usar BBC International."""
    payload = {"url": "https://www.bbc.com/portuguese/articles/c0123456789o"}
    response = client.post("/api/scrape-and-predict", json=payload)
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert "inglês" in detail or "ingles" in detail
