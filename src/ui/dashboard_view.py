from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk

from src.services.depto_service import buscar_integrantes_y_deptos, obtener_resumen_metricas
from src.services.excel_service import importar_carpeta_bloque, importar_ficha_excel, exportar_consolidad_excel


class DashboardWindow(ctk.CTk):
    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data

        # Configuración de la ventana principal
        self.title("Sistema de Gestión de Departamentos")
        self.geometry("980x620")
        self.minsize(850, 500)

        # Configurar grid layout (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_content_area()

    def create_sidebar(self):
        """Crea la barra lateral de navegación."""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Título del sistema en el Sidebar
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Mi Edificio", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Información del usuario conectado
        self.user_info_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"👤 {self.user_data['nombre_completo']}\n({self.user_data['rol'].capitalize()})",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.user_info_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Botones de navegación
        self.btn_departamentos = ctk.CTkButton(
            self.sidebar_frame, 
            text="Visualizar Datos", 
            command=self.show_visualizar_datos
        )
        self.btn_departamentos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_residentes = ctk.CTkButton(
            self.sidebar_frame, 
            text="Añadir / Modificar", 
            command=self.show_gestion_datos
        )
        self.btn_residentes.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Botón Cerrar Sesión
        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame, 
            text="Cerrar Sesión", 
            fg_color="#D32F2F", 
            hover_color="#9A0007",
            command=self.logout
        )
        self.btn_logout.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    def create_content_area(self):
        """Crea el contenedor principal donde se mostrarán las distintas vistas."""
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Cargar vista por defecto
        self.show_visualizar_datos()

    def clear_main_frame(self):
        """Limpia todos los elementos dentro del contenedor principal."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_visualizar_datos(self):
        """Vista para consultar departamentos, residentes y filtrar en tiempo real."""
        self.clear_main_frame()

        # Header
        label = ctk.CTkLabel(
            self.main_frame, 
            text="🔍 Consulta de Departamentos y Residentes", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack(pady=(15, 10), padx=20, anchor="w")

        # Frame de Búsqueda y Métricas
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Buscador
        self.entry_search = ctk.CTkEntry(
            top_frame, 
            placeholder_text="🔎 Buscar por RUT, Nombre, Block o Depto...",
            width=360,
            height=35
        )
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", lambda event: self.actualizar_tabla_datos())

        # Métricas resumidas
        total_deptos, total_residentes = obtener_resumen_metricas()
        self.label_stats = ctk.CTkLabel(
            top_frame, 
            text=f"🏢 Deptos: {total_deptos}  |  👥 Residentes: {total_residentes}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4CAF50"
        )
        self.label_stats.pack(side="right", padx=10)

        # Configuración de estilos para Treeview (Tabla) en modo oscuro
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#2A2A2A", 
                        foreground="white", 
                        fieldbackground="#2A2A2A", 
                        rowheight=28,
                        font=('Arial', 10))
        style.configure("Treeview.Heading", 
                        background="#1F1F1F", 
                        foreground="white", 
                        font=('Arial', 10, 'bold'))
        style.map("Treeview", background=[('selected', '#1F6AA5')])

        # Frame contenedor de la Tabla
        table_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Definir Columnas
        columns = ("block", "depto", "parentesco", "nombre", "rut", "asistencia")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("block", text="BLOCK")
        self.tree.heading("depto", text="DEPTO")
        self.tree.heading("parentesco", text="PARENTESCO")
        self.tree.heading("nombre", text="NOMBRE COMPLETO")
        self.tree.heading("rut", text="RUT")
        self.tree.heading("asistencia", text="ASISTENCIA")

        self.tree.column("block", width=110, anchor="center")
        self.tree.column("depto", width=90, anchor="center")
        self.tree.column("parentesco", width=120, anchor="center")
        self.tree.column("nombre", width=220, anchor="w")
        self.tree.column("rut", width=110, anchor="center")
        self.tree.column("asistencia", width=90, anchor="center")

        # Scrollbar vertical para la tabla
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Cargar datos iniciales
        self.actualizar_tabla_datos()

    def actualizar_tabla_datos(self):
        """Limpia y repuebla la tabla según el filtro escrito."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtro = self.entry_search.get() if hasattr(self, 'entry_search') else ""
        registros = buscar_integrantes_y_deptos(filtro)

        for reg in registros:
            self.tree.insert("", "end", values=(
                reg["bloque"],
                reg["numero_depto"],
                reg["parentesco"] or "N/A",
                reg["nombre_completo"].strip() or "SIN NOMBRE",
                reg["rut"] or "N/A",
                reg["asistencia_reuniones"] or "NO"
            ))

    def show_gestion_datos(self):
        """Vista para agregar, editar o importar/exportar información."""
        self.clear_main_frame()
        
        label = ctk.CTkLabel(
            self.main_frame, 
            text="⚙️ Gestión de Datos e Importación Masiva", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack(pady=20, padx=20, anchor="w")

        # Frame de Carga Masiva
        import_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        import_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            import_frame, 
            text="📁 Carga Masiva / Individual desde Excel", 
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
            text="📂 Cargar Carpeta de Block", 
            command=self.accion_importar_carpeta
        )
        btn_folder.pack(side="left", padx=(0, 10))

        btn_file = ctk.CTkButton(
            btn_container, 
            text="📄 Cargar Archivo Excel Individual", 
            fg_color="#1F6AA5",
            command=self.accion_importar_archivo
        )
        btn_file.pack(side="left", padx=(0, 10))

        btn_export = ctk.CTkButton(
            btn_container, 
            text="📊 Exportar BD a Excel Consolidado", 
            fg_color="#2E7D32", 
            hover_color="#1B5E20",
            command=self.accion_exportar
        )
        btn_export.pack(side="left")

    def accion_importar_carpeta(self):
        folder_selected = filedialog.askdirectory(title="Selecciona la carpeta del Block (ej: BLOKC 2613)")
        if folder_selected:
            exitos, errores, total = importar_carpeta_bloque(folder_selected)
            messagebox.showinfo(
                "Importación Finalizada", 
                f"Proceso completado para el Block:\n\n✅ Éxitos: {exitos}\n❌ Errores: {errores}\n📄 Total procesados: {total}"
            )

    def accion_importar_archivo(self):
        file_selected = filedialog.askopenfilename(
            title="Selecciona la ficha Excel del Departamento",
            filetypes=[("Archivos de Excel", "*.xlsx")]
        )
        if file_selected:
            ok, msg = importar_ficha_excel(file_selected)
            if ok:
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)

    def accion_exportar(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")],
            title="Guardar Consolidado como"
        )
        if file_path:
            ok, msg = exportar_consolidad_excel(file_path)
            if ok:
                messagebox.showinfo("Éxito", msg)
            else:
                messagebox.showerror("Error", msg)

    def logout(self):
        """Cierra la ventana actual y vuelve al Login."""
        self.destroy()
        from src.ui.login_view import LoginWindow
        from main import on_login_success
        app = LoginWindow(on_login_success=on_login_success)
        app.mainloop()