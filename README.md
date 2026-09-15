# 🚀 API de Gestión de Servicios

API RESTful desarrollada con **Python** y **FastAPI** para la administración de registros de servicios y clientes.

## 🛠️ Tecnologías utilizadas

* **Lenguaje:** Python 3.x
* **Framework:** FastAPI
* **Servidor ASGI:** Uvicorn
* **Validación de Datos:** Pydantic

## 📌 Funcionalidades (CRUD)

* `GET /servicios`: Listar todos los servicios registrados.
* `GET /servicios/{id}`: Consultar un servicio específico por su ID.
* `POST /servicios`: Registrar un nuevo servicio.
* `PUT /servicios/{id}`: Actualizar el estado de completado de un servicio.
* `DELETE /servicios/{id}`: Eliminar un servicio del sistema.

## ⚙️ Ejecución en Local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/EmilioManiero/mi_primer_api.git](https://github.com/EmilioManiero/mi_primer_api.git)