import sqlite3
import os
import sys
import hashlib

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

BASE_DIR = get_base_dir()
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "sistema_departamentos.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'admin'
            );
        """)

        # Tabla departamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bloque TEXT NOT NULL,
                numero_depto TEXT NOT NULL,
                fojas TEXT,
                numero_inscripcion TEXT,
                ano_inscripcion INTEGER,
                rol_sii TEXT,
                avaluo_fiscal REAL,
                observaciones TEXT,
                UNIQUE(bloque, numero_depto)
            );
        """)

        # Tabla integrantes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                departamento_id INTEGER NOT NULL,
                parentesco TEXT,
                nombres TEXT,
                apellido_paterno TEXT,
                apellido_materno TEXT,
                rut TEXT,
                asistencia_reuniones TEXT DEFAULT 'NO',
                FOREIGN KEY (departamento_id) REFERENCES departamentos (id) ON DELETE CASCADE
            );
        """)

        # Tabla Hoja de Convivencia con soporte para fecha de modificación
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_convivencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                departamento_id INTEGER,
                es_general INTEGER DEFAULT 0,
                tipo_evento TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TEXT,
                autor TEXT NOT NULL,
                FOREIGN KEY (departamento_id) REFERENCES departamentos (id) ON DELETE CASCADE
            );
        """)

        # Usuarios por defecto
        admin_pass = hash_password("admin123")
        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES ('admin', ?, 'Administrador Inicial', 'admin')
            ON CONFLICT(username) DO UPDATE SET password_hash = excluded.password_hash;
        """, (admin_pass,))

        pepe_pass = hash_password("1928")
        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES ('pepe', ?, 'Pepe (Administrador)', 'admin')
            ON CONFLICT(username) DO UPDATE SET password_hash = excluded.password_hash;
        """, (pepe_pass,))

        conn.commit()

if __name__ == "__main__":
    init_db()