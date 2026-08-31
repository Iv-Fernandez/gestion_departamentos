from src.services.db_service import get_connection

def obtener_resumen_metricas():
    """Retorna conteos clave para el panel de información."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM departamentos;")
        total_deptos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM integrantes;")
        total_residentes = cursor.fetchone()[0]

        return total_deptos, total_residentes

def obtener_deptos_resumen(filtro: str = ""):
    """
    Obtiene la lista de departamentos ordenada numéricamente de menor a mayor,
    priorizando al Propietario/Titular para la vista general.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        param = f"%{filtro.strip()}%"
        cursor.execute("""
            SELECT 
                d.id AS depto_id,
                d.bloque,
                d.numero_depto,
                COALESCE(i.parentesco, 'PROPIETARIO') AS habitante_tipo,
                (COALESCE(i.nombres, '') || ' ' || COALESCE(i.apellido_paterno, '') || ' ' || COALESCE(i.apellido_materno, '')) AS nombre_titular,
                i.rut AS rut_titular
            FROM departamentos d
            LEFT JOIN integrantes i ON d.id = i.departamento_id AND (
                UPPER(i.parentesco) LIKE '%PROP%' OR 
                UPPER(i.parentesco) LIKE '%TITULAR%' OR 
                UPPER(i.parentesco) LIKE '%ARRENDATARIO%'
            )
            WHERE 
                d.bloque LIKE ? OR
                d.numero_depto LIKE ? OR
                i.nombres LIKE ? OR
                i.apellido_paterno LIKE ? OR
                i.rut LIKE ?
            GROUP BY d.id
            ORDER BY d.bloque ASC, LENGTH(d.numero_depto) ASC, d.numero_depto ASC;
        """, (param, param, param, param, param))
        return cursor.fetchall()

def obtener_detalle_depto_e_integrantes(depto_id: int):
    """Devuelve los datos de la propiedad y la lista de todos sus habitantes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, bloque, numero_depto, fojas, numero_inscripcion, ano_inscripcion, rol_sii, avaluo_fiscal, observaciones
            FROM departamentos WHERE id = ?;
        """, (depto_id,))
        depto = dict(cursor.fetchone())

        cursor.execute("""
            SELECT id, parentesco, nombres, apellido_paterno, apellido_materno, rut, asistencia_reuniones
            FROM integrantes WHERE departamento_id = ?;
        """, (depto_id,))
        integrantes = [dict(row) for row in cursor.fetchall()]

        return depto, integrantes

def verificar_existe_departamento(bloque: str, numero_depto: str) -> bool:
    """Verifica si ya existe un departamento registrado con el mismo bloque y número."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM departamentos 
            WHERE LOWER(TRIM(bloque)) = LOWER(TRIM(?)) 
              AND LOWER(TRIM(numero_depto)) = LOWER(TRIM(?));
        """, (bloque, numero_depto))
        return cursor.fetchone()[0] > 0

def crear_departamento_manual(depto_data: dict, integrantes_list: list):
    """Crea un nuevo departamento y sus integrantes en la base de datos."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO departamentos (bloque, numero_depto, fojas, numero_inscripcion, ano_inscripcion, rol_sii, avaluo_fiscal, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            depto_data["bloque"], depto_data["numero_depto"], depto_data.get("fojas", ""),
            depto_data.get("numero_inscripcion", ""), depto_data.get("ano_inscripcion"),
            depto_data.get("rol_sii", ""), depto_data.get("avaluo_fiscal"), depto_data.get("observaciones", "")
        ))
        
        depto_id = cursor.lastrowid

        for idx in integrantes_list:
            if idx["nombres"] or idx["rut"] or idx["parentesco"]:
                cursor.execute("""
                    INSERT INTO integrantes (departamento_id, parentesco, nombres, apellido_paterno, apellido_materno, rut, asistencia_reuniones)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    depto_id, idx["parentesco"], idx["nombres"],
                    idx["apellido_paterno"], idx["apellido_materno"], idx["rut"], idx.get("asistencia_reuniones", "NO")
                ))
        conn.commit()
        return True

def guardar_cambios_depto_completo(depto_id: int, depto_data: dict, integrantes_list: list):
    """Guarda las modificaciones del departamento y sus integrantes en la BD."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE departamentos
            SET bloque = ?, numero_depto = ?, fojas = ?, numero_inscripcion = ?, 
                ano_inscripcion = ?, rol_sii = ?, avaluo_fiscal = ?, observaciones = ?
            WHERE id = ?;
        """, (
            depto_data["bloque"], depto_data["numero_depto"], depto_data["fojas"],
            depto_data["numero_inscripcion"], depto_data["ano_inscripcion"],
            depto_data["rol_sii"], depto_data["avaluo_fiscal"], depto_data["observaciones"],
            depto_id
        ))

        cursor.execute("DELETE FROM integrantes WHERE departamento_id = ?;", (depto_id,))
        for idx in integrantes_list:
            if idx["nombres"] or idx["rut"] or idx["parentesco"]:
                cursor.execute("""
                    INSERT INTO integrantes (departamento_id, parentesco, nombres, apellido_paterno, apellido_materno, rut, asistencia_reuniones)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    depto_id, idx["parentesco"], idx["nombres"],
                    idx["apellido_paterno"], idx["apellido_materno"], idx["rut"], idx.get("asistencia_reuniones", "NO")
                ))
        conn.commit()
        return True

def eliminar_departamento_completo(depto_id: int):
    """Elimina el departamento y todos sus residentes asociados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM integrantes WHERE departamento_id = ?;", (depto_id,))
        cursor.execute("DELETE FROM departamentos WHERE id = ?;", (depto_id,))
        conn.commit()
        return True