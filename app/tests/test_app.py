import pytest
import json
from unittest.mock import MagicMock

# Importar la factory y las extensiones
from app.app import create_app, db, Portfolio, cache

@pytest.fixture
def app():
    """Crea una instancia de la aplicación para pruebas."""
    # Usamos la factory para crear una app con la configuración de testing
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


def test_home_page_from_database(client):
    """Test para verificar que la página se carga desde la BD la primera vez."""
    # 1. Simular que el caché está vacío
    cache.get.return_value = None

    # 2. Añadir datos de prueba a la base de datos en memoria
    with client.application.app_context():
        test_data = Portfolio(
            name="Test User",
            title="Test Title",
            summary="Test Summary",
            skills="Skill1, Skill2"
        )
        db.session.add(test_data)
        db.session.commit()

    # 3. Hacer la petición a la ruta principal
    response = client.get('/')
    assert response.status_code == 200
    assert b'Datos desde: <strong>database</strong>' in response.data
    assert b'Test User' in response.data

    # 4. Verificar que los datos se intentaron guardar en el caché
    cache.setex.assert_called_once()

def test_home_page_from_cache(client):
    """Test para verificar que la página se carga desde el caché en la segunda visita."""
    # 1. Simular que el caché SÍ tiene datos
    cached_data = {
        'name': 'Cached User',
        'title': 'Cached Title',
        'summary': 'Cached Summary',
        'skills': ['SkillA', 'SkillB']
    }
    cache.get.return_value = json.dumps(cached_data)

    # 2. Hacer la petición
    response = client.get('/')
    assert response.status_code == 200
    assert b'Datos desde: <strong>cache</strong>' in response.data
    assert b'Cached User' in response.data

    # 3. Verificar que NO se intentó acceder a la BD ni guardar en caché
    cache.setex.assert_not_called()

def test_home_page_no_data(client):
    """Test para verificar el comportamiento cuando no hay datos en la BD."""
    cache.get.return_value = None
    response = client.get('/')
    assert response.status_code == 404
    assert b'No portfolio data found' in response.data

def test_health_check(client):
    """Test para el endpoint de health check."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_init_db_command(runner, app):
    """Test para verificar que el comando 'init-db' funciona correctamente."""
    # Ejecutar el comando
    result = runner.invoke(args=['init-db'])
    assert 'Base de datos inicializada' in result.output

    # Verificar que los datos se insertaron en la base de datos
    with app.app_context():
        item = Portfolio.query.first()
        assert item is not None
        assert item.name == "Roxs"

    # Verificar que la caché fue limpiada
    cache.delete.assert_called_once_with('portfolio_data')
