import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QDialog, QFormLayout, QLineEdit, QHeaderView
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================
# CONFIGURACIÓN DE FIREBASE
# ==========================================
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ==========================================
# FORMULARIO PARA AÑADIR/EDITAR JUGADOR
# ==========================================
class FormularioJugador(QDialog):
    def __init__(self, jugador_data=None):
        super().__init__()
        self.setWindowTitle("Formulario de Jugador")
        self.setGeometry(300, 300, 400, 350)

        self.jugador_data = jugador_data or {}
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos
        self.equipo_input = QLineEdit(self.jugador_data.get("equipo", ""))
        self.nombre_input = QLineEdit(self.jugador_data.get("nombre", ""))
        self.posicion_input = QLineEdit(self.jugador_data.get("posicion", ""))
        self.dorsal_input = QLineEdit(str(self.jugador_data.get("dorsal", 0)))
        self.goles_input = QLineEdit(str(self.jugador_data.get("goles", 0)))
        self.asistencias_input = QLineEdit(str(self.jugador_data.get("asistencias", 0)))
        self.amarillas_input = QLineEdit(str(self.jugador_data.get("tarjetas_amarillas", 0)))
        self.rojas_input = QLineEdit(str(self.jugador_data.get("tarjetas_rojas", 0)))

        form_layout.addRow("Equipo:", self.equipo_input)
        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Posición:", self.posicion_input)
        form_layout.addRow("Dorsal:", self.dorsal_input)
        form_layout.addRow("Goles:", self.goles_input)
        form_layout.addRow("Asistencias:", self.asistencias_input)
        form_layout.addRow("Tarj Amarillas:", self.amarillas_input)
        form_layout.addRow("Tarj Rojas:", self.rojas_input)

        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        return {
            "equipo": self.equipo_input.text().strip(),
            "nombre": self.nombre_input.text().strip(),
            "posicion": self.posicion_input.text().strip(),
            "dorsal": self.dorsal_input.text().strip(),
            "goles": self.goles_input.text().strip(),
            "asistencias": self.asistencias_input.text().strip(),
            "tarjetas_amarillas": self.amarillas_input.text().strip(),
            "tarjetas_rojas": self.rojas_input.text().strip(),
        }

