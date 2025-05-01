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

# ------------------------------------------------------------------
#  Utilidades
# ------------------------------------------------------------------
def _str(value):
    """Convierte cualquier valor a cadena; si es None, devuelve ''. """
    return "" if value is None else str(value)

def _int(texto):
    """
    Convierte el texto a int;  
    si viene vacío o es inválido devuelve 0.
    """
    try:
        return int(texto)
    except (ValueError, TypeError):
        return 0

# ------------------------------------------------------------------
#  Configuración Firebase
# ------------------------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ------------------------------------------------------------------
#  Formulario de alta / edición de jugador
# ------------------------------------------------------------------
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
        self.dorsal_input = QLineEdit(_str(self.jugador_data.get("dorsal", 0)))
        self.goles_input = QLineEdit(_str(self.jugador_data.get("goles", 0)))
        self.asistencias_input = QLineEdit(_str(self.jugador_data.get("asistencias", 0)))
        self.amarillas_input = QLineEdit(_str(self.jugador_data.get("tarjetas_amarillas", 0)))
        self.rojas_input = QLineEdit(_str(self.jugador_data.get("tarjetas_rojas", 0)))

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
        """Devuelve los datos del formulario convirtiendo
        los campos numéricos a int."""
        return {
            "equipo": self.equipo_input.text().strip(),
            "nombre": self.nombre_input.text().strip(),
            "posicion": self.posicion_input.text().strip(),
            "dorsal": _int(self.dorsal_input.text()),
            "goles": _int(self.goles_input.text()),
            "asistencias": _int(self.asistencias_input.text()),
            "tarjetas_amarillas": _int(self.amarillas_input.text()),
            "tarjetas_rojas": _int(self.rojas_input.text()),
        }

