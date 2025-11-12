import pytest
from httpx import Client
from sqlmodel import create_engine, Session, SQLModel

# Importar la aplicación principal y los modelos
from main_service.app.main import app
from main_service.app.database import get_session
from main_service.app.models import Task, TaskCreate

# ----------------------------------------------------
# 1. Configuración de la Base de Datos de Prueba (SQLite en memoria)
# ----------------------------------------------------

# Usaremos SQLite para las pruebas, ya que es más rápido y fácil de configurar
# La URL de la DB en memoria
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Crear un motor de prueba
engine = create_engine(sqlite_url, echo=False)

# Función para crear las tablas antes de cada test
def create_db_and_tables():
    """Crea las tablas en la base de datos de prueba."""
    SQLModel.metadata.create_all(engine)

# Función para limpiar las tablas después de cada test
def clear_db_and_tables():
    """Elimina las tablas de la base de datos de prueba."""
    SQLModel.metadata.drop_all(engine)

# Sobreescribir la dependencia get_session para usar la DB de prueba
def get_session_override():
    """Proporciona una sesión que usa la base de datos de prueba."""
    with Session(engine) as session:
        yield session

# Reemplazar la dependencia en la aplicación
app.dependency_overrides[get_session] = get_session_override

# Cliente de pruebas (usando context manager)
@pytest.fixture(name="client")
def client_fixture():
    """Fixture que proporciona un cliente HTTP para pruebas."""
    # Configuración: limpiar/crear tablas antes de las pruebas
    clear_db_and_tables()
    create_db_and_tables()
    # Ejecutar el test
    with Client(app=app, base_url="http://test") as client:
        yield client
    # Limpieza: (aunque se hace al inicio, es buena práctica)
    clear_db_and_tables()

# ----------------------------------------------------
# 2. Pruebas Funcionales
# ----------------------------------------------------

def test_health_check(client: Client):
    """Verifica el endpoint de salud."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running!"}

def test_create_and_read_task(client: Client):
    """Prueba la creación y lectura de una tarea."""
    
    # 1. Crear tarea (POST)
    task_data = {"title": "Comprar leche", "description": "Leche entera", "is_completed": False}
    response_create = client.post("/tasks/", json=task_data)
    
    # Verificación de la creación
    assert response_create.status_code == 201
    created_task = response_create.json()
    assert created_task["title"] == "Comprar leche"
    assert "id" in created_task
    
    # 2. Leer tareas (GET)
    response_read = client.get("/tasks/")
    
    # Verificación de la lectura
    assert response_read.status_code == 200
    tasks_list = response_read.json()
    assert len(tasks_list) == 1
    assert tasks_list[0]["title"] == "Comprar leche"
    
def test_validation_error_422(client: Client):
    """Prueba que la validación de Pydantic/FastAPI devuelva 422."""
    
    # Intenta crear una tarea con un título demasiado largo (definido en models.py:255)
    # Creamos un string con 300 caracteres
    long_title = "A" * 300
    task_data = {"title": long_title}
    
    response = client.post("/tasks/", json=task_data)
    
    # Debe fallar con el código de validación de FastAPI
    assert response.status_code == 422
    
    # Verificar que el contrato de error JSON sea claro y estándar
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "title"]
    assert "Value error" in error_detail["msg"] # Mensaje de error de validación
    
def test_validation_required_field(client: Client):
    """Prueba que un campo requerido no esté ausente."""
    
    # Intenta crear una tarea sin el campo 'title' (que es obligatorio)
    task_data = {"description": "Esto no debería funcionar"}
    
    response = client.post("/tasks/", json=task_data)
    
    # Debe fallar con el código de validación de FastAPI
    assert response.status_code == 422
    
    # Verificar que el contrato de error JSON indique el campo faltante
    error_detail = response.json()["detail"][0]
    assert error_detail["loc"] == ["body", "title"]
    assert "Field required" in error_detail["msg"]