# ==========================================
# WIDGET PRINCIPAL (JugadoresWidget)
# ==========================================
class JugadoresWidget(QWidget):
    def __init__(self, read_only=False):
        super().__init__()
        self.read_only = read_only
        self.row_to_doc_id = {}  # Inicializar como un diccionario vacío
        self.setup_ui()

    def setup_ui(self):
        # Título y configuración básica
        self.setWindowTitle("Gestión de Jugadores (Colección 'Jugadores')")
        self.setGeometry(200, 200, 1000, 600)
        layout = QVBoxLayout()

        # Título
        self.title_label = QLabel("Gestión de Jugadores")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filtro superior (equipo + búsqueda)
        filter_layout = QHBoxLayout()
        self.equipo_selector = QComboBox()
        self.equipo_selector.currentIndexChanged.connect(self.load_players)
        filter_layout.addWidget(self.equipo_selector)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_input.textChanged.connect(self.load_players)  # Recargar al cambiar texto
        filter_layout.addWidget(self.search_input)

        layout.addLayout(filter_layout)

        # Tabla: Mostrar información de jugadores
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "DocID", "Equipo", "Nombre", "Posición", "Dorsal",
            "Goles", "Asist", "TarjAmar", "TarjRojas"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #0056b3;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Botones
        buttons_layout = QHBoxLayout()

        # Botón "Añadir Jugador"
        self.add_player_btn = QPushButton("Añadir Jugador")
        self.add_player_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
        self.add_player_btn.clicked.connect(self.add_player)
        self.add_player_btn.setEnabled(not self.read_only)  # Solo habilitado si no es modo lectura

        # Botón "Editar Jugador"
        self.edit_player_btn = QPushButton("Editar Jugador")
        self.edit_player_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.edit_player_btn.clicked.connect(self.edit_player)
        self.edit_player_btn.setEnabled(not self.read_only)  # Solo habilitado si no es modo lectura

        # Botón "Eliminar Jugador"
        self.delete_player_btn = QPushButton("Eliminar Jugador")
        self.delete_player_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.delete_player_btn.clicked.connect(self.delete_selected_player)
        self.delete_player_btn.setEnabled(not self.read_only)  # Solo habilitado si no es modo lectura

        # Botón "Gráfico Jugador"
        self.graph_player_btn = QPushButton("Gráfico Jugador")
        self.graph_player_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.graph_player_btn.clicked.connect(self.show_graph_player)

        # Botón "Gráfico Equipo"
        self.graph_team_btn = QPushButton("Gráfico Equipo")
        self.graph_team_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.graph_team_btn.clicked.connect(self.show_graph_team)

        # Añadir botones al layout
        buttons_layout.addWidget(self.add_player_btn)
        buttons_layout.addWidget(self.edit_player_btn)
        buttons_layout.addWidget(self.delete_player_btn)
        buttons_layout.addWidget(self.graph_player_btn)
        buttons_layout.addWidget(self.graph_team_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Cargar datos iniciales
        self.load_teams()
        self.load_players()


    # ========================
    # CARGAR EQUIPOS
    # ========================
    def load_teams(self):
        """Lee la colección 'Equipos' y rellena el ComboBox."""
        self.equipo_selector.clear()
        self.equipo_selector.addItem("Todos")
        equipos_ref = db.collection("Equipos").stream()
        for doc in equipos_ref:
            data = doc.to_dict()
            nombre_equipo = data.get("nombre", doc.id)
            self.equipo_selector.addItem(nombre_equipo)

    # ========================
    # GENERAR DOC ID TIPO JXXX
    # ========================
    def generate_jug_id(self):
        coll_ref = db.collection("Jugadores")
        last_index = 0
        all_jug_docs = coll_ref.stream()
        for d in all_jug_docs:
            if d.id.startswith("J"):
                num_str = d.id[1:]
                try:
                    number = int(num_str)
                    if number > last_index:
                        last_index = number
                except ValueError:
                    pass

        new_id_number = last_index + 1
        new_id = f"J{new_id_number:03d}"  # 'J' + 3 dígitos
        return new_id

    # ========================
    # CARGAR JUGADORES
    # ========================
    def load_players(self, index=None):
        self.table.setRowCount(0)
        self.row_to_doc_id.clear()

        equipo_name = self.equipo_selector.currentText()
        search_text = self.search_input.text().strip().lower()

        jugadores_ref = db.collection("Jugadores")
        if equipo_name != "Todos":
            jugadores_ref = jugadores_ref.where("equipo", "==", equipo_name)

        docs = list(jugadores_ref.stream())
        current_row = 0
        for doc in docs:
            data = doc.to_dict()
            # Filtro manual por nombre
            nombre_jugador = data.get("nombre", "").lower()
            if search_text and search_text not in nombre_jugador:
                continue

            self.table.insertRow(current_row)
            self.row_to_doc_id[current_row] = doc.id

            self.table.setItem(current_row, 0, QTableWidgetItem(doc.id))
            self.table.setItem(current_row, 1, QTableWidgetItem(data.get("equipo", "")))
            self.table.setItem(current_row, 2, QTableWidgetItem(data.get("nombre", "")))
            self.table.setItem(current_row, 3, QTableWidgetItem(data.get("posicion", "")))
            self.table.setItem(current_row, 4, QTableWidgetItem(data.get("dorsal", "")))
            self.table.setItem(current_row, 5, QTableWidgetItem(data.get("goles", "0")))
            self.table.setItem(current_row, 6, QTableWidgetItem(data.get("asistencias", "0")))
            self.table.setItem(current_row, 7, QTableWidgetItem(data.get("tarjetas_amarillas", "0")))
            self.table.setItem(current_row, 8, QTableWidgetItem(data.get("tarjetas_rojas", "0")))

            current_row += 1

    # ========================
    # AÑADIR JUGADOR
    # ========================
    def add_player(self):
        form = FormularioJugador()
        if form.exec_():
            new_data = form.get_data()

            # Forzar el campo 'equipo' si no es "Todos"
            combo_equipo = self.equipo_selector.currentText()
            if combo_equipo != "Todos":
                new_data["equipo"] = combo_equipo

            # Generar docID
            new_id = self.generate_jug_id()

            db.collection("Jugadores").document(new_id).set(new_data)
            self.load_players()

    # ========================
    # EDITAR JUGADOR
    # ========================
    def edit_player(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un jugador para editar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID para el jugador.")
            return

        snap = db.collection("Jugadores").document(doc_id).get()
        if not snap.exists:
            QMessageBox.warning(self, "Error", f"El documento {doc_id} no existe en 'Jugadores'.")
            return

        data_jugador = snap.to_dict()
        form = FormularioJugador(data_jugador)
        if form.exec_():
            updated_data = form.get_data()
            db.collection("Jugadores").document(doc_id).update(updated_data)
            QMessageBox.information(self, "Éxito", f"Jugador {doc_id} actualizado.")
            self.load_players()

    # ========================
    # ELIMINAR JUGADOR
    # ========================
    def delete_selected_player(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un jugador para eliminar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID en row_to_doc_id.")
            return

        confirm = QMessageBox.question(
            self, "Eliminar Jugador",
            f"¿Seguro que deseas eliminar el jugador con ID {doc_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db.collection("Jugadores").document(doc_id).delete()
            QMessageBox.information(self, "Eliminado", "Jugador eliminado correctamente.")
            self.load_players()

    # ========================
    # GRÁFICO JUGADOR
    # ========================
    def show_graph_player(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Selecciona un jugador para ver su gráfico.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            return

        snap = db.collection("Jugadores").document(doc_id).get()
        if not snap.exists:
            return

        data = snap.to_dict()
        nombre = data.get("nombre", doc_id)
        goles = int(data.get("goles", "0"))
        asist = int(data.get("asistencias", "0"))
        amar = int(data.get("tarjetas_amarillas", "0"))
        rojas = int(data.get("tarjetas_rojas", "0"))

        labels = ["Goles", "Asist", "T.Amar", "T.Rojas"]
        valores = [goles, asist, amar, rojas]

        import numpy as np
        x = np.arange(len(labels))
        plt.figure(figsize=(5, 4))
        plt.bar(x, valores, color=["blue", "orange", "yellow", "red"])
        plt.xticks(x, labels)
        plt.title(f"Estadísticas de {nombre}")
        plt.tight_layout()
        plt.show()

    # ========================
    # GRÁFICO EQUIPO
    # ========================
    def show_graph_team(self):
        equipo_name = self.equipo_selector.currentText()
        if not equipo_name or equipo_name == "Todos":
            QMessageBox.warning(self, "Error", "Selecciona un equipo válido para el gráfico.")
            return

        docs = db.collection("Jugadores").where("equipo", "==", equipo_name).stream()
        nombres = []
        goles_list = []
        asist_list = []
        for doc in docs:
            data = doc.to_dict()
            nombres.append(data.get("nombre", doc.id))
            goles_list.append(int(data.get("goles", "0")))
            asist_list.append(int(data.get("asistencias", "0")))

        if not nombres:
            QMessageBox.warning(self, "Sin datos", f"No hay jugadores en equipo {equipo_name}.")
            return

        import numpy as np
        x = np.arange(len(nombres))
        width = 0.4
        plt.figure(figsize=(8, 5))
        plt.bar(x - width/2, goles_list, width=width, color="blue", label="Goles")
        plt.bar(x + width/2, asist_list, width=width, color="orange", label="Asistencias")
        plt.xticks(x, nombres, rotation=45)
        plt.xlabel("Jugadores")
        plt.ylabel("Cantidad")
        plt.title(f"Estadísticas del Equipo: {equipo_name}")
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JugadoresWidget()
    window.show()
    sys.exit(app.exec_())
