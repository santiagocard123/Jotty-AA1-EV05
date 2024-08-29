from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# Crear una instancia de FastAPI
app = FastAPI()

# Conectar a la base de datos SQLite (se creará automáticamente si no existe)
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn



# Creamos la tabla de usuarios si no existe esto nos permite crear la base de datos sin tener instlado sqlite en el sistema
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar la base de datos
init_db()

# Modelo para la autenticación
class User(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(user: User):
    """
    Endpoint para registrar un nuevo usuario.
    """
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (user.username, user.password)) #consulta sql para insertar datos a la bd de users.db
        conn.commit()
        return {"message": "Registro exitoso"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    finally:
        conn.close()

@app.post("/login")
async def login(user: User):
    """
    Endpoint para iniciar sesión.
    """
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (user.username, user.password)).fetchone()
    conn.close()
    
    if user_row is None:
        raise HTTPException(status_code=401, detail="Error en la autenticación")
    
    return {"message": "Autenticación satisfactoria"}


# Para ejecutar el servidor, se utiliza el siguiente comando:
# uvicorn main:app --reload