# ------------------------------------------------------------------
#  Widget principal
# ------------------------------------------------------------------
class JugadoresWidget(QWidget):
    def __init__(self, read_only=False):
        super().__init__()
        self.read_only = read_only
        self.row_to_doc_id = {}
        self.setup_ui()

    # -------------------------
    #  Interfaz
    # -------------------------
    def setup_ui(self):
        self.setWindowTitle("Gestión de Jugadores (Colección 'Jugadores')")
        self.setGeometry(200, 200, 1000, 600)
        layout = QVBoxLayout()

        # Título
        self.title_label = QLabel("Gestión de Jugadores")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filtros
        filter_layout = QHBoxLayout()
        self.equipo_selector = QComboBox()
        self.equipo_selector.currentIndexChanged.connect(self.load_players)
        filter_layout.addWidget(self.equipo_selector)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre...")
        self.search_input.textChanged.connect(self.load_players)
        filter_layout.addWidget(self.search_input)

        layout.addLayout(filter_layout)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "DocID", "Equipo", "Nombre", "Posición", "Dorsal",
            "Goles", "Asist", "TarjAmar", "TarjRojas"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 14px; gridline-color: #ccc; }
            QHeaderView::section {
                background-color: #0056b3; color: white;
                font-weight: bold; font-size: 14px; border: none;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Botones
        buttons_layout = QHBoxLayout()

        self.add_player_btn = QPushButton("Añadir Jugador")
        self.add_player_btn.setStyleSheet(
            "background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;"
        )
        self.add_player_btn.clicked.connect(self.add_player)
        self.add_player_btn.setEnabled(not self.read_only)

        self.edit_player_btn = QPushButton("Editar Jugador")
        self.edit_player_btn.setStyleSheet(
            "background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;"
        )
        self.edit_player_btn.clicked.connect(self.edit_player)
        self.edit_player_btn.setEnabled(not self.read_only)

        self.delete_player_btn = QPushButton("Eliminar Jugador")
        self.delete_player_btn.setStyleSheet(
            "background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;"
        )
        self.delete_player_btn.clicked.connect(self.delete_selected_player)
        self.delete_player_btn.setEnabled(not self.read_only)

        self.graph_player_btn = QPushButton("Gráfico Jugador")
        self.graph_player_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;"
        )
        self.graph_player_btn.clicked.connect(self.show_graph_player)

        self.graph_team_btn = QPushButton("Gráfico Equipo")
        self.graph_team_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;"
        )
        self.graph_team_btn.clicked.connect(self.show_graph_team)

        buttons_layout.addWidget(self.add_player_btn)
        buttons_layout.addWidget(self.edit_player_btn)
        buttons_layout.addWidget(self.delete_player_btn)
        buttons_layout.addWidget(self.graph_player_btn)
        buttons_layout.addWidget(self.graph_team_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Datos iniciales
        self.load_teams()
        self.load_players()

    # -------------------------
    #  Cargar equipos
    # -------------------------
    def load_teams(self):
        self.equipo_selector.clear()
        self.equipo_selector.addItem("Todos")
        for doc in db.collection("Equipos").stream():
            nombre_equipo = doc.to_dict().get("nombre", doc.id)
            self.equipo_selector.addItem(nombre_equipo)

    # -------------------------
    #  Generar ID tipo JXXX
    # -------------------------
    def generate_jug_id(self):
        last_index = 0
        for d in db.collection("Jugadores").stream():
            if d.id.startswith("J"):
                try:
                    last_index = max(last_index, int(d.id[1:]))
                except ValueError:
                    pass
        return f"J{last_index + 1:03d}"

    # -------------------------
    #  Cargar jugadores
    # -------------------------
    def load_players(self, *_):
        self.table.setRowCount(0)
        self.row_to_doc_id.clear()

        equipo_name = self.equipo_selector.currentText()
        search_text = self.search_input.text().strip().lower()

        jugadores_ref = db.collection("Jugadores")
        if equipo_name != "Todos":
            jugadores_ref = jugadores_ref.where("equipo", "==", equipo_name)

        current_row = 0
        for doc in jugadores_ref.stream():
            data = doc.to_dict()

            # Filtro por nombre
            if search_text and search_text not in data.get("nombre", "").lower():
                continue

            self.table.insertRow(current_row)
            self.row_to_doc_id[current_row] = doc.id

            self.table.setItem(current_row, 0, QTableWidgetItem(doc.id))
            self.table.setItem(current_row, 1, QTableWidgetItem(_str(data.get("equipo"))))
            self.table.setItem(current_row, 2, QTableWidgetItem(_str(data.get("nombre"))))
            self.table.setItem(current_row, 3, QTableWidgetItem(_str(data.get("posicion"))))
            self.table.setItem(current_row, 4, QTableWidgetItem(_str(data.get("dorsal"))))
            self.table.setItem(current_row, 5, QTableWidgetItem(_str(data.get("goles"))))
            self.table.setItem(current_row, 6, QTableWidgetItem(_str(data.get("asistencias"))))
            self.table.setItem(current_row, 7, QTableWidgetItem(_str(data.get("tarjetas_amarillas"))))
            self.table.setItem(current_row, 8, QTableWidgetItem(_str(data.get("tarjetas_rojas"))))

            current_row += 1

    # -------------------------
    #  Añadir jugador
    # -------------------------
    def add_player(self):
        form = FormularioJugador()
        if form.exec_():
            new_data = form.get_data()

            # Forzar equipo si se filtró por uno
            combo_equipo = self.equipo_selector.currentText()
            if combo_equipo != "Todos":
                new_data["equipo"] = combo_equipo

            new_id = self.generate_jug_id()
            db.collection("Jugadores").document(new_id).set(new_data)
            self.load_players()

    # -------------------------
    #  Editar jugador
    # -------------------------
    def edit_player(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un jugador para editar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        snap = db.collection("Jugadores").document(doc_id).get()
        if not snap.exists:
            QMessageBox.warning(self, "Error", f"El documento {doc_id} no existe.")
            return

        form = FormularioJugador(snap.to_dict())
        if form.exec_():
            db.collection("Jugadores").document(doc_id).update(form.get_data())
            QMessageBox.information(self, "Éxito", f"Jugador {doc_id} actualizado.")
            self.load_players()

    # -------------------------
    #  Eliminar jugador
    # -------------------------
    def delete_selected_player(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un jugador para eliminar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        confirm = QMessageBox.question(
            self, "Eliminar Jugador",
            f"¿Seguro que deseas eliminar al jugador {doc_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db.collection("Jugadores").document(doc_id).delete()
            QMessageBox.information(self, "Eliminado", "Jugador eliminado correctamente.")
            self.load_players()

    # -------------------------
    #  Gráfico individual
    # -------------------------
    def show_graph_player(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Selecciona un jugador para ver su gráfico.")
            return

        doc_id = self.row_to_doc_id[selected_row]
        snap = db.collection("Jugadores").document(doc_id).get()
        if not snap.exists:
            return
        data = snap.to_dict()

        nombre = data.get("nombre", doc_id)
        goles = int(data.get("goles") or 0)
        asist = int(data.get("asistencias") or 0)
        amar = int(data.get("tarjetas_amarillas") or 0)
        rojas = int(data.get("tarjetas_rojas") or 0)

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

    # -------------------------
    #  Gráfico por equipo
    # -------------------------
    def show_graph_team(self):
        equipo_name = self.equipo_selector.currentText()
        if equipo_name in ("", "Todos"):
            QMessageBox.warning(self, "Error", "Selecciona un equipo válido para el gráfico.")
            return

        nombres, goles_list, asist_list = [], [], []
        for doc in db.collection("Jugadores").where("equipo", "==", equipo_name).stream():
            data = doc.to_dict()
            nombres.append(data.get("nombre", doc.id))
            goles_list.append(int(data.get("goles") or 0))
            asist_list.append(int(data.get("asistencias") or 0))

        if not nombres:
            QMessageBox.warning(self, "Sin datos", f"No hay jugadores en {equipo_name}.")
            return

        import numpy as np
        x = np.arange(len(nombres))
        width = 0.4
        plt.figure(figsize=(8, 5))
        plt.bar(x - width/2, goles_list, width=width, label="Goles")
        plt.bar(x + width/2, asist_list, width=width, label="Asistencias")
        plt.xticks(x, nombres, rotation=45)
        plt.xlabel("Jugadores")
        plt.ylabel("Cantidad")
        plt.title(f"Estadísticas del Equipo: {equipo_name}")
        plt.legend()
        plt.tight_layout()
        plt.show()

# ------------------------------------------------------------------
#  Arranque
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JugadoresWidget()
    window.show()
    sys.exit(app.exec_())
