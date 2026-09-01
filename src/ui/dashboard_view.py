from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk

from src.services.depto_service import (
    obtener_deptos_resumen,
    obtener_resumen_metricas,
    obtener_detalle_depto_e_integrantes,
    guardar_cambios_depto_completo,
    eliminar_departamento_completo,
    verificar_existe_departamento,
    crear_departamento_manual
)
from src.services.convivencia_service import (
    registrar_nota_convivencia,
    obtener_historial_convivencia,
    eliminar_nota_convivencia,
    obtener_lista_departamentos_selector
)
from src.services.excel_service import (
    importar_carpeta_bloque, 
    importar_ficha_excel, 
    exportar_consolidad_excel
)

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    if alto > alto_pantalla - 80:
        alto = alto_pantalla - 80
    pos_x = max(0, int((ancho_pantalla / 2) - (ancho / 2)))
    pos_y = max(0, int((alto_pantalla / 2) - (alto / 2)) - 20)
    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")


class ModalNuevaNotaConvivencia(ctk.CTkToplevel):
    """Modal para registrar o editar una nota en la Hoja de Convivencia."""
    def __init__(self, parent, autor_nombre, depto_preseleccionado=None, nota_data=None, on_save_callback=None):
        super().__init__(parent)
        self.autor_nombre = autor_nombre
        self.nota_data = nota_data  # Si viene con datos, es modo EDICIÓN
        self.on_save_callback = on_save_callback
        self.deptos = obtener_lista_departamentos_selector()

        titulo_modal = " Editar Nota de Convivencia" if self.nota_data else " Nueva Nota en Hoja de Convivencia"
        self.title(titulo_modal)
        self.resizable(False, False)
        centrar_ventana(self, 520, 570)
        self.grab_set()

        ctk.CTkLabel(self, text=titulo_modal, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))

        form_f = ctk.CTkFrame(self, fg_color="transparent")
        form_f.pack(padx=25, fill="both", expand=True)

        ctk.CTkLabel(form_f, text="Alcance / Destinatario:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        
        self.depto_map = {" GENERAL (Para todos los departamentos)": None}
        for d in self.deptos:
            label = f"Block {d['bloque']} - Depto {d['numero_depto']}"
            self.depto_map[label] = d["id"]

        opciones_selector = list(self.depto_map.keys())
        self.combo_depto = ctk.CTkOptionMenu(form_f, values=opciones_selector, width=460)
        
        # Establecer selección previa
        target_depto = self.nota_data["departamento_id"] if self.nota_data else depto_preseleccionado
        if target_depto:
            for k, v in self.depto_map.items():
                if v == target_depto:
                    self.combo_depto.set(k)
                    break
        else:
            self.combo_depto.set(opciones_selector[0])
        self.combo_depto.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_f, text="Tipo de Registro:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        opciones_tipo = ["Asistencia a Reunión", "Inasistencia a Reunión", "Incidente / Reclamo", "Felicitación / Aporte", "Aviso / Multa", "Nota de Convivencia General"]
        self.combo_tipo = ctk.CTkOptionMenu(form_f, values=opciones_tipo, width=460)
        if self.nota_data and self.nota_data.get("tipo_evento") in opciones_tipo:
            self.combo_tipo.set(self.nota_data["tipo_evento"])
        self.combo_tipo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_f, text="Asunto / Título:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.entry_titulo = ctk.CTkEntry(form_f, placeholder_text="ej: Asistencia a Asamblea Ordinaria", width=460)
        if self.nota_data:
            self.entry_titulo.insert(0, self.nota_data["titulo"])
        self.entry_titulo.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_f, text="Detalle de la Nota:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.txt_desc = ctk.CTkTextbox(form_f, height=120, width=460)
        if self.nota_data:
            self.txt_desc.insert("1.0", self.nota_data["descripcion"])
        self.txt_desc.pack(fill="x", pady=(0, 15))

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=(0, 15), padx=25, fill="x")

        btn_txt = " Guardar Modificación" if self.nota_data else " Guardar Nota"
        ctk.CTkButton(btn_box, text=btn_txt, fg_color="#2E7D32", command=self.guardar).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text=" Cancelar", fg_color="#6c757d", hover_color="#5a6268", command=self.destroy).pack(side="left", expand=True, padx=5)

    def guardar(self):
        sel_texto = self.combo_depto.get()
        depto_id = self.depto_map.get(sel_texto)
        es_general = (depto_id is None)
        tipo = self.combo_tipo.get()
        titulo = self.entry_titulo.get().strip()
        desc = self.txt_desc.get("1.0", "end").strip()

        if not titulo or not desc:
            messagebox.showwarning("Campos Requeridos", "Por favor completa el Asunto y el Detalle de la nota.")
            return

        from src.services.convivencia_service import actualizar_nota_convivencia
        if self.nota_data:
            actualizar_nota_convivencia(self.nota_data["id"], depto_id, es_general, tipo, titulo, desc, self.autor_nombre)
            messagebox.showinfo("Éxito", "Nota modificada correctamente.")
        else:
            registrar_nota_convivencia(depto_id, es_general, tipo, titulo, desc, self.autor_nombre)
            messagebox.showinfo("Éxito", "Nota registrada exitosamente en la Hoja de Convivencia.")

        if self.on_save_callback:
            self.on_save_callback()
        self.destroy()

