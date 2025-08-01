import pytest
import json
from unittest.mock import patch

# Importar la factory y las extensiones
from app.app import create_app, db, Portfolio

@pytest.fixture
def app():
    """Crea una instancia de la aplicación para pruebas."""
    _app = create_app(testing=True)
    yield _app

@pytest.fixture
def client(app):
    """Crea un cliente de prueba y gestiona el contexto y la BD."""
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def runner(app):
    """Fixture para ejecutar comandos de CLI de Flask."""
    return app.test_cli_runner()

@patch('app.app.cache.get')
@patch('app.app.cache.setex')
def test_home_page_from_database(mock_setex, mock_get, client):
    """Test para verificar que la página se carga desde la BD la primera vez."""
    mock_get.return_value = None

    with client.application.app_context():
        test_data = Portfolio(
            name="Test User",
            title="Test Title",
            summary="Test Summary",
            skills="Skill1, Skill2"
        )
        db.session.add(test_data)
        db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b'Datos desde: <strong>database</strong>' in response.data
    assert b'Test User' in response.data

    mock_get.assert_called_once_with('portfolio_data')
    mock_setex.assert_called_once()

@patch('app.app.cache.get')
@patch('app.app.cache.setex')
def test_home_page_from_cache(mock_setex, mock_get, client):
    """Test para verificar que la página se carga desde el caché en la segunda visita."""
    cached_data = {
        'name': 'Cached User',
        'title': 'Cached Title',
        'summary': 'Cached Summary',
        'skills': ['SkillA', 'SkillB']
    }
    mock_get.return_value = json.dumps(cached_data)

    response = client.get('/')
    assert response.status_code == 200
    assert b'Datos desde: <strong>cache</strong>' in response.data
    assert b'Cached User' in response.data

    mock_get.assert_called_once_with('portfolio_data')
    mock_setex.assert_not_called()

@patch('app.app.cache.get')
def test_home_page_no_data(mock_get, client):
    """Test para verificar el comportamiento cuando no hay datos en la BD."""
    mock_get.return_value = None
    response = client.get('/')
    assert response.status_code == 404
    assert b'No portfolio data found' in response.data

def test_health_check(client):
    """Test para el endpoint de health check."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

@patch('app.app.cache.delete')
def test_init_db_command(mock_delete, runner, app):
    """Test para verificar que el comando 'init-db' funciona correctamente."""
    result = runner.invoke(args=['init-db'])
    assert 'Base de datos inicializada' in result.output

    with app.app_context():
        item = Portfolio.query.first()
        assert item is not None
        assert item.name == "Litocruz"

    mock_delete.assert_called_once_with('portfolio_data')
