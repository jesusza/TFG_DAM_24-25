import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from equipos import EquiposWidget
from contratos import ContratosWidget  # Importar la vista de contratos

class MainMenu(QWidget):
    def __init__(self, team, name, role, email, logout_callback):
        super().__init__()
        self.setWindowTitle("CRM - Menú Principal")
        self.setGeometry(100, 100, 1200, 800)

        self.team = team
        self.name = name
        self.role = role
        self.email = email
        self.logout_callback = logout_callback

        # Layout principal
        main_layout = QVBoxLayout()

        # Barra superior
        self.top_bar = QLabel(f"Bienvenido {name} - Equipo: {team}")
        self.top_bar.setAlignment(Qt.AlignCenter)
        self.top_bar.setStyleSheet("background-color: #002D62; color: white; padding: 10px; font-size: 16px;")
        main_layout.addWidget(self.top_bar)

        # Layout de contenido dividido
        content_layout = QHBoxLayout()

        # Menú lateral
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: #0056b3;")
        sidebar_layout = QVBoxLayout()

        self.menu_buttons = {}
        menu_items = {
            "Equipos": self.show_equipos,
            "Contratos": self.show_contratos,
            "Ingreso Entradas": lambda: print("Ingreso Entradas"),
            "Jugadores": lambda: print("Jugadores"),
            "Productos": lambda: print("Productos"),
            "Inventario": lambda: print("Inventario"),
            "Calendario": lambda: print("Calendario"),
            "Clasificación": lambda: print("Clasificación"),
            "Entrenamientos": lambda: print("Entrenamientos"),
            "Gráficos Equipo": lambda: print("Gráficos Equipo"),
            "Resultados del Año": lambda: print("Resultados del Año"),
            "Contratos del Personal": lambda: print("Contratos del Personal")
        }

        for item, callback in menu_items.items():
            btn = QPushButton(item)
            btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
            btn.clicked.connect(self.create_highlight_function(btn, callback))
            self.menu_buttons[item] = btn
            sidebar_layout.addWidget(btn)

        # Botón de cerrar sesión
        self.logout_button = QPushButton("Cerrar Sesión")
        self.logout_button.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.logout_button.clicked.connect(self.logout_callback)
        sidebar_layout.addWidget(self.logout_button)

        self.sidebar.setLayout(sidebar_layout)

        # Contenido principal
        self.stack = QStackedWidget()
        self.equipos_widget = EquiposWidget()
        self.contratos_widget = ContratosWidget()

        self.stack.addWidget(self.equipos_widget)
        self.stack.addWidget(self.contratos_widget)

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_highlight_function(self, button, callback):
        """Resalta el botón seleccionado y ejecuta su función."""
        def highlight():
            for btn in self.menu_buttons.values():
                btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
            button.setStyleSheet("background-color: gold; color: black; padding: 10px; border-radius: 5px;")
            callback()
        return highlight

    def show_equipos(self):
        """Cambia la vista para mostrar Equipos."""
        self.stack.setCurrentWidget(self.equipos_widget)

    def show_contratos(self):
        """Cambia la vista para mostrar Contratos."""
        self.stack.setCurrentWidget(self.contratos_widget)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainMenu("Club", "Directivo", "Admin", "directivo@email.com", lambda: print("Logout"))
    window.show()
    sys.exit(app.exec_())
