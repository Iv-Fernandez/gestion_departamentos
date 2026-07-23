from src.services.db_service import get_connection

def buscar_integrantes_y_deptos(filtro: str = ""):
    """
    Busca integrantes y departamentos aplicando un filtro por texto 
    (RUT, nombre, apellido, bloque o número de depto).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        param = f"%{filtro.strip()}%"
        cursor.execute("""
            SELECT 
                d.bloque,
                d.numero_depto,
                i.parentesco,
                (COALESCE(i.nombres, '') || ' ' || COALESCE(i.apellido_paterno, '') || ' ' || COALESCE(i.apellido_materno, '')) AS nombre_completo,
                i.rut,
                i.asistencia_reuniones,
                d.rol_sii
            FROM departamentos d
            LEFT JOIN integrantes i ON d.id = i.departamento_id
            WHERE 
                d.bloque LIKE ? OR
                d.numero_depto LIKE ? OR
                i.nombres LIKE ? OR
                i.apellido_paterno LIKE ? OR
                i.apellido_materno LIKE ? OR
                i.rut LIKE ?
            ORDER BY d.bloque ASC, d.numero_depto ASC;
        """, (param, param, param, param, param, param))
        return cursor.fetchall()

def obtener_resumen_metricas():
    """Retorna conteos clave para el panel de información."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM departamentos;")
        total_deptos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM integrantes;")
        total_integrantes = cursor.fetchone()[0]

        return total_deptos, total_integrantes