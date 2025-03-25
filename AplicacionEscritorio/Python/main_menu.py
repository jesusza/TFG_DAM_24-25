import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt

from equipos import EquiposWidget
from contratos import ContratosWidget
from ingresos_entradas import IngresosWidget
from jugadores_Widget import JugadoresWidget
from inventario_widget import InventarioWidget
from entrenamientos_widget import EntrenamientosWidget
from resultadosWidget import ResultadosWidget
from clasificacion_widget import ClasificacionWidget  # <-- AÑADIDO

class MainMenu(QWidget):
    def __init__(self, team, name, role, email, logout_callback):
        super().__init__()
        self.setWindowTitle("CRM - Menú Principal")
        self.setGeometry(100, 100, 1200, 800)

        self.team = team
        self.name = name
        self.role = role.lower()
        self.email = email
        self.logout_callback = logout_callback

        main_layout = QVBoxLayout()

        self.top_bar = QLabel(f"Bienvenido {name} - Equipo: {team} - Rol: {role.capitalize()}")
        self.top_bar.setAlignment(Qt.AlignCenter)
        self.top_bar.setStyleSheet("background-color: #002D62; color: white; padding: 10px; font-size: 16px;")
        main_layout.addWidget(self.top_bar)

        content_layout = QHBoxLayout()

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: #0056b3;")
        sidebar_layout = QVBoxLayout()

        self.menu_buttons = {}
        menu_items = {
            "Equipos": (self.show_equipos, ["directivo", "entrenador"]),
            "Contratos": (self.show_contratos, ["directivo"]),
            "Ingreso Entradas": (self.show_ingresos_entradas, ["directivo"]),
            "Jugadores": (self.show_jugadores, ["directivo", "entrenador", "jugador"]),
            "Inventario": (self.show_inventario, ["directivo"]),
            "Clasificación": (self.show_clasificacion, ["directivo", "entrenador", "jugador"]),  # <-- MODIFICADO
            "Entrenamientos": (self.show_entrenamientos, ["directivo", "entrenador", "jugador"]),
            "Resultados del Año": (self.show_resultados, ["directivo"])
        }

        for item, (callback, roles_allowed) in menu_items.items():
            if self.role in roles_allowed:
                btn = QPushButton(item)
                btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
                btn.clicked.connect(self.create_highlight_function(btn, callback))
                self.menu_buttons[item] = btn
                sidebar_layout.addWidget(btn)

        self.logout_button = QPushButton("Cerrar Sesión")
        self.logout_button.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.logout_button.clicked.connect(self.logout_callback)
        sidebar_layout.addWidget(self.logout_button)

        self.sidebar.setLayout(sidebar_layout)

        self.stack = QStackedWidget()

        self.equipos_widget = EquiposWidget()
        self.contratos_widget = ContratosWidget()
        self.ingresos_widget = IngresosWidget()
        self.jugadores_widget = JugadoresWidget(read_only=(self.role == "jugador"))
        self.inventario_widget = InventarioWidget()
        self.entrenamientos_widget = EntrenamientosWidget(read_only=(self.role == "jugador"))
        self.resultados_widget = ResultadosWidget()
        self.clasificacion_widget = ClasificacionWidget()  # <-- AÑADIDO

        self.stack.addWidget(self.equipos_widget)
        self.stack.addWidget(self.contratos_widget)
        self.stack.addWidget(self.ingresos_widget)
        self.stack.addWidget(self.jugadores_widget)
        self.stack.addWidget(self.inventario_widget)
        self.stack.addWidget(self.entrenamientos_widget)
        self.stack.addWidget(self.resultados_widget)
        self.stack.addWidget(self.clasificacion_widget)  # <-- AÑADIDO

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_highlight_function(self, button, callback):
        def highlight():
            for btn in self.menu_buttons.values():
                btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
            button.setStyleSheet("background-color: gold; color: black; padding: 10px; border-radius: 5px;")
            callback()
        return highlight

    def show_equipos(self):
        self.stack.setCurrentWidget(self.equipos_widget)

    def show_contratos(self):
        self.stack.setCurrentWidget(self.contratos_widget)

    def show_ingresos_entradas(self):
        self.stack.setCurrentWidget(self.ingresos_widget)

    def show_jugadores(self):
        self.stack.setCurrentWidget(self.jugadores_widget)

    def show_inventario(self):
        self.stack.setCurrentWidget(self.inventario_widget)

    def show_entrenamientos(self):
        self.stack.setCurrentWidget(self.entrenamientos_widget)

    def show_resultados(self):
        self.stack.setCurrentWidget(self.resultados_widget)

    def show_clasificacion(self):
        self.stack.setCurrentWidget(self.clasificacion_widget)
