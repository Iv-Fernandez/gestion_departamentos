import customtkinter as ctk
from src.services.auth_service import authenticate_user

# Configuración del tema visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()

        self.on_login_success = on_login_success

        # Configuración de la ventana principal
        self.title("Sistema de Gestión - Iniciar Sesión")
        self.geometry("400x480")
        self.resizable(False, False)

        # Centrar la ventana en la pantalla
        self.eval('tk::PlaceWindow . center')

        self.create_widgets()

    def create_widgets(self):
        # Frame contenedor
        self.frame = ctk.CTkFrame(master=self, corner_radius=15)
        self.frame.pack(pady=30, padx=30, fill="both", expand=True)

        # Título
        self.label_title = ctk.CTkLabel(
            master=self.frame, 
            text="Bienvenido", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_title.pack(pady=(30, 10))

        self.label_subtitle = ctk.CTkLabel(
            master=self.frame, 
            text="Gestión de Departamentos", 
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.label_subtitle.pack(pady=(0, 20))

        # Campo: Usuario
        self.entry_user = ctk.CTkEntry(
            master=self.frame, 
            placeholder_text="Usuario",
            width=260,
            height=40
        )
        self.entry_user.pack(pady=10)

        # Campo: Contraseña
        self.entry_pass = ctk.CTkEntry(
            master=self.frame, 
            placeholder_text="Contraseña", 
            show="*",
            width=260,
            height=40
        )
        self.entry_pass.pack(pady=10)

        # Mensaje de error (oculto inicialmente)
        self.label_error = ctk.CTkLabel(
            master=self.frame, 
            text="", 
            text_color="#FF5555",
            font=ctk.CTkFont(size=12)
        )
        self.label_error.pack(pady=5)

        # Botón Iniciar Sesión
        self.btn_login = ctk.CTkButton(
            master=self.frame, 
            text="Iniciar Sesión", 
            command=self.handle_login,
            width=260,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_login.pack(pady=(10, 20))

        # Permitir enviar con la tecla Enter
        self.bind('<Return>', lambda event: self.handle_login())

    def handle_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if not username or not password:
            self.label_error.configure(text="Por favor completa todos los campos.")
            return

        # Intentar autenticar con el servicio de backend
        user = authenticate_user(username, password)

        if user:
            self.label_error.configure(text="")
            self.destroy()  # Cierra la ventana de login
            self.on_login_success(user)  # Llama a la siguiente ventana pasándole el usuario
        else:
            self.label_error.configure(text="Usuario o contraseña incorrectos.")