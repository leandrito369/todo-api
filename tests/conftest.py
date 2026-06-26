import pytest
from app import create_app


@pytest.fixture
def app():
    """Crea una instancia de la app en modo testing con DB en memoria."""
    application = create_app(testing=True)
    yield application


@pytest.fixture
def client(app):
    """Cliente HTTP de prueba."""
    return app.test_client()
