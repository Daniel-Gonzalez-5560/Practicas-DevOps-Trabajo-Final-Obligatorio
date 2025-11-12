from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select, SQLModel
from pydantic import ValidationError # Para manejar errores de validación de modelos
from .database import create_db_and_tables, get_session
from .models import Task, TaskCreate, TaskRead

# --- Ciclo de vida de la aplicación ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al inicio: Inicializar la base de datos y crear tablas
    create_db_and_tables()
    yield
    # Al final: No se requiere ninguna acción de limpieza por ahora

app = FastAPI(
    title="Single FastAPI Service",
    version="1.0.0",
    description="API de ejemplo con FastAPI y PostgreSQL usando SQLModel.",
    lifespan=lifespan
)

# --- Manejo de Errores Estándar (FastAPI/Pydantic) ---

# FastAPI ya maneja automáticamente los errores de validación de Pydantic (422 Unprocessable Entity)
# con un contrato JSON estándar.

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador de excepciones HTTP genérico para un contrato de error claro."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# --- Endpoints ---

@app.get("/health", tags=["Utilities"])
def health_check():
    """Endpoint de salud para verificar si la API está en funcionamiento."""
    return {"status": "ok", "message": "API is running!"}

# POST: Crear una nueva tarea
@app.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Crea una nueva tarea en la base de datos.
    
    La validación de campos requeridos y tipos (e.g., título no vacío) la hace Pydantic/SQLModel,
    devolviendo un error 422 si falla.
    """
    try:
        db_task = Task.model_validate(task)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task
    except ValidationError as e:
        # Esto es más un fallback, Pydantic lo maneja en la capa de FastAPI
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )
    except Exception as e:
        # Manejo de otros errores internos (ej. DB no disponible)
        print(f"Error al crear tarea: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la solicitud."
        )

# GET: Obtener todas las tareas
@app.get("/tasks/", response_model=List[TaskRead], tags=["Tasks"])
def read_tasks(session: Session = Depends(get_session)):
    """Recupera todas las tareas existentes de la base de datos."""
    tasks = session.exec(select(Task)).all()
    return tasks