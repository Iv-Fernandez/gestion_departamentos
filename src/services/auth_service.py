from src.services.db_service import get_connection
from src.auth.security import verify_password

def authenticate_user(username: str, password_plain: str):
    """
    Verifica las credenciales del usuario.
    Retorna los datos del usuario si es correcto, o None si falla.
    """
    if not username or not password_plain:
        return None

    with get_connection() as conn:
        cursor = conn.cursor()
        # Usamos consulta parametrizada (?) para prevenir Inyección SQL
        cursor.execute("""
            SELECT id, username, password_hash, nombre_completo, rol 
            FROM usuarios 
            WHERE username = ?;
        """, (username.strip(),))
        
        user = cursor.fetchone()

        if user and verify_password(password_plain, user["password_hash"]):
            # Retornamos los datos sin el hash de la clave
            return {
                "id": user["id"],
                "username": user["username"],
                "nombre_completo": user["nombre_completo"],
                "rol": user["rol"]
            }
    
    return None