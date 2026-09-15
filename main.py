from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select

# 1. Definimos el modelo de la base de datos
class Servicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente: str
    descripcion: str
    precio: float
    completado: bool = False

# 2. Configuración de la base de datos SQLite
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# 3. Inicializamos FastAPI
app = FastAPI(title="API de Gestión de Servicios con SQLite")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- RUTAS DE LA API ---

# Crear un servicio (CREATE)
@app.post("/servicios", response_model=Servicio, status_code=201)
def crear_servicio(servicio: Servicio, session: Session = Depends(get_session)):
    session.add(servicio)
    session.commit()
    session.refresh(servicio)
    return servicio

# Leer todos los servicios (READ)
@app.get("/servicios", response_model=List[Servicio])
def obtener_servicios(session: Session = Depends(get_session)):
    servicios = session.exec(select(Servicio)).all()
    return servicios

# Leer un servicio por ID (READ)
@app.get("/servicios/{servicio_id}", response_model=Servicio)
def obtener_servicio(servicio_id: int, session: Session = Depends(get_session)):
    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

# Actualizar estado (UPDATE)
@app.put("/servicios/{servicio_id}")
def actualizar_servicio(servicio_id: int, completado: bool, session: Session = Depends(get_session)):
    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    servicio.completado = completado
    session.add(servicio)
    session.commit()
    session.refresh(servicio)
    return {"mensaje": f"Servicio {servicio_id} actualizado", "datos": servicio}

# Eliminar un servicio (DELETE)
@app.delete("/servicios/{servicio_id}")
def eliminar_servicio(servicio_id: int, session: Session = Depends(get_session)):
    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    session.delete(servicio)
    session.commit()
    return {"mensaje": f"Servicio {servicio_id} eliminado exitosamente"}