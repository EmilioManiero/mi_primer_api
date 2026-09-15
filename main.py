from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="API de Gestión de Servicios - Portfolio")

# 1. Definimos la estructura de datos con Pydantic (Validación automática)
class Servicio(BaseModel):
    id: int
    cliente: str
    descripcion: str
    precio: float
    completado: bool = False

# 2. Base de datos simulada en memoria
base_de_datos: List[Servicio] = [
    Servicio(id=1, cliente="Estudio Jurídico", descripcion="Diseño de Landing Page", precio=150.0, completado=True),
    Servicio(id=2, cliente="Café de la Plaza", descripcion="Sistema de Pedidos", precio=300.0, completado=False)
]

# --- RUTAS DE LA API (Endpoints) ---

# Obtener todos los servicios (READ)
@app.get("/servicios", response_model=List[Servicio])
def obtener_servicios():
    return base_de_datos

# Obtener un servicio por ID (READ)
@app.get("/servicios/{servicio_id}", response_model=Servicio)
def obtener_servicio_por_id(servicio_id: int):
    for servicio in base_de_datos:
        if servicio.id == servicio_id:
            return servicio
    raise HTTPException(status_code=404, detail="Servicio no encontrado")

# Crear un nuevo servicio (CREATE)
@app.post("/servicios", response_model=Servicio, status_code=201)
def crear_servicio(nuevo_servicio: Servicio):
    # Verificamos que el ID no exista
    for s in base_de_datos:
        if s.id == nuevo_servicio.id:
            raise HTTPException(status_code=400, detail="El ID ya existe")
    
    base_de_datos.append(nuevo_servicio)
    return nuevo_servicio

# Eliminar un servicio (DELETE)
@app.delete("/servicios/{servicio_id}")
def eliminar_servicio(servicio_id: int):
    for index, servicio in enumerate(base_de_datos):
        if servicio.id == servicio_id:
            base_de_datos.pop(index)
            return {"mensaje": f"Servicio con ID {servicio_id} eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Servicio no encontrado")

# Actualizar el estado de un servicio (UPDATE)
@app.put("/servicios/{servicio_id}")
def actualizar_servicio(servicio_id: int, completado: bool):
    for servicio in base_de_datos:
        if servicio.id == servicio_id:
            servicio.completado = completado
            return {"mensaje": f"Servicio {servicio_id} actualizado", "datos": servicio}
    raise HTTPException(status_code=404, detail="Servicio no encontrado")