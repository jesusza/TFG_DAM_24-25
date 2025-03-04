import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt

# Importa tus widgets
from equipos import EquiposWidget
from contratos import ContratosWidget
from ingresos_entradas import IngresosWidget
from jugadores_Widget import JugadoresWidget
from calendario import CalendarWidget
from inventario_widget import InventarioWidget
from entrenamientos_widget import EntrenamientosWidget  

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
        # Diccionario de botones y funciones
        menu_items = {
            "Equipos": self.show_equipos,
            "Contratos": self.show_contratos,
            "Ingreso Entradas": self.show_ingresos_entradas,
            "Jugadores": self.show_jugadores,
            "Inventario": self.show_inventario,
            "Calendario": self.show_calendar,
            "Clasificación": lambda: print("Clasificación"),
            "Entrenamientos": self.show_entrenamientos,  # ← Llamará a self.show_entrenamientos
            "Gráficos Equipo": lambda: print("Gráficos Equipo"),
            "Resultados del Año": lambda: print("Resultados del Año"),
            "Contratos del Personal": lambda: print("Contratos del Personal")
        }

        # Crear botones en el menú lateral
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

        # StackedWidget para cambiar vistas
        self.stack = QStackedWidget()

        # Instanciar los distintos widgets
        self.equipos_widget = EquiposWidget()
        self.contratos_widget = ContratosWidget()
        self.ingresos_widget = IngresosWidget()
        self.jugadores_widget = JugadoresWidget()
        self.calendar_widget = CalendarWidget()
        self.inventario_widget = InventarioWidget()
        self.entrenamientos_widget = EntrenamientosWidget()  # ← Añadimos EntrenamientosWidget

        # Agregar widgets al stack
        self.stack.addWidget(self.equipos_widget)
        self.stack.addWidget(self.contratos_widget)
        self.stack.addWidget(self.ingresos_widget)
        self.stack.addWidget(self.jugadores_widget)
        self.stack.addWidget(self.calendar_widget)
        self.stack.addWidget(self.inventario_widget)
        self.stack.addWidget(self.entrenamientos_widget)  # ← Lo agregamos al stack

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.stack, 1)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def create_highlight_function(self, button, callback):
        """Resalta el botón seleccionado y llama a la función asociada."""
        def highlight():
            # Revertir estilo de todos los botones
            for btn in self.menu_buttons.values():
                btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
            # Resaltar el botón actual
            button.setStyleSheet("background-color: gold; color: black; padding: 10px; border-radius: 5px;")
            # Ejecutar la función callback
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

    def show_calendar(self):
        self.stack.setCurrentWidget(self.calendar_widget)

    def show_entrenamientos(self):
        """Muestra EntrenamientosWidget."""
        self.stack.setCurrentWidget(self.entrenamientos_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu(
        "Mi Equipo", "Pedro", "Admin", "pedro@email.com",
        lambda: print("Logout presionado")
    )
    window.show()
    sys.exit(app.exec_())
