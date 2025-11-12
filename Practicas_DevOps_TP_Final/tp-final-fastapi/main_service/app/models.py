from typing import Optional
from sqlmodel import Field, SQLModel, Text

# Definición del esquema base para las tareas
class TaskBase(SQLModel):
    # El título es obligatorio (no puede ser None) y debe tener un límite de 255 caracteres.
    title: str = Field(index=True, max_length=255, nullable=False)
    
    # La descripción es opcional. Usamos 'Text' para permitir descripciones largas en la DB.
    description: Optional[str] = Field(default=None, sa_column=Text())
    
    # Estado de la tarea, por defecto es False (pendiente).
    is_completed: bool = Field(default=False)


# 1. Modelo de la Base de Datos (DB)
# Esta clase representa la tabla 'task' en PostgreSQL.
class Task(TaskBase, table=True):
    # ID es la clave primaria y es autogenerado por la DB.
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Definir el nombre de la tabla (opcional, pero buena práctica)
    __tablename__ = "task"


# 2. Esquema de Entrada (POST Request)
# Se usa para recibir datos al crear una nueva tarea. No necesita el ID.
class TaskCreate(TaskBase):
    pass


# 3. Esquema de Salida (GET/POST Response)
# Se usa para enviar datos al cliente (incluye el ID y el status).
class TaskRead(TaskBase):
    id: int
    
   