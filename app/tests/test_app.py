import pytest
import json
from unittest.mock import patch, MagicMock

# Importar la app y el modelo
# Es importante hacerlo ANTES de configurar la app para testing
from app.app import app, db, Portfolio, cache

@pytest.fixture
def client():
    """Configura la app para testing y crea un cliente de prueba."""
    # Usar una base de datos en memoria para los tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture
def runner():
    """Fixture para ejecutar comandos de CLI de Flask."""
    return app.test_cli_runner()

# --- Mocks para Redis ---
# Usamos patch para "simular" el caché de Redis sin necesitar una instancia real
@patch('app.app.cache')
def test_home_page_from_database(mock_cache, client):
    """Test para verificar que la página se carga desde la BD la primera vez."""
    # 1. Simular que el caché está vacío
    mock_cache.get.return_value = None

    # 2. Añadir datos de prueba a la base de datos en memoria
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
    # Verificar que el contenido viene de la base de datos
    assert b'Datos desde: <strong>DATABASE</strong>' in response.data
    assert b'Test User' in response.data

    # 4. Verificar que los datos se intentaron guardar en el caché
    mock_cache.setex.assert_called_once()

@patch('app.app.cache')
def test_home_page_from_cache(mock_cache, client):
    """Test para verificar que la página se carga desde el caché en la segunda visita."""
    # 1. Simular que el caché SÍ tiene datos
    cached_data = {
        'name': 'Cached User',
        'title': 'Cached Title',
        'summary': 'Cached Summary',
        'skills': ['SkillA', 'SkillB']
    }
    mock_cache.get.return_value = json.dumps(cached_data)

    # 2. Hacer la petición
    response = client.get('/')
    assert response.status_code == 200
    # Verificar que el contenido viene del caché
    assert b'Datos desde: <strong>CACHE</strong>' in response.data
    assert b'Cached User' in response.data

    # 3. Verificar que NO se intentó guardar nada nuevo en el caché
    mock_cache.setex.assert_not_called()

def test_home_page_no_data(client):
    """Test para verificar el comportamiento cuando no hay datos en la BD."""
    response = client.get('/')
    assert response.status_code == 404
    assert b'No portfolio data found' in response.data

def test_health_check(client):
    """Test para el endpoint de health check."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

@patch('app.app.cache')
def test_init_db_command(mock_cache, runner):
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
    mock_cache.delete.assert_called_once_with('portfolio_data')