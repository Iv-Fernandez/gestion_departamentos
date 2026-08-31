import re
from src.services.db_service import get_connection

def limpiar_numeracion_bloques():
    """
    Extrae la numeración de la columna 'bloque'. 
    Si al renombrar se genera un duplicado, fusiona los residentes y elimina la fila sobrante.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, bloque, numero_depto FROM departamentos ORDER BY id ASC;")
    rows = cursor.fetchall()
    
    modificados = 0
    fusionados = 0

    for row in rows:
        depto_id = row["id"]
        bloque_original = str(row["bloque"] or "")
        numero_depto = str(row["numero_depto"] or "")
        
        # Extraer solo dígitos del bloque
        numeros = re.findall(r'\d+', bloque_original)
        bloque_limpio = numeros[0] if numeros else bloque_original.strip()
        
        if bloque_limpio != bloque_original:
            # Comprobar si ya existe otro departamento con la numeración limpia
            cursor.execute("""
                SELECT id FROM departamentos 
                WHERE bloque = ? AND numero_depto = ? AND id != ?;
            """, (bloque_limpio, numero_depto, depto_id))
            existente = cursor.fetchone()

            if existente:
                depto_destino_id = existente["id"]
                # Reasignar todos los integrantes al departamento existente
                cursor.execute("""
                    UPDATE integrantes SET departamento_id = ? WHERE departamento_id = ?;
                """, (depto_destino_id, depto_id))
                # Eliminar el departamento duplicado con nombre viejo
                cursor.execute("DELETE FROM departamentos WHERE id = ?;", (depto_id,))
                fusionados += 1
            else:
                # Actualizar el bloque al número limpio
                cursor.execute("UPDATE departamentos SET bloque = ? WHERE id = ?;", (bloque_limpio, depto_id))
                modificados += 1

    conn.commit()
    conn.close()
    print("Proceso finalizado:")
    print(f"   • Deptos actualizados a número limpio: {modificados}")
    print(f"   • Deptos duplicados fusionados: {fusionados}")

if __name__ == "__main__":
    limpiar_numeracion_bloques()