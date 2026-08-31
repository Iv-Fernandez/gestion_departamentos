import hashlib
from src.services.db_service import get_connection

def hash_password(password: str) -> str:
    """Genera un hash SHA-256 para la contraseña."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def autenticar_usuario(username: str, password: str):
    """
    Verifica si las credenciales coinciden con algún usuario en la BD.
    Retorna el diccionario con la información del usuario si es correcto, o None si falla.
    """
    hashed_pwd = hash_password(password)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, nombre_completo, rol 
            FROM usuarios 
            WHERE username = ? AND password_hash = ?;
        """, (username.strip(), hashed_pwd))
        
        usuario = cursor.fetchone()
        
        if usuario:
            return dict(usuario)
        return None