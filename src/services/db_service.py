import sqlite3
import os
from src.auth.security import hash_password

# Definimos el directorio raíz del proyecto para asegurar las rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "database", "sistema_departamentos.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

def get_connection():
    """Retorna una conexión activa a la base de datos con FK habilitadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la estructura de la base de datos y crea el usuario Admin inicial."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"No se encontró el archivo de esquema SQL en: {SCHEMA_PATH}")

    # 1. Crear las tablas ejecutando el esquema dentro de un bloque de transacción explícito
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_script = f.read()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_script)
        conn.commit()
    finally:
        conn.close()

    # 2. Crear un usuario administrador por defecto si la tabla está vacía
    create_default_admin()

def create_default_admin():
    """Crea un usuario 'admin' por defecto con clave encriptada si no hay usuarios."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        total_usuarios = cursor.fetchone()[0]

        if total_usuarios == 0:
            admin_user = "admin"
            admin_pass = "admin123"
            pass_hashed = hash_password(admin_pass)

            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
                VALUES (?, ?, ?, ?);
            """, (admin_user, pass_hashed, "Administrador Inicial", "admin"))
            
            conn.commit()
            print("--------------------------------------------------")
            print("⚠️ BASE DE DATOS INICIALIZADA CON ÉXITO ⚠️")
            print("Usuario Administrador por defecto creado:")
            print(f" -> Usuario: {admin_user}")
            print(f" -> Clave:   {admin_pass}")
            print("--------------------------------------------------")
    finally:
        conn.close()