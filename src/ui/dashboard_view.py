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
from src.services.excel_service import (
    importar_carpeta_bloque, 
    importar_ficha_excel, 
    exportar_consolidad_excel
)


def centrar_ventana(ventana, ancho, alto):
    """Calcula la posición para centrar cualquier ventana en la pantalla."""
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    
    # Prevenir que la ventana sea más alta que la pantalla del usuario
    if alto > alto_pantalla - 80:
        alto = alto_pantalla - 80

    pos_x = int((ancho_pantalla / 2) - (ancho / 2))
    pos_y = int((alto_pantalla / 2) - (alto / 2)) - 20
    
    # Prevenir coordenadas negativas
    pos_x = max(0, pos_x)
    pos_y = max(0, pos_y)

    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")


class NuevoDeptoModal(ctk.CTkToplevel):
    """Modal centrado para registrar un departamento manualmente con verificación previa."""
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.on_save_callback = on_save_callback

        self.title("Registrar Nuevo Departamento")
        self.resizable(True, True)
        self.minsize(680, 500)
        
        # Centrar ventana con tamaño controlado
        centrar_ventana(self, 720, 620)
        self.grab_set()

        ctk.CTkLabel(
            self, 
            text="Nuevo Departamento Manual", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Scrollable container para todo el contenido
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=(0, 5), fill="both", expand=True)

        # PASO 1: VERIFICACIÓN
        sec1 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        sec1.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(sec1, text="1. Identificación del Departamento", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

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

        btn_check = ctk.CTkButton(
            f_id, text="Validar", width=100, fg_color="#1F6AA5",
            command=self.validar_duplicado
        )
        btn_check.grid(row=0, column=6, padx=5, pady=5)

        self.lbl_status = ctk.CTkLabel(
            sec1, 
            text="Ingresa Block, Letra y N° Depto para validar que no exista previamente.", 
            text_color="#D32F2F", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_status.pack(anchor="w", padx=15, pady=(0, 10))

        # PASO 2: DATOS LEGALES Y PROPIEDAD
        self.sec2 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        self.sec2.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(self.sec2, text="2️⃣ Información Legal / Rol / Avalúo", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

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

        # PASO 3: GRUPO FAMILIAR
        self.sec3 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        self.sec3.pack(fill="x", pady=10, padx=5)

        header_fam = ctk.CTkFrame(self.sec3, fg_color="transparent")
        header_fam.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_fam, text="3️⃣ Residentes y Grupo Familiar", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header_fam, text="Agregar Residente", width=130, height=26, fg_color="#1F6AA5", command=self.agregar_fila_residente).pack(side="right")

        self.integrantes_entries = []
        self.agregar_fila_residente({"parentesco": "PROPIETARIO"})

        # BOTONES DE ACCIÓN FIJOS ABAJO
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=10, padx=20, fill="x", side="bottom")

        ctk.CTkButton(btn_box, text="💾 Crear Departamento", fg_color="#2E7D32", command=self.guardar).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="↩️ Volver", fg_color="#6c757d", hover_color="#5a6268", command=self.destroy).pack(side="left", expand=True, padx=5)

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
            self.lbl_status.configure(text="Por favor completa el Block y la identificación del departamento.", text_color="#FFC107")
            messagebox.showwarning("Atención", "Por favor completa Block y N° Depto.")
            return False

        if verificar_existe_departamento(blk, num):
            self.lbl_status.configure(text=f"ERROR: El departamento '{num}' en el Block '{blk}' ya existe registrado.", text_color="#D32F2F")
            messagebox.showerror("Departamento Duplicado", f"El departamento '{num}' en el Block '{blk}' ya está en la base de datos.")
            return False
        else:
            self.lbl_status.configure(text=f"¡Disponible! Puedes continuar registrando el depto {num} (Block {blk}).", text_color="#4CAF50")
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

        btn_del = ctk.CTkButton(
            f_row, text="Eliminar", width=70, height=28, fg_color="#D32F2F", hover_color="#9A0007",
            command=lambda r=row_dict: self.remover_fila_residente(r)
        )
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


class EditModal(ctk.CTkToplevel):
    """Ventana modal centrada: Editar y Visualizar Registro Completo del Departamento."""
    def __init__(self, parent, depto_id, on_save_callback):
        super().__init__(parent)
        self.depto_id = depto_id
        self.on_save_callback = on_save_callback

        self.depto_data, self.integrantes = obtener_detalle_depto_e_integrantes(depto_id)

        self.title("Editar y Visualizar Registro")
        self.resizable(True, True)
        self.minsize(680, 500)

        # Centrar ventana con dimensiones óptimas
        centrar_ventana(self, 720, 620)
        self.grab_set()

        ctk.CTkLabel(
            self, 
            text=f"📋 Ficha Departamento: Block {self.depto_data['bloque']} - Depto {self.depto_data['numero_depto']}", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Scrollable Frame para el contenido medio
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(padx=20, pady=(0, 5), fill="both", expand=True)

        # SECCIÓN 1: DATOS PROPIEDAD
        sec1 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        sec1.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(sec1, text="🏢 Datos del Departamento y Legal", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))

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

        # SECCIÓN 2: INTEGRANTES / FAMILIARES
        self.sec2 = ctk.CTkFrame(scroll_frame, corner_radius=8)
        self.sec2.pack(fill="x", pady=10, padx=5)

        header_fam = ctk.CTkFrame(self.sec2, fg_color="transparent")
        header_fam.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(header_fam, text="👥 Grupo Familiar y Residentes", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header_fam, text="Agregar Residente", width=130, height=26, fg_color="#1F6AA5", command=self.agregar_fila_residente).pack(side="right")

        self.integrantes_entries = []
        for inte in self.integrantes:
            self.agregar_fila_residente(inte)

        # BOTONES DE ACCIÓN FIJOS ABAJO (Siempre visibles)
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=10, padx=20, fill="x", side="bottom")

        ctk.CTkButton(btn_box, text="💾 Guardar Cambios", fg_color="#2E7D32", command=self.guardar).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="↩️ Volver", fg_color="#6c757d", hover_color="#5a6268", command=self.destroy).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="🗑️ Eliminar Depto", fg_color="#D32F2F", command=self.eliminar).pack(side="left", expand=True, padx=5)

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
            f_row, text="Eliminar", width=70, height=28, fg_color="#D32F2F", hover_color="#9A0007",
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


