import hashlib
from src.services.db_service import get_connection

def crear_nuevo_administrador(username: str, password: str, nombre_completo: str):
    pwd_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES (?, ?, ?, 'admin')
            ON CONFLICT(username) DO UPDATE SET password_hash = excluded.password_hash;
        """, (username.strip(), pwd_hash, nombre_completo))
        conn.commit()
        
    print(f"Usuario '{username}' creado exitosamente con permisos de Administrador.")

if __name__ == "__main__":
    crear_nuevo_administrador("pepe", "1928", "Pepe (Administrador)")