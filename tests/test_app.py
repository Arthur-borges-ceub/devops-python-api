import pytest
from app import create_app

@pytest.fixture
def app():
    application = create_app()
    application.config.update({
        "TESTING": True,
    })
    yield application

@pytest.fixture
def client(app):
    return app.test_client()

def test_root_endpoint(client):
    """Testa a rota raiz (/)"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "devops-python-api"
    assert data["status"] == "online"
    assert "version" in data

def test_health_check(client):
    """Testa o endpoint de verificação de saúde (/health)"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_info_endpoint(client):
    """Testa o endpoint de metadados (/api/v1/info)"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "devops-python-api"
    assert data["discipline"] == "Integração DevOps"
    assert isinstance(data["endpoints"], list)

def test_version_endpoint(client):
    """Testa o endpoint de consulta de versão (/api/v1/version)"""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.get_json()
    assert data["application"] == "devops-python-api"
    assert "version" in data

def test_tools_endpoint(client):
    """Testa o endpoint de listagem de ferramentas (/api/v1/tools)"""
    response = client.get("/api/v1/tools")
    assert response.status_code == 200
    data = response.get_json()
    assert "tools" in data
    assert len(data["tools"]) >= 4

def test_not_found_endpoint(client):
    """Testa tratamento para rota inexistente (404)"""
    response = client.get("/rota-inexistente")
    assert response.status_code == 404
    data = response.get_json()
    assert data["status_code"] == 404
    assert "error" in data
