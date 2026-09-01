from datetime import datetime
from src.services.db_service import get_connection

def asegurar_columna_modificacion():
    """Verifica y agrega la columna fecha_modificacion si la tabla ya existía."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(historial_convivencia);")
        columnas = [col["name"] for col in cursor.fetchall()]
        if "fecha_modificacion" not in columnas:
            cursor.execute("ALTER TABLE historial_convivencia ADD COLUMN fecha_modificacion TEXT;")
            conn.commit()

asegurar_columna_modificacion()

def registrar_nota_convivencia(departamento_id: int | None, es_general: bool, tipo_evento: str, titulo: str, descripcion: str, autor: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cursor.execute("""
            INSERT INTO historial_convivencia (departamento_id, es_general, tipo_evento, titulo, descripcion, fecha, autor)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            departamento_id if not es_general else None,
            1 if es_general else 0,
            tipo_evento.strip(),
            titulo.strip(),
            descripcion.strip(),
            fecha_actual,
            autor.strip()
        ))
        conn.commit()
        return True

def actualizar_nota_convivencia(nota_id: int, departamento_id: int | None, es_general: bool, tipo_evento: str, titulo: str, descripcion: str, editor: str):
    """Actualiza la nota y registra la fecha de modificación y el editor sin alterar la fecha original."""
    with get_connection() as conn:
        cursor = conn.cursor()
        fecha_mod = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cursor.execute("""
            UPDATE historial_convivencia 
            SET departamento_id = ?,
                es_general = ?,
                tipo_evento = ?,
                titulo = ?,
                descripcion = ?,
                fecha_modificacion = ?
            WHERE id = ?;
        """, (
            departamento_id if not es_general else None,
            1 if es_general else 0,
            tipo_evento.strip(),
            titulo.strip(),
            descripcion.strip(),
            f"{fecha_mod} (por {editor.strip()})",
            nota_id
        ))
        conn.commit()
        return True

def obtener_historial_convivencia(filtro_depto_id: int | None = None, texto_busqueda: str = ""):
    with get_connection() as conn:
        cursor = conn.cursor()
        param_texto = f"%{texto_busqueda.strip()}%"

        query = """
            SELECT 
                h.id,
                h.departamento_id,
                h.es_general,
                h.tipo_evento,
                h.titulo,
                h.descripcion,
                h.fecha,
                h.fecha_modificacion,
                h.autor,
                d.bloque,
                d.numero_depto
            FROM historial_convivencia h
            LEFT JOIN departamentos d ON h.departamento_id = d.id
            WHERE (h.titulo LIKE ? OR h.descripcion LIKE ? OR h.tipo_evento LIKE ? OR d.bloque LIKE ? OR d.numero_depto LIKE ?)
        """
        params = [param_texto, param_texto, param_texto, param_texto, param_texto]

        if filtro_depto_id is not None:
            query += " AND (h.departamento_id = ? OR h.es_general = 1)"
            params.append(filtro_depto_id)

        query += " ORDER BY h.id DESC;"
        
        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

def eliminar_nota_convivencia(nota_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historial_convivencia WHERE id = ?;", (nota_id,))
        conn.commit()
        return True

def obtener_lista_departamentos_selector():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, bloque, numero_depto FROM departamentos ORDER BY bloque ASC, LENGTH(numero_depto) ASC, numero_depto ASC;")
        return [dict(row) for row in cursor.fetchall()]