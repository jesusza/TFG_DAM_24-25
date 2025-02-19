import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QDialog, QFormLayout, QLineEdit, QHeaderView
)
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, firestore

# ========================
# CONFIGURACIÓN DE FIREBASE
# ========================
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ========================
# FORMULARIO DE PARTIDO
# ========================
class FormularioPartido(QDialog):
    """
    Formulario para crear/editar un partido.
    Campos:
      - equipo_local, equipo_visitante
      - fecha, hora
      - estado (ej: Pendiente, Finalizado)
      - goles_local, goles_visitante
    """
    def __init__(self, partido_data=None):
        super().__init__()
        self.setWindowTitle("Formulario de Partido")
        self.setGeometry(300, 300, 400, 350)

        self.partido_data = partido_data or {}
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos
        self.equipo_local_input = QLineEdit(self.partido_data.get("equipo_local", ""))
        self.equipo_visitante_input = QLineEdit(self.partido_data.get("equipo_visitante", ""))
        self.fecha_input = QLineEdit(self.partido_data.get("fecha", ""))
        self.hora_input = QLineEdit(self.partido_data.get("hora", ""))
        self.estado_input = QLineEdit(self.partido_data.get("estado", "Pendiente"))
        self.goles_local_input = QLineEdit(str(self.partido_data.get("goles_local", 0)))
        self.goles_visitante_input = QLineEdit(str(self.partido_data.get("goles_visitante", 0)))

        form_layout.addRow("Equipo Local:", self.equipo_local_input)
        form_layout.addRow("Equipo Visitante:", self.equipo_visitante_input)
        form_layout.addRow("Fecha (YYYY-MM-DD):", self.fecha_input)
        form_layout.addRow("Hora:", self.hora_input)
        form_layout.addRow("Estado:", self.estado_input)
        form_layout.addRow("Goles Local:", self.goles_local_input)
        form_layout.addRow("Goles Visitante:", self.goles_visitante_input)

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
        """Retorna los datos del partido en un diccionario."""
        return {
            "equipo_local": self.equipo_local_input.text().strip(),
            "equipo_visitante": self.equipo_visitante_input.text().strip(),
            "fecha": self.fecha_input.text().strip(),
            "hora": self.hora_input.text().strip(),
            "estado": self.estado_input.text().strip(),
            "goles_local": int(self.goles_local_input.text() or 0),
            "goles_visitante": int(self.goles_visitante_input.text() or 0),
        }

