from src.services.db_service import init_db
from src.ui.login_view import LoginWindow
from src.ui.dashboard_view import DashboardWindow

def on_login_success(user_data):
    """Abre el Dashboard principal enviándole la información del usuario en sesión."""
    dashboard = DashboardWindow(user_data=user_data)
    dashboard.mainloop()

def main():
    # 1. Inicializar la base de datos
    init_db()

    # 2. Iniciar la interfaz gráfica de Login
    app = LoginWindow(on_login_success=on_login_success)
    app.mainloop()

if __name__ == "__main__":
    main()