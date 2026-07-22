import bcrypt

def hash_password(password: str) -> str:
    """Encripta una contraseña usando bcrypt con salt automático."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))