# ========================
# WIDGET PRINCIPAL: CalendarWidget
# ========================
class CalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Calendario")
        self.setGeometry(200, 200, 1000, 600)

        # Diccionario fila -> docID
        self.row_to_doc_id = {}

        layout = QVBoxLayout()

        self.title_label = QLabel("Gestión de Partidos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filtros: ComboBox equipo_local + búsqueda de equipo_visitante
        filter_layout = QHBoxLayout()

        self.equipo_selector = QComboBox()
        self.equipo_selector.currentIndexChanged.connect(self.load_matches)
        filter_layout.addWidget(self.equipo_selector)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por equipo visitante...")
        self.search_input.textChanged.connect(self.load_matches)
        filter_layout.addWidget(self.search_input)

        layout.addLayout(filter_layout)

        # Tabla con 8 columnas: docID, equipo_local, equipo_visitante, fecha, hora, goles_local, goles_visitante, estado
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "DocID", "Local", "Visitante", "Fecha", "Hora",
            "Goles Local", "Goles Visitante", "Estado"
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
        for col in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(col).setTextAlignment(Qt.AlignCenter)

        layout.addWidget(self.table)

        # Botones inferiores
        buttons_layout = QHBoxLayout()

        self.add_match_btn = QPushButton("Añadir Partido")
        self.add_match_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
        self.add_match_btn.clicked.connect(self.add_match)

        self.edit_match_btn = QPushButton("Editar Partido")
        self.edit_match_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.edit_match_btn.clicked.connect(self.edit_match)

        self.delete_match_btn = QPushButton("Eliminar Partido")
        self.delete_match_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.delete_match_btn.clicked.connect(self.delete_selected_match)

        buttons_layout.addWidget(self.add_match_btn)
        buttons_layout.addWidget(self.edit_match_btn)
        buttons_layout.addWidget(self.delete_match_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Cargar
        self.load_teams()
        self.load_matches()

    # ========================
    # Cargar combos de equipos
    # ========================
    def load_teams(self):
        """Lee la colección 'Equipos' y rellena el combo con sus nombres."""
        self.equipo_selector.clear()
        self.equipo_selector.addItem("Todos")
        equipos_ref = db.collection("Equipos").stream()
        for doc in equipos_ref:
            data = doc.to_dict()
            nombre_equipo = data.get("nombre", doc.id)
            self.equipo_selector.addItem(nombre_equipo)

    # ========================
    # Generar docID tipo PartidoXXX
    # ========================
    def generate_partido_id(self):
        """Busca el mayor número en IDs tipo 'PartidoXXX' y genera el siguiente."""
        coll_ref = db.collection("Calendario")
        last_index = 0

        all_docs = coll_ref.stream()
        for d in all_docs:
            if d.id.startswith("Partido"):
                # Extraer la parte numérica
                num_str = d.id.replace("Partido", "")
                try:
                    number = int(num_str)
                    if number > last_index:
                        last_index = number
                except ValueError:
                    pass

        new_id_number = last_index + 1
        new_id = f"Partido{new_id_number:03d}"  # 'Partido001', 'Partido002', ...
        return new_id

    # ========================
    # Cargar Partidos
    # ========================
    def load_matches(self, index=None):
        """Filtra docs en 'Calendario' por equipo_local (combo) y equipo_visitante (search_input)."""
        self.table.setRowCount(0)
        self.row_to_doc_id.clear()

        equipo_filtro = self.equipo_selector.currentText()  # 'Todos' o un nombre
        search_text = self.search_input.text().strip().lower()

        matches_ref = db.collection("Calendario")
        # Filtro de equipo
        if equipo_filtro != "Todos":
            matches_ref = matches_ref.where("equipo_local", "==", equipo_filtro)

        docs = matches_ref.stream()
        current_row = 0
        for doc in docs:
            data = doc.to_dict()
            # Filtro manual por equipo_visitante
            visitante = data.get("equipo_visitante", "").lower()
            if search_text and search_text not in visitante:
                continue

            self.table.insertRow(current_row)
            self.row_to_doc_id[current_row] = doc.id

            # Columnas:
            # 0: doc.id
            # 1: equipo_local
            # 2: equipo_visitante
            # 3: fecha
            # 4: hora
            # 5: goles_local
            # 6: goles_visitante
            # 7: estado
            self.table.setItem(current_row, 0, QTableWidgetItem(doc.id))
            self.table.setItem(current_row, 1, QTableWidgetItem(data.get("equipo_local", "")))
            self.table.setItem(current_row, 2, QTableWidgetItem(data.get("equipo_visitante", "")))
            self.table.setItem(current_row, 3, QTableWidgetItem(data.get("fecha", "")))
            self.table.setItem(current_row, 4, QTableWidgetItem(data.get("hora", "")))
            self.table.setItem(current_row, 5, QTableWidgetItem(str(data.get("goles_local", 0))))
            self.table.setItem(current_row, 6, QTableWidgetItem(str(data.get("goles_visitante", 0))))
            self.table.setItem(current_row, 7, QTableWidgetItem(data.get("estado", "Pendiente")))

            current_row += 1

    # ========================
    # Añadir Partido
    # ========================
    def add_match(self):
        """Crea un doc en 'Calendario' con ID tipo 'PartidoXXX'."""
        form = FormularioPartido()
        if form.exec_():
            new_data = form.get_data()

            # Forzar el equipo local al combo si no es 'Todos'
            combo_equipo = self.equipo_selector.currentText()
            if combo_equipo != "Todos":
                new_data["equipo_local"] = combo_equipo

            # Generar docID
            new_id = self.generate_partido_id()

            db.collection("Calendario").document(new_id).set(new_data)
            QMessageBox.information(self, "Éxito", f"Partido agregado (doc ID: {new_id}).")
            self.load_matches()

    # ========================
    # Editar Partido
    # ========================
    def edit_match(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un partido para editar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID de partido.")
            return

        snap = db.collection("Calendario").document(doc_id).get()
        if not snap.exists:
            QMessageBox.warning(self, "Error", f"El documento {doc_id} no existe en 'Calendario'.")
            return

        data_partido = snap.to_dict()
        form = FormularioPartido(data_partido)
        if form.exec_():
            updated_data = form.get_data()
            db.collection("Calendario").document(doc_id).update(updated_data)
            QMessageBox.information(self, "Éxito", f"Partido {doc_id} actualizado.")
            self.load_matches()

    # ========================
    # Eliminar Partido
    # ========================
    def delete_selected_match(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un partido para eliminar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID del partido.")
            return

        confirm = QMessageBox.question(
            self, "Eliminar Partido",
            f"¿Seguro que deseas eliminar el partido con ID {doc_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db.collection("Calendario").document(doc_id).delete()
            QMessageBox.information(self, "Eliminado", "Partido eliminado correctamente.")
            self.load_matches()

# =========================
# MAIN (PRUEBA)
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarWidget()
    window.show()
    sys.exit(app.exec_())