class EditModal(ctk.CTkToplevel):
    """Ventana modal: Ficha del Departamento y su Hoja de Vida."""
    def __init__(self, parent, depto_id, autor_nombre, on_save_callback):
        super().__init__(parent)
        self.depto_id = depto_id
        self.autor_nombre = autor_nombre
        self.on_save_callback = on_save_callback

        self.depto_data, self.integrantes = obtener_detalle_depto_e_integrantes(depto_id)

        self.title("Editar y Visualizar Registro")
        self.resizable(True, True)
        self.minsize(700, 520)
        centrar_ventana(self, 760, 660)
        self.grab_set()

        ctk.CTkLabel(
            self, 
            text=f" Ficha Departamento: Block {self.depto_data['bloque']} - Depto {self.depto_data['numero_depto']}", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=(0, 5), fill="both", expand=True)

        # SECCIÓN 1: DATOS PROPIEDAD
        sec1 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        sec1.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(sec1, text=" Datos del Departamento y Legal", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        grid_f = ctk.CTkFrame(sec1, fg_color="transparent")
        grid_f.pack(fill="x", padx=10, pady=5)

        self.fields_depto = {}
        labels = [
            ("Block:", "bloque", 0, 0),
            ("Depto:", "numero_depto", 0, 2),
            ("Rol SII:", "rol_sii", 1, 0),
            ("Avalúo Fiscal:", "avaluo_fiscal", 1, 2),
            ("Fojas:", "fojas", 2, 0),
            ("N° Inscripción:", "numero_inscripcion", 2, 2),
            ("Año Inscripción:", "ano_inscripcion", 3, 0),
        ]

        for lbl, key, r, c in labels:
            ctk.CTkLabel(grid_f, text=lbl, anchor="w").grid(row=r, column=c, sticky="w", padx=5, pady=3)
            ent = ctk.CTkEntry(grid_f, width=150)
            ent.insert(0, str(self.depto_data[key] or ""))
            ent.grid(row=r, column=c+1, sticky="w", padx=5, pady=3)
            self.fields_depto[key] = ent

        # SECCIÓN 2: INTEGRANTES
        self.sec2 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        self.sec2.pack(fill="x", pady=10, padx=5)

        header_fam = ctk.CTkFrame(self.sec2, fg_color="transparent")
        header_fam.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_fam, text=" Grupo Familiar y Residentes", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header_fam, text=" Agregar Residente", width=130, height=26, fg_color="#1F6AA5", command=self.agregar_fila_residente).pack(side="right")

        self.integrantes_entries = []
        for inte in self.integrantes:
            self.agregar_fila_residente(inte)

        # SECCIÓN 3: BITÁCORA / HOJA DE CONVIVENCIA DEL DEPTO
        sec3 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        sec3.pack(fill="x", pady=10, padx=5)

        header_bitacora = ctk.CTkFrame(sec3, fg_color="transparent")
        header_bitacora.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_bitacora, text=" Historial y Hoja de Convivencia de este Depto", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(
            header_bitacora, 
            text=" Añadir Nota a este Depto", 
            width=160, 
            height=26, 
            fg_color="#E65100", 
            hover_color="#BF360C",
            command=self.abrir_modal_nota_directa
        ).pack(side="right")

        self.f_historial = ctk.CTkFrame(sec3, fg_color="transparent")
        self.f_historial.pack(fill="x", padx=10, pady=(5, 10))
        self.cargar_historial_depto()

        # BOTONES FIJOS
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=10, padx=20, fill="x", side="bottom")

        ctk.CTkButton(btn_box, text=" Guardar Cambios", fg_color="#2E7D32", command=self.guardar).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text=" Volver", fg_color="#6c757d", hover_color="#5a6268", command=self.destroy).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text=" Eliminar Depto", fg_color="#D32F2F", command=self.eliminar).pack(side="left", expand=True, padx=5)

    def cargar_historial_depto(self):
        for w in self.f_historial.winfo_children():
            w.destroy()

        notas = obtener_historial_convivencia(filtro_depto_id=self.depto_id)
        if not notas:
            ctk.CTkLabel(self.f_historial, text="No hay registros de convivencia ni asistencias previas.", text_color="gray").pack(anchor="w", pady=5)
            return

        for n in notas:
            item_f = ctk.CTkFrame(self.f_historial, corner_radius=6)
            item_f.pack(fill="x", pady=4)

            top_row = ctk.CTkFrame(item_f, fg_color="transparent")
            top_row.pack(fill="x", padx=8, pady=(4, 1))

            alcance_txt = " GENERAL" if n["es_general"] else f" Depto {n['numero_depto']}"
            top_line = f"[{n['fecha']}]  •  {alcance_txt}  •  {n['tipo_evento'].upper()}: {n['titulo']} (Por: {n['autor']})"
            
            ctk.CTkLabel(
                top_row, 
                text=top_line, 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color="#1F6AA5"
            ).pack(side="left", fill="x", expand=True, anchor="w")

            # Botón Editar Nota
            btn_edit_nota = ctk.CTkButton(
                top_row,
                text=" Editar",
                width=28,
                height=24,
                fg_color="#1F6AA5",
                command=lambda nota=n: ModalNuevaNotaConvivencia(self, self.autor_nombre, nota_data=nota, on_save_callback=self.cargar_historial_depto)
            )
            btn_edit_nota.pack(side="right", padx=2)

            # Botón Eliminar Nota
            btn_borrar_nota = ctk.CTkButton(
                top_row,
                text="Eliminar",
                width=28,
                height=24,
                fg_color="#D32F2F",
                hover_color="#9A0007",
                command=lambda nota_id=n["id"]: self.confirmar_eliminar_nota(nota_id)
            )
            btn_borrar_nota.pack(side="right", padx=2)

            ctk.CTkLabel(
                item_f, 
                text=n["descripcion"], 
                font=ctk.CTkFont(size=11), 
                wraplength=620, 
                justify="left"
            ).pack(anchor="w", padx=8, pady=(0, 2))

            # Si fue editada, muestra la fecha de modificación abajo
            if n.get("fecha_modificacion"):
                ctk.CTkLabel(
                    item_f,
                    text=f"✏️ Modificado: {n['fecha_modificacion']}",
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color="#FFA726"
                ).pack(anchor="w", padx=8, pady=(0, 4))

    def confirmar_eliminar_nota(self, nota_id):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta nota de la hoja de convivencia?"):
            eliminar_nota_convivencia(nota_id)
            messagebox.showinfo("Éxito", "Nota eliminada correctamente.")
            self.cargar_historial_depto()

    def abrir_modal_nota_directa(self):
        ModalNuevaNotaConvivencia(self, self.autor_nombre, depto_preseleccionado=self.depto_id, on_save_callback=self.cargar_historial_depto)

    def agregar_fila_residente(self, data=None):
        if data is None:
            data = {"parentesco": "", "nombres": "", "apellido_paterno": "", "apellido_materno": "", "rut": "", "asistencia_reuniones": "NO"}

        f_row = ctk.CTkFrame(self.sec2, fg_color="transparent")
        f_row.pack(fill="x", padx=10, pady=3)

        e_par = ctk.CTkEntry(f_row, width=100, placeholder_text="Parentesco")
        e_par.insert(0, data.get("parentesco") or "")
        e_par.pack(side="left", padx=2)

        e_nom = ctk.CTkEntry(f_row, width=120, placeholder_text="Nombres")
        e_nom.insert(0, data.get("nombres") or "")
        e_nom.pack(side="left", padx=2)

        e_pat = ctk.CTkEntry(f_row, width=110, placeholder_text="Ap. Paterno")
        e_pat.insert(0, data.get("apellido_paterno") or "")
        e_pat.pack(side="left", padx=2)

        e_mat = ctk.CTkEntry(f_row, width=110, placeholder_text="Ap. Materno")
        e_mat.insert(0, data.get("apellido_materno") or "")
        e_mat.pack(side="left", padx=2)

        e_rut = ctk.CTkEntry(f_row, width=95, placeholder_text="RUT")
        e_rut.insert(0, data.get("rut") or "")
        e_rut.pack(side="left", padx=2)

        row_dict = {
            "frame": f_row, "parentesco": e_par, "nombres": e_nom,
            "apellido_paterno": e_pat, "apellido_materno": e_mat, "rut": e_rut,
            "asistencia_reuniones": data.get("asistencia_reuniones", "NO")
        }

        btn_del = ctk.CTkButton(
            f_row, text="Remover", width=28, height=28, fg_color="#D32F2F", hover_color="#9A0007",
            command=lambda r=row_dict: self.remover_fila_residente(r)
        )
        btn_del.pack(side="left", padx=3)

        self.integrantes_entries.append(row_dict)

    def remover_fila_residente(self, row_dict):
        row_dict["frame"].destroy()
        if row_dict in self.integrantes_entries:
            self.integrantes_entries.remove(row_dict)

    def guardar(self):
        new_depto = {k: v.get().strip() for k, v in self.fields_depto.items()}
        new_depto["observaciones"] = self.depto_data.get("observaciones", "")

        new_integrantes = []
        for row in self.integrantes_entries:
            par = row["parentesco"].get().strip()
            nom = row["nombres"].get().strip()
            pat = row["apellido_paterno"].get().strip()
            mat = row["apellido_materno"].get().strip()
            rut = row["rut"].get().strip()

            if par or nom or rut or pat:
                new_integrantes.append({
                    "parentesco": par, "nombres": nom, "apellido_paterno": pat,
                    "apellido_materno": mat, "rut": rut, "asistencia_reuniones": row["asistencia_reuniones"]
                })

        guardar_cambios_depto_completo(self.depto_id, new_depto, new_integrantes)
        messagebox.showinfo("Éxito", "Información del departamento actualizada.")
        self.on_save_callback()
        self.destroy()

    def eliminar(self):
        if messagebox.askyesno("Confirmar", "¿Eliminar este departamento y todos sus residentes registrados?"):
            eliminar_departamento_completo(self.depto_id)
            messagebox.showinfo("Éxito", "Departamento eliminado.")
            self.on_save_callback()
            self.destroy()


