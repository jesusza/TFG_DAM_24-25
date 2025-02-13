import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLabel, QVBoxLayout, QWidget
from main_menu import MainMenu

class MainWindow(QMainWindow):
    def __init__(self, team, name, role, email):
        super().__init__()
        self.setWindowTitle("CRM - Principal")
        self.setGeometry(100, 100, 1200, 800)

        # Stack de widgets
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear pantalla de bienvenida personalizada
        self.welcome_screen = QWidget()
        layout = QVBoxLayout()
        self.welcome_label = QLabel(f"Bienvenido {name}\nEquipo: {team}\nRol: {role}")
        layout.addWidget(self.welcome_label)
        self.welcome_screen.setLayout(layout)

        # Inicializar el menú principal
        self.main_menu = MainMenu(team, name, role, email, self.handle_logout)
        
        # Agregar las pantallas al stack
        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.main_menu)

        # Mostrar la pantalla del menú principal
        self.stack.setCurrentWidget(self.main_menu)

    def handle_logout(self):
        """Cierra la sesión y regresa al inicio de sesión."""
        from login import LoginWindow  # Importación dentro de la función para evitar errores circulares
        self.login_window = LoginWindow(self.handle_login_success)
        self.login_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    from login import LoginWindow  # Asegurar que arranca con login
    login_window = LoginWindow(lambda team, name, role, email: MainWindow(team, name, role, email).show())
    login_window.show()
    sys.exit(app.exec_())
