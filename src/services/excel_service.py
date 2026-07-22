import os
import openpyxl
from src.services.db_service import get_connection

def importar_ficha_excel(filepath: str, bloque_nombre: str = ""):
    """
    Lee un archivo Excel con la ficha individual de un departamento y
    guarda en la base de datos el departamento y su grupo familiar.
    """
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active

        # 1. Extraer datos del Departamento (Fila 2 del Excel)
        bloque_val = str(sheet.cell(row=2, column=1).value or bloque_nombre or "SIN BLOQUE").strip()
        depto_val = str(sheet.cell(row=2, column=2).value or "").strip()
        
        # Si el número de depto no está en la celda B2, intentar extraerlo del nombre del archivo
        if not depto_val:
            filename = os.path.basename(filepath)
            depto_val = filename.split()[0]  # Ej: "A-11" de "A-11 ROSA FLORES.xlsx"

        fojas = str(sheet.cell(row=2, column=7).value or "").strip()
        numero_insc = str(sheet.cell(row=2, column=8).value or "").strip()
        ano_insc = sheet.cell(row=2, column=9).value
        try:
            ano_insc = int(ano_insc) if ano_insc else None
        except (ValueError, TypeError):
            ano_insc = None

        rol_sii = str(sheet.cell(row=2, column=10).value or "").strip()
        avaluo = sheet.cell(row=2, column=11).value
        try:
            avaluo = float(avaluo) if avaluo else None
        except (ValueError, TypeError):
            avaluo = None

        # Observaciones (fila 20)
        obs_val = str(sheet.cell(row=20, column=2).value or "").strip()

        # Guardar / Actualizar Departamento en la BD
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO departamentos (bloque, numero_depto, fojas, numero_inscripcion, ano_inscripcion, rol_sii, avaluo_fiscal, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(bloque, numero_depto) DO UPDATE SET
                fojas = excluded.fojas,
                numero_inscripcion = excluded.numero_inscripcion,
                ano_inscripcion = excluded.ano_inscripcion,
                rol_sii = excluded.rol_sii,
                avaluo_fiscal = excluded.avaluo_fiscal,
                observaciones = excluded.observaciones;
        """, (bloque_val, depto_val, fojas, numero_insc, ano_insc, rol_sii, avaluo, obs_val))

        # Obtener ID
        cursor.execute("SELECT id FROM departamentos WHERE bloque = ? AND numero_depto = ?;", (bloque_val, depto_val))
        depto_id = cursor.fetchone()["id"]

        # 2. Extraer Integrantes del Grupo Familiar (Filas 5 a 18)
        cursor.execute("DELETE FROM integrantes WHERE departamento_id = ?;", (depto_id,))

        for row_idx in range(5, 19):
            parentesco = str(sheet.cell(row=row_idx, column=1).value or "").strip()
            nombres = str(sheet.cell(row=row_idx, column=2).value or "").strip()
            ap_paterno = str(sheet.cell(row=row_idx, column=3).value or "").strip()
            ap_materno = str(sheet.cell(row=row_idx, column=4).value or "").strip()
            rut = str(sheet.cell(row=row_idx, column=6).value or "").strip()
            asistencia = str(sheet.cell(row=row_idx, column=13).value or "NO").strip()

            if parentesco or nombres or rut:
                cursor.execute("""
                    INSERT INTO integrantes (departamento_id, parentesco, nombres, apellido_paterno, apellido_materno, rut, asistencia_reuniones)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (depto_id, parentesco or "INTEGRANTE", nombres, ap_paterno, ap_materno, rut, asistencia))

        conn.commit()
        conn.close()
        return True, f"Ficha {depto_val} ({bloque_val}) importada con éxito."

    except Exception as e:
        return False, f"Error al procesar {filepath}: {str(e)}"


def importar_carpeta_bloque(folder_path: str):
    """
    Recorre todos los archivos .xlsx de una carpeta (ej: BLOCK 2613) e importa cada uno.
    """
    bloque_nombre = os.path.basename(folder_path)
    archivos = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and not f.startswith('~$')]
    
    exitos = 0
    errores = 0

    for archivo in archivos:
        full_path = os.path.join(folder_path, archivo)
        ok, msg = importar_ficha_excel(full_path, bloque_nombre)
        if ok:
            exitos += 1
        else:
            errores += 1

    return exitos, errores, len(archivos)


def exportar_consolidad_excel(output_path: str):
    """
    Exporta toda la base de datos a un libro de Excel consolidado usando openpyxl.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                d.bloque,
                d.numero_depto,
                d.rol_sii,
                d.avaluo_fiscal,
                d.fojas,
                d.numero_inscripcion,
                d.ano_inscripcion,
                i.parentesco,
                i.nombres,
                i.apellido_paterno,
                i.apellido_materno,
                i.rut,
                i.asistencia_reuniones,
                d.observaciones
            FROM departamentos d
            LEFT JOIN integrantes i ON d.id = i.departamento_id
            ORDER BY d.bloque ASC, d.numero_depto ASC;
        """)
        rows = cursor.fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Consolidado"

        # Encabezados
        headers = [
            "BLOCK", "DEPTO", "ROL SII", "AVALÚO FISCAL", "FOJAS", 
            "N° INSCRIPCIÓN", "AÑO", "PARENTESCO", "NOMBRES", 
            "AP. PATERNO", "AP. MATERNO", "RUT", "ASISTENCIA", "OBSERVACIONES"
        ]
        ws.append(headers)

        # Agregar cada registro directamente
        for row in rows:
            ws.append(list(row))

        wb.save(output_path)
        return True, f"Reporte exportado exitosamente a:\n{output_path}"

    except Exception as e:
        return False, f"Error al exportar: {str(e)}"