from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Field, Session, SQLModel, create_engine, select
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- CONFIGURACIÓN DE SEGURIDAD ---
SECRET_KEY = "mi_clave_secreta_super_segura_para_portfolio" # En producción se usaría una variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- MODELOS DE LA BASE DE DATOS ---

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str

class Servicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente: str
    descripcion: str
    precio: float
    completado: bool = False

# --- CONFIGURACIÓN DE SQLITE ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- FUNCIONES AUXILIARES DE SEGURIDAD ---

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# --- INICIALIZACIÓN DE FASTAPI ---
app = FastAPI(title="API de Gestión de Servicios con Seguridad JWT")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- RUTAS DE AUTENTICACIÓN ---

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a mi API en Render. Visitá /docs para interactuar."}

@app.post("/registro", status_code=201)
def registrar_usuario(username: str, password: str, session: Session = Depends(get_session)):
    user_db = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if user_db:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    nuevo_usuario = Usuario(username=username, password_hash=hash_password(password))
    session.add(nuevo_usuario)
    session.commit()
    return {"mensaje": f"Usuario '{username}' registrado exitosamente"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(Usuario).where(Usuario.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# --- RUTAS DE LA API (SERVICIOS) ---

# Consultas públicas (READ)
@app.get("/servicios", response_model=List[Servicio])
def obtener_servicios(session: Session = Depends(get_session)):
    return session.exec(select(Servicio)).all()

@app.get("/servicios/{servicio_id}", response_model=Servicio)
def obtener_servicio(servicio_id: int, session: Session = Depends(get_session)):
    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

# Rutas protegidas (Requieren Token JWT)
@app.post("/servicios", response_model=Servicio, status_code=201)
def crear_servicio(
    servicio: Servicio, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    session.add(servicio)
    session.commit()
    session.refresh(servicio)
    return servicio

@app.put("/servicios/{servicio_id}")
def actualizar_servicio(
    servicio_id: int, 
    completado: bool, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    servicio.completado = completado
    session.add(servicio)
    session.commit()
    session.refresh(servicio)
    return {"mensaje": f"Servicio {servicio_id} actualizado", "datos": servicio}

@app.delete("/servicios/{servicio_id}")
def eliminar_servicio(
    servicio_id: int, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    servicio = session.get(Servicio, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    session.delete(servicio)
    session.commit()
    return {"mensaje": f"Servicio {servicio_id} eliminado exitosamente"}