class NuevoDeptoModal(ctk.CTkToplevel):
    """Modal centrado para registrar un departamento manualmente."""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.on_save_callback = on_save_callback

        self.title(" Registrar Nuevo Departamento")
        self.resizable(True, True)
        self.minsize(680, 500)
        centrar_ventana(self, 720, 620)
        self.grab_set()

        ctk.CTkLabel(self, text=" Nuevo Departamento Manual", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=(0, 5), fill="both", expand=True)

        sec1 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        sec1.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(sec1, text=" Identificación del Departamento", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        f_id = ctk.CTkFrame(sec1, fg_color="transparent")
        f_id.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(f_id, text="Block (N°):").grid(row=0, column=0, padx=(0, 2), pady=5, sticky="w")
        self.entry_block = ctk.CTkEntry(f_id, width=90, placeholder_text="ej: 2613")
        self.entry_block.grid(row=0, column=1, padx=(0, 10), pady=5)
        self.entry_block.bind("<KeyRelease>", lambda e: self.validar_input_numerico(self.entry_block, 10))

        ctk.CTkLabel(f_id, text="Letra:").grid(row=0, column=2, padx=(0, 2), pady=5, sticky="w")
        self.entry_letra = ctk.CTkEntry(f_id, width=70, placeholder_text="ej: A")
        self.entry_letra.grid(row=0, column=3, padx=(0, 10), pady=5)
        self.entry_letra.bind("<KeyRelease>", lambda e: self.validar_input_texto(self.entry_letra, 10))

        ctk.CTkLabel(f_id, text="N° Depto:").grid(row=0, column=4, padx=(0, 2), pady=5, sticky="w")
        self.entry_depto_num = ctk.CTkEntry(f_id, width=90, placeholder_text="ej: 11")
        self.entry_depto_num.grid(row=0, column=5, padx=(0, 10), pady=5)
        self.entry_depto_num.bind("<KeyRelease>", lambda e: self.validar_input_numerico(self.entry_depto_num, 10))

        btn_check = ctk.CTkButton(f_id, text=" Validar", width=100, fg_color="#1F6AA5", command=self.validar_duplicado)
        btn_check.grid(row=0, column=6, padx=5, pady=5)

        self.lbl_status = ctk.CTkLabel(sec1, text=" Ingresa Block, Letra y N° Depto para validar que no exista previamente.", text_color="#D32F2F", font=ctk.CTkFont(size=12, weight="bold"))
        self.lbl_status.pack(anchor="w", padx=15, pady=(0, 10))

        self.sec2 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        self.sec2.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(self.sec2, text=" Información Legal / Rol / Avalúo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

        grid_f = ctk.CTkFrame(self.sec2, fg_color="transparent")
        grid_f.pack(fill="x", padx=10, pady=5)

        self.fields_depto = {}
        labels = [
            ("Rol SII:", "rol_sii", 0, 0),
            ("Avalúo Fiscal:", "avaluo_fiscal", 0, 2),
            ("Fojas:", "fojas", 1, 0),
            ("N° Inscripción:", "numero_inscripcion", 1, 2),
            ("Año Inscripción:", "ano_inscripcion", 2, 0),
        ]

        for lbl, key, r, c in labels:
            ctk.CTkLabel(grid_f, text=lbl, anchor="w").grid(row=r, column=c, sticky="w", padx=5, pady=3)
            ent = ctk.CTkEntry(grid_f, width=150)
            ent.grid(row=r, column=c+1, sticky="w", padx=5, pady=3)
            self.fields_depto[key] = ent

        self.sec3 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        self.sec3.pack(fill="x", pady=10, padx=5)

        header_fam = ctk.CTkFrame(self.sec3, fg_color="transparent")
        header_fam.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_fam, text=" Residentes y Grupo Familiar", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header_fam, text=" Agregar Residente", width=130, height=26, fg_color="#1F6AA5", command=self.agregar_fila_residente).pack(side="right")

        self.integrantes_entries = []
        self.agregar_fila_residente({"parentesco": "PROPIETARIO"})

        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=10, padx=20, fill="x", side="bottom")

        ctk.CTkButton(btn_box, text=" Crear Departamento", fg_color="#2E7D32", command=self.guardar).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="↩ Volver", fg_color="#6c757d", hover_color="#5a6268", command=self.destroy).pack(side="left", expand=True, padx=5)

    def validar_input_numerico(self, entry_widget, max_len=10):
        val = entry_widget.get()
        filtrado = ''.join(c for c in val if c.isdigit())[:max_len]
        if val != filtrado:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, filtrado)

    def validar_input_texto(self, entry_widget, max_len=10):
        val = entry_widget.get()
        if len(val) > max_len:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, val[:max_len])

    def construir_nombres_bloque_depto(self):
        blk_num = self.entry_block.get().strip()
        letra = self.entry_letra.get().strip().upper()
        num_depto = self.entry_depto_num.get().strip()
        bloque_completo = blk_num
        depto_completo = f"{letra}-{num_depto}" if letra and num_depto else (letra or num_depto)
        return bloque_completo, depto_completo

    def validar_duplicado(self):
        blk, num = self.construir_nombres_bloque_depto()
        if not self.entry_block.get().strip() or not (self.entry_letra.get().strip() or self.entry_depto_num.get().strip()):
            self.lbl_status.configure(text=" Por favor completa el Block y la identificación del departamento.", text_color="#D32F2F")
            messagebox.showwarning("Atención", "Por favor completa Block y N° Depto.")
            return False

        if verificar_existe_departamento(blk, num):
            self.lbl_status.configure(text=f" ERROR: El departamento '{num}' en el Block '{blk}' ya existe registrado.", text_color="#D32F2F")
            messagebox.showerror("Departamento Duplicado", f"El departamento '{num}' en el Block '{blk}' ya está en la base de datos.")
            return False
        else:
            self.lbl_status.configure(text=f" ¡Disponible! Puedes continuar registrando el depto {num} (Block {blk}).", text_color="#2E7D32")
            return True

    def agregar_fila_residente(self, data=None):
        if data is None:
            data = {"parentesco": "", "nombres": "", "apellido_paterno": "", "apellido_materno": "", "rut": ""}

        f_row = ctk.CTkFrame(self.sec3, fg_color="transparent")
        f_row.pack(fill="x", padx=10, pady=3)

        e_par = ctk.CTkEntry(f_row, width=100, placeholder_text="Parentesco")
        e_par.insert(0, data.get("parentesco") or "")
        e_par.pack(side="left", padx=2)

        e_nom = ctk.CTkEntry(f_row, width=120, placeholder_text="Nombres")
        e_nom.insert(0, data.get("nombres") or "")
        e_nom.pack(side="left", padx=2)

        e_pat = ctk.CTkEntry(f_row, width=110, placeholder_text="Ap. Paterno")
        e_pat.insert(0, data.get("apellido_paterno") or "")
        e_pat.pack(side="left", padx=2)

        e_mat = ctk.CTkEntry(f_row, width=110, placeholder_text="Ap. Materno")
        e_mat.insert(0, data.get("apellido_materno") or "")
        e_mat.pack(side="left", padx=2)

        e_rut = ctk.CTkEntry(f_row, width=95, placeholder_text="RUT")
        e_rut.insert(0, data.get("rut") or "")
        e_rut.pack(side="left", padx=2)

        row_dict = {
            "frame": f_row, "parentesco": e_par, "nombres": e_nom,
            "apellido_paterno": e_pat, "apellido_materno": e_mat, "rut": e_rut
        }

        btn_del = ctk.CTkButton(f_row, text="❌", width=28, height=28, fg_color="#D32F2F", hover_color="#9A0007", command=lambda r=row_dict: self.remover_fila_residente(r))
        btn_del.pack(side="left", padx=3)
        self.integrantes_entries.append(row_dict)

    def remover_fila_residente(self, row_dict):
        row_dict["frame"].destroy()
        if row_dict in self.integrantes_entries:
            self.integrantes_entries.remove(row_dict)

    def guardar(self):
        if not self.validar_duplicado():
            return

        blk, num = self.construir_nombres_bloque_depto()
        new_depto = {k: v.get().strip() for k, v in self.fields_depto.items()}
        new_depto["bloque"] = blk
        new_depto["numero_depto"] = num

        new_integrantes = []
        for row in self.integrantes_entries:
            par = row["parentesco"].get().strip()
            nom = row["nombres"].get().strip()
            pat = row["apellido_paterno"].get().strip()
            mat = row["apellido_materno"].get().strip()
            rut = row["rut"].get().strip()

            if par or nom or rut or pat:
                new_integrantes.append({
                    "parentesco": par, "nombres": nom, "apellido_paterno": pat,
                    "apellido_materno": mat, "rut": rut, "asistencia_reuniones": "NO"
                })

        crear_departamento_manual(new_depto, new_integrantes)
        messagebox.showinfo("Éxito", f"Departamento {num} (Block {blk}) creado correctamente.")
        self.on_save_callback()
        self.destroy()


