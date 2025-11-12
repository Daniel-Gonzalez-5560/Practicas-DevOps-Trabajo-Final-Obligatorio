import os
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from .models import Task # Importar el modelo para la creación de tablas

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.environ.get("DATABASE_URL")

# Configurar el motor de la base de datos
# La opción pool_pre_ping=True ayuda a manejar conexiones inactivas en Docker/Postgres
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Función para inicializar la base de datos (crea las tablas si no existen)
def create_db_and_tables():
    """Crea todas las tablas definidas en los modelos."""
    print("Intentando crear tablas en la DB...")
    # SQLModel.metadata.create_all(engine) crea todas las tablas de los modelos importados
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas exitosamente o ya existentes.")

# Dependencia para obtener la sesión de la base de datos
def get_session() -> Generator[Session, None, None]:
    """Generador para la inyección de dependencia de la sesión de la base de datos."""
    with Session(engine) as session:
        yield session