class DashboardWindow(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data
        self.registros_cache = []
        self.sort_reverse = False

        self.title("Sistema de Gestión de Departamentos")
        self.minsize(900, 550)

        # Centrar ventana principal en la pantalla
        centrar_ventana(self, 980, 620)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Mi Edificio", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.user_info_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"👤 {self.user_data['nombre_completo']}\n({self.user_data['rol'].capitalize()})",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.user_info_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_departamentos = ctk.CTkButton(
            self.sidebar_frame, 
            text="Visualizar / Editar Datos", 
            command=self.show_visualizar_datos
        )
        self.btn_departamentos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_residentes = ctk.CTkButton(
            self.sidebar_frame, 
            text="Añadir / Importar", 
            command=self.show_gestion_datos
        )
        self.btn_residentes.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame, 
            text="Cerrar Sesión", 
            fg_color="#D32F2F", 
            hover_color="#9A0007",
            command=self.logout
        )
        self.btn_logout.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    def create_content_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.show_visualizar_datos()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_visualizar_datos(self):
        self.clear_main_frame()

        label = ctk.CTkLabel(
            self.main_frame, 
            text="🔍 Consulta General de Departamentos", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack(pady=(15, 2), padx=20, anchor="w")

        ctk.CTkLabel(
            self.main_frame,
            text="💡 Tip: Haz clic en el encabezado de cualquier columna para ordenar ascendente/descendente.",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        ).pack(pady=(0, 10), padx=20, anchor="w")

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_search = ctk.CTkEntry(
            top_frame, 
            placeholder_text=" Buscar por Block, Depto, RUT o Titular...",
            width=340,
            height=35
        )
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda event: self.actualizar_tabla_datos())

        total_deptos, total_residentes = obtener_resumen_metricas()
        self.label_stats = ctk.CTkLabel(
            top_frame, 
            text=f"🏢 Deptos: {total_deptos} |  Residentes: {total_residentes}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4CAF50"
        )
        self.label_stats.pack(side="right", padx=10)

        btn_edit = ctk.CTkButton(
            top_frame,
            text=" Ver / Editar Depto",
            width=140,
            fg_color="#1F6AA5",
            command=self.abrir_editor_seleccionado
        )
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
        EditModal(self, depto_id, on_save_callback=self.show_visualizar_datos)

    def show_gestion_datos(self):
        self.clear_main_frame()
        
        label = ctk.CTkLabel(
            self.main_frame, 
            text="Añadir Departamentos e Importación Masiva", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack(pady=15, padx=20, anchor="w")

        manual_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        manual_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            manual_frame, 
            text="Registro Manual de Departamento",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5), padx=15, anchor="w")

        ctk.CTkLabel(
            manual_frame, 
            text="Crea un departamento rellenando sus datos y habitantes directamente en la interfaz.",
            text_color="gray"
        ).pack(pady=(0, 10), padx=15, anchor="w")

        ctk.CTkButton(
            manual_frame,
            text="Registrar Nuevo Departamento Manualmente",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self.abrir_modal_crear_manual
        ).pack(pady=(0, 15), padx=15, anchor="w")

        import_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        import_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            import_frame, 
            text="Carga Masiva / Individual desde Excel", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5), padx=15, anchor="w")

        ctk.CTkLabel(
            import_frame, 
            text="Selecciona una carpeta completa de un Block o sube una ficha individual (.xlsx).",
            text_color="gray"
        ).pack(pady=(0, 10), padx=15, anchor="w")

        btn_container = ctk.CTkFrame(import_frame, fg_color="transparent")
        btn_container.pack(pady=(0, 15), padx=15, fill="x")

        btn_folder = ctk.CTkButton(
            btn_container, 
            text=" Cargar Carpeta de Block", 
            command=self.accion_importar_carpeta
        )
        btn_folder.pack(side="left", padx=(0, 10))

        btn_file = ctk.CTkButton(
            btn_container, 
            text=" Cargar Archivo Excel Individual", 
            fg_color="#1F6AA5",
            command=self.accion_importar_archivo
        )
        btn_file.pack(side="left", padx=(0, 10))

        btn_export = ctk.CTkButton(
            btn_container, 
            text=" Exportar BD a Excel Consolidado", 
            fg_color="#1F6AA5",
            command=self.accion_exportar
        )
        btn_export.pack(side="left")

    def abrir_modal_crear_manual(self):
        NuevoDeptoModal(self, on_save_callback=self.show_visualizar_datos)

    def accion_importar_carpeta(self):
        folder_selected = filedialog.askdirectory(title="Selecciona la carpeta del Block")
        if folder_selected:
            exitos, errores, total = importar_carpeta_bloque(folder_selected)
            messagebox.showinfo("Importación Finalizada", f"Éxitos: {exitos}\nErrores: {errores}\nTotal: {total}")

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