class DashboardWindow(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data
        self.registros_cache = []
        self.sort_reverse = False

        self.title("Sistema de Gestión de Departamentos")
        self.minsize(920, 560)
        centrar_ventana(self, 980, 620)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Mi Edificio", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.user_info_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f" {self.user_data['nombre_completo']}\n({self.user_data['rol'].capitalize()})",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.user_info_label.grid(row=1, column=0, padx=20, pady=(0, 15))

        self.btn_departamentos = ctk.CTkButton(self.sidebar_frame, text="Visualizar / Editar", command=self.show_visualizar_datos)
        self.btn_departamentos.grid(row=2, column=0, padx=20, pady=6, sticky="ew")

        self.btn_residentes = ctk.CTkButton(self.sidebar_frame, text="Añadir / Importar", command=self.show_gestion_datos)
        self.btn_residentes.grid(row=3, column=0, padx=20, pady=6, sticky="ew")

        # NUEVO BOTÓN: HOJA DE CONVIVENCIA
        self.btn_convivencia = ctk.CTkButton(
            self.sidebar_frame, 
            text=" Hoja de Convivencia", 
            fg_color="#E65100", 
            hover_color="#BF360C",
            command=self.show_hoja_convivencia
        )
        self.btn_convivencia.grid(row=4, column=0, padx=20, pady=6, sticky="ew")

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="Cerrar Sesión", fg_color="#D32F2F", hover_color="#9A0007", command=self.logout)
        self.btn_logout.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

    def create_content_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.show_visualizar_datos()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_visualizar_datos(self):
        self.clear_main_frame()

        label = ctk.CTkLabel(self.main_frame, text=" Consulta General de Departamentos", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=(15, 2), padx=20, anchor="w")

        ctk.CTkLabel(self.main_frame, text=" Tip: Haz doble clic en una fila para ver su ficha completa y su hoja de convivencia.", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=(0, 10), padx=20, anchor="w")

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_search = ctk.CTkEntry(top_frame, placeholder_text=" Buscar por Block, Depto, RUT o Titular...", width=300, height=35)
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda event: self.actualizar_tabla_datos())

        total_deptos, total_residentes = obtener_resumen_metricas()
        self.label_stats = ctk.CTkLabel(top_frame, text=f" Deptos: {total_deptos} |  Residentes: {total_residentes}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#4CAF50")
        self.label_stats.pack(side="right", padx=10)

        btn_edit = ctk.CTkButton(top_frame, text=" Ver / Editar Depto", fg_color="#1F6AA5", command=self.abrir_editor_seleccionado)
        btn_edit.pack(side="right", padx=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2A2A2A", foreground="white", fieldbackground="#2A2A2A", rowheight=28, font=('Arial', 10))
        style.configure("Treeview.Heading", background="#1F1F1F", foreground="white", font=('Arial', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#1F6AA5')])

        table_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        columns = ("block", "depto", "habitante", "nombre", "rut")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            col_name = col.upper()
            if col == "nombre":
                col_name = "NOMBRE TITULAR / PROPIETARIO"
            elif col == "rut":
                col_name = "RUT TITULAR"
            self.tree.heading(col, text=col_name, command=lambda c=col: self.ordenar_columna(c))

        self.tree.column("block", width=120, anchor="center")
        self.tree.column("depto", width=100, anchor="center")
        self.tree.column("habitante", width=130, anchor="center")
        self.tree.column("nombre", width=260, anchor="w")
        self.tree.column("rut", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.tree.bind("<Double-1>", lambda event: self.abrir_editor_seleccionado())
        self.actualizar_tabla_datos()

    def ordenar_columna(self, col):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=self.sort_reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.sort_reverse = not self.sort_reverse

    def actualizar_tabla_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtro = self.entry_search.get() if hasattr(self, 'entry_search') else ""
        self.registros_cache = obtener_deptos_resumen(filtro)

        for idx, reg in enumerate(self.registros_cache):
            self.tree.insert("", "end", iid=str(idx), values=(
                reg["bloque"],
                reg["numero_depto"],
                reg["habitante_tipo"],
                reg["nombre_titular"].strip() or "SIN TITULAR REGISTRADO",
                reg["rut_titular"] or "N/A"
            ))

    def abrir_editor_seleccionado(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Por favor selecciona un departamento de la lista.")
            return

        idx = int(selected_item[0])
        depto_id = self.registros_cache[idx]["depto_id"]
        EditModal(self, depto_id, self.user_data["nombre_completo"], on_save_callback=self.show_visualizar_datos)

    def show_gestion_datos(self):
        self.clear_main_frame()
        
        label = ctk.CTkLabel(self.main_frame, text=" Añadir Departamentos e Importación Masiva", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=15, padx=20, anchor="w")

        manual_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        manual_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(manual_frame, text=" Registro Manual de Departamento", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5), padx=15, anchor="w")
        ctk.CTkLabel(manual_frame, text="Crea un departamento rellenando sus datos y habitantes directamente en la interfaz.", text_color="gray").pack(pady=(0, 10), padx=15, anchor="w")

        ctk.CTkButton(manual_frame, text="Registrar Nuevo Departamento Manualmente", fg_color="#2E7D32", hover_color="#1B5E20", command=lambda: NuevoDeptoModal(self, on_save_callback=self.show_visualizar_datos)).pack(pady=(0, 15), padx=15, anchor="w")

        import_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        import_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(import_frame, text="Carga Masiva / Individual desde Excel", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5), padx=15, anchor="w")
        ctk.CTkLabel(import_frame, text="Selecciona una carpeta completa de un Block o sube una ficha individual (.xlsx).", text_color="gray").pack(pady=(0, 10), padx=15, anchor="w")

        btn_container = ctk.CTkFrame(import_frame, fg_color="transparent")
        btn_container.pack(pady=(0, 15), padx=15, fill="x")

        ctk.CTkButton(btn_container, text=" Cargar Carpeta de Block", command=self.accion_importar_carpeta).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_container, text=" Cargar Archivo Excel Individual", fg_color="#1F6AA5", command=self.accion_importar_archivo).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_container, text=" Exportar BD a Excel Consolidado", fg_color="#1F6AA5", command=self.accion_exportar).pack(side="left")

    def show_hoja_convivencia(self):
        """Vista principal para la Hoja de Convivencia y Bitácora del Edificio."""
        self.clear_main_frame()

        label = ctk.CTkLabel(self.main_frame, text=" Hoja de Convivencia y Bitácora General", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=(15, 2), padx=20, anchor="w")

        ctk.CTkLabel(
            self.main_frame, 
            text="Control de asistencias a reuniones, reclamos, acuerdos e incidentes registrados por administradores.",
            text_color="gray", 
            font=ctk.CTkFont(size=11)
        ).pack(pady=(0, 10), padx=20, anchor="w")

        top_f = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_f.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_search_conv = ctk.CTkEntry(top_f, placeholder_text=" Buscar en notas por asunto, texto, block o tipo...", width=320, height=35)
        self.entry_search_conv.pack(side="left", padx=(0, 10))
        self.entry_search_conv.bind("<KeyRelease>", lambda e: self.actualizar_tabla_convivencia())

        ctk.CTkButton(
            top_f, 
            text=" Redactar Nueva Nota", 
            fg_color="#E65100", 
            hover_color="#BF360C",
            command=lambda: ModalNuevaNotaConvivencia(self, self.user_data["nombre_completo"], on_save_callback=self.actualizar_tabla_convivencia)
        ).pack(side="right", padx=10)

        # Contenedor lista de notas
        self.scroll_conv = ctk.CTkScrollableFrame(self.main_frame, corner_radius=10)
        self.scroll_conv.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.actualizar_tabla_convivencia()

    def actualizar_tabla_convivencia(self):
        for w in self.scroll_conv.winfo_children():
            w.destroy()

        filtro = self.entry_search_conv.get() if hasattr(self, 'entry_search_conv') else ""
        notas = obtener_historial_convivencia(texto_busqueda=filtro)

        if not notas:
            ctk.CTkLabel(self.scroll_conv, text="No se encontraron registros en la hoja de convivencia.", text_color="gray", font=ctk.CTkFont(size=13)).pack(pady=30)
            return

        for n in notas:
            card = ctk.CTkFrame(self.scroll_conv, corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            alcance_txt = " GENERAL" if n["es_general"] else f" Block {n['bloque']} - Depto {n['numero_depto']}"
            
            top_card = ctk.CTkFrame(card, fg_color="transparent")
            top_card.pack(fill="x", padx=12, pady=(8, 2))

            ctk.CTkLabel(
                top_card, 
                text=f"{alcance_txt}  |  {n['tipo_evento'].upper()}: {n['titulo']}", 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#1F6AA5"
            ).pack(side="left")

            # Botones de Acción en Vista General
            btn_del = ctk.CTkButton(
                top_card,
                text="Eliminar",
                width=28,
                height=24,
                fg_color="#D32F2F",
                hover_color="#9A0007",
                command=lambda nota_id=n["id"]: self.accion_eliminar_nota_general(nota_id)
            )
            btn_del.pack(side="right", padx=(4, 0))

            btn_edit = ctk.CTkButton(
                top_card,
                text="Editar",
                width=28,
                height=24,
                fg_color="#1F6AA5",
                command=lambda nota=n: ModalNuevaNotaConvivencia(self, self.user_data["nombre_completo"], nota_data=nota, on_save_callback=self.actualizar_tabla_convivencia)
            )
            btn_edit.pack(side="right", padx=(8, 0))

            ctk.CTkLabel(
                top_card, 
                text=f" {n['fecha']}  (Por: {n['autor']})", 
                font=ctk.CTkFont(size=11), 
                text_color="gray"
            ).pack(side="right")

            ctk.CTkLabel(
                card, 
                text=n["descripcion"], 
                font=ctk.CTkFont(size=12), 
                wraplength=660, 
                justify="left"
            ).pack(anchor="w", padx=12, pady=(2, 4))

            if n.get("fecha_modificacion"):
                ctk.CTkLabel(
                    card,
                    text=f" Modificado: {n['fecha_modificacion']}",
                    font=ctk.CTkFont(size=10, slant="italic"),
                    text_color="#FFA726"
                ).pack(anchor="w", padx=12, pady=(0, 6))

    def accion_eliminar_nota_general(self, nota_id):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta nota?"):
            eliminar_nota_convivencia(nota_id)
            messagebox.showinfo("Éxito", "Nota eliminada.")
            self.actualizar_tabla_convivencia()

    def accion_importar_carpeta(self):
        folder_selected = filedialog.askdirectory(title="Selecciona la carpeta del Block")
        if folder_selected:
            exitos, errores, total = importar_carpeta_bloque(folder_selected)
            messagebox.showinfo("Importación Finalizada", f" Éxitos: {exitos}\n❌ Errores: {errores}\n Total: {total}")

    def accion_importar_archivo(self):
        file_selected = filedialog.askopenfilename(title="Selecciona la ficha Excel", filetypes=[("Archivos de Excel", "*.xlsx")])
        if file_selected:
            ok, msg = importar_ficha_excel(file_selected)
            messagebox.showinfo("Éxito" if ok else "Error", msg)

    def accion_exportar(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")], title="Guardar Consolidado como")
        if file_path:
            ok, msg = exportar_consolidad_excel(file_path)
            messagebox.showinfo("Éxito" if ok else "Error", msg)

    def logout(self):
        self.destroy()
        from src.ui.login_view import LoginWindow
        from main import on_login_success
        app = LoginWindow(on_login_success=on_login_success)
        app.mainloop()