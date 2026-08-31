import customtkinter as ctk
from src.services.auth_service import autenticar_usuario

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    pos_x = int((ancho_pantalla / 2) - (ancho / 2))
    pos_y = int((alto_pantalla / 2) - (alto / 2)) - 20
    ventana.geometry(f"{ancho}x{alto}+{max(0, pos_x)}+{max(0, pos_y)}")

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()

        self.on_login_success = on_login_success

        self.title("Sistema de Gestión de Departamentos - Acceso")
        self.resizable(False, False)
        
        # Centrar Login
        centrar_ventana(self, 400, 480)

        # Contenedor Principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=30, padx=30, fill="both", expand=True)

        # Título / Encabezado
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Iniciar Sesión", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(pady=(25, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.main_frame, 
            text="Ingresa tus credenciales para continuar", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Campo Usuario
        self.username_entry = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Usuario (ej: admin)", 
            width=280,
            height=40
        )
        self.username_entry.pack(pady=10)

        # Campo Contraseña
        self.password_entry = ctk.CTkEntry(
            self.main_frame, 
            placeholder_text="Contraseña", 
            show="*", 
            width=280,
            height=40
        )
        self.password_entry.pack(pady=10)

        # Permite presionar Enter para iniciar sesión
        self.password_entry.bind("<Return>", lambda event: self.ejecutar_login())

        # Etiqueta de Mensaje de Error
        self.error_label = ctk.CTkLabel(
            self.main_frame, 
            text="", 
            text_color="#FF5252", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.error_label.pack(pady=5)

        # Botón Ingresar
        self.login_button = ctk.CTkButton(
            self.main_frame, 
            text="Ingresar", 
            command=self.ejecutar_login,
            width=280,
            height=40,
            fg_color="#1F6AA5",
            hover_color="#144870"
        )
        self.login_button.pack(pady=(10, 20))

    def ejecutar_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Por favor ingresa usuario y contraseña")
            return

        usuario = autenticar_usuario(username, password)

        if usuario:
            self.error_label.configure(text="")
            self.destroy()
            self.on_login_success(usuario)
        else:
            self.error_label.configure(text="Usuario o contraseña incorrectos")