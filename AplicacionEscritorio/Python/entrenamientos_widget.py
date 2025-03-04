import sys
import base64
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QDialog, QFormLayout, QLineEdit, QHeaderView,
    QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# CONFIGURACIÓN DE FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# FORMULARIO DE ENTRENAMIENTO
# =========================
class FormularioEntrenamiento(QDialog):
    """
    Formulario para crear/editar un entrenamiento en la colección 'Entrenamientos'.
    Campos:
      - fecha, entrenador, equipo
      - titulo/sesion_name
      - actividades (multilinea)
      - objetivos_tacticos (multilinea)
      - objetivos_fisicos (multilinea)
      - material (multilinea)
      - observaciones (multilinea)
      - incidencias (multilinea)
      - diagrama (base64 de imagen, opcional)
    """
    def __init__(self, entrenamiento_data=None, equipos_list=None, coaches_list=None):
        super().__init__()
        self.setWindowTitle("Formulario de Entrenamiento")
        self.setGeometry(300, 300, 600, 600)

        self.entrenamiento_data = entrenamiento_data or {}
        self.equipos_list = equipos_list or []       # Lista de equipos
        self.coaches_list = coaches_list or []       # Lista de entrenadores
        self.diagrama_base64 = self.entrenamiento_data.get("diagrama", "")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos básicos
        self.fecha_input = QLineEdit(self.entrenamiento_data.get("fecha", ""))
        self.titulo_input = QLineEdit(self.entrenamiento_data.get("titulo", ""))

        # ComboBox de Equipo
        self.equipo_combo = QComboBox()
        self.equipo_combo.addItems(self.equipos_list)
        # Ajustar el valor actual, si existe
        current_eq = self.entrenamiento_data.get("equipo", "")
        if current_eq in self.equipos_list:
            self.equipo_combo.setCurrentText(current_eq)

        # ComboBox de Entrenador
        self.entrenador_combo = QComboBox()
        self.entrenador_combo.addItems(self.coaches_list)
        current_coach = self.entrenamiento_data.get("entrenador", "")
        if current_coach in self.coaches_list:
            self.entrenador_combo.setCurrentText(current_coach)

        # Textos multilinea
        self.actividades_txt = QTextEdit(self.entrenamiento_data.get("actividades", ""))
        self.obj_tacticos_txt = QTextEdit(self.entrenamiento_data.get("objetivos_tacticos", ""))
        self.obj_fisicos_txt = QTextEdit(self.entrenamiento_data.get("objetivos_fisicos", ""))
        self.material_txt = QTextEdit(self.entrenamiento_data.get("material", ""))
        self.observaciones_txt = QTextEdit(self.entrenamiento_data.get("observaciones", ""))
        self.incidencias_txt = QTextEdit(self.entrenamiento_data.get("incidencias", ""))

        # Botón para cargar diagrama
        self.diagrama_btn = QPushButton("Cargar Diagrama")
        self.diagrama_btn.clicked.connect(self.cargar_diagrama)

        # Añadir campos al form
        form_layout.addRow("Fecha (YYYY-MM-DD):", self.fecha_input)
        form_layout.addRow("Título de la Sesión:", self.titulo_input)
        form_layout.addRow("Equipo:", self.equipo_combo)
        form_layout.addRow("Entrenador:", self.entrenador_combo)
        form_layout.addRow("Actividades/Ejercicios:", self.actividades_txt)
        form_layout.addRow("Objetivos Tácticos:", self.obj_tacticos_txt)
        form_layout.addRow("Objetivos Físicos:", self.obj_fisicos_txt)
        form_layout.addRow("Material:", self.material_txt)
        form_layout.addRow("Observaciones:", self.observaciones_txt)
        form_layout.addRow("Incidencias:", self.incidencias_txt)
        form_layout.addRow("Diagrama:", self.diagrama_btn)

        layout.addLayout(form_layout)

        # Botones de Guardar/Cancelar
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def cargar_diagrama(self):
        """
        Permite seleccionar una imagen y almacenarla en base64
        para guardarla en Firestore.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Diagrama", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            with open(file_path, "rb") as f:
                img_bytes = f.read()
                self.diagrama_base64 = base64.b64encode(img_bytes).decode("utf-8")
            QMessageBox.information(self, "Diagrama Cargado", f"Se ha cargado la imagen: {file_path}")

    def get_data(self):
        """
        Retorna el diccionario con los datos del entrenamiento,
        incluyendo diagrama_base64 si existe.
        """
        return {
            "fecha": self.fecha_input.text().strip(),
            "titulo": self.titulo_input.text().strip(),
            "equipo": self.equipo_combo.currentText(),
            "entrenador": self.entrenador_combo.currentText(),
            "actividades": self.actividades_txt.toPlainText(),
            "objetivos_tacticos": self.obj_tacticos_txt.toPlainText(),
            "objetivos_fisicos": self.obj_fisicos_txt.toPlainText(),
            "material": self.material_txt.toPlainText(),
            "observaciones": self.observaciones_txt.toPlainText(),
            "incidencias": self.incidencias_txt.toPlainText(),
            "diagrama": self.diagrama_base64
        }

# =========================
# WIDGET PRINCIPAL: EntrenamientosWidget
# =========================
class EntrenamientosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Entrenamientos (Colección 'Entrenamientos')")
        self.setGeometry(200, 200, 1100, 600)

        # Diccionario fila->docID
        self.row_to_doc_id = {}

        layout = QVBoxLayout()

        self.title_label = QLabel("Gestión de Entrenamientos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filtros: equipo + entrenador + busqueda (ej. por fecha)
        filter_layout = QHBoxLayout()

        self.equipo_filter = QLineEdit()
        self.equipo_filter.setPlaceholderText("Filtrar por equipo...")
        self.equipo_filter.textChanged.connect(self.load_trainings)
        filter_layout.addWidget(self.equipo_filter)

        self.coach_filter = QLineEdit()
        self.coach_filter.setPlaceholderText("Filtrar por entrenador...")
        self.coach_filter.textChanged.connect(self.load_trainings)
        filter_layout.addWidget(self.coach_filter)

        self.fecha_filter = QLineEdit()
        self.fecha_filter.setPlaceholderText("Filtrar por fecha (YYYY-MM-DD)...")
        self.fecha_filter.textChanged.connect(self.load_trainings)
        filter_layout.addWidget(self.fecha_filter)

        layout.addLayout(filter_layout)

        # Tabla con 5 columnas: docID, fecha, equipo, entrenador, titulo
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "DocID", "Fecha", "Equipo", "Entrenador", "Título"
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

        # Botones
        buttons_layout = QHBoxLayout()

        self.add_btn = QPushButton("Añadir Entrenamiento")
        self.add_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
        self.add_btn.clicked.connect(self.add_training)

        self.edit_btn = QPushButton("Editar Entrenamiento")
        self.edit_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.edit_btn.clicked.connect(self.edit_training)

        self.delete_btn = QPushButton("Eliminar Entrenamiento")
        self.delete_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.delete_btn.clicked.connect(self.delete_selected_training)

        buttons_layout.addWidget(self.add_btn)
        buttons_layout.addWidget(self.edit_btn)
        buttons_layout.addWidget(self.delete_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Cargar combos de equipo/entrenador (para formulario)
        self.equipos_list = self.load_equipos_list()
        self.coaches_list = self.load_coaches_list()

        self.load_trainings()

    # =========================
    # GENERAR DOCID TIPO ENTxxx
    # =========================
    def generate_training_id(self):
        coll_ref = db.collection("Entrenamientos")
        last_index = 0

        all_docs = coll_ref.stream()
        for d in all_docs:
            if d.id.startswith("ENT"):
                num_str = d.id[3:]  # si es ENT001 -> 001
                try:
                    number = int(num_str)
                    if number > last_index:
                        last_index = number
                except ValueError:
                    pass
        new_id_number = last_index + 1
        new_id = f"ENT{new_id_number:03d}"
        return new_id

    # =========================
    # CARGAR LISTA DE EQUIPOS
    # =========================
    def load_equipos_list(self):
        """Lee la colección 'Equipos' y devuelve la lista de nombres."""
        equipos_ref = db.collection("Equipos").stream()
        equipos = []
        for doc in equipos_ref:
            data = doc.to_dict()
            eq_name = data.get("nombre", doc.id)
            equipos.append(eq_name)
        return sorted(equipos)

    # =========================
    # CARGAR LISTA DE ENTRENADORES
    # =========================
    def load_coaches_list(self):
        """
        Supón que tienes una colección 'Usuarios' con un campo 'rol' = 'Entrenador',
        o algo similar. Ajusta según tu estructura real.
        """
        coaches = []
        users_ref = db.collection("Usuarios").where("rol", "==", "Entrenador").stream()
        for doc in users_ref:
            data = doc.to_dict()
            email = data.get("email", doc.id)
            coaches.append(email)
        return sorted(coaches)

    # =========================
    # CARGAR ENTRENAMIENTOS
    # =========================
    def load_trainings(self):
        self.table.setRowCount(0)
        self.row_to_doc_id.clear()

        eq_filter = self.equipo_filter.text().strip().lower()
        coach_filter = self.coach_filter.text().strip().lower()
        fecha_filter = self.fecha_filter.text().strip().lower()

        trainings_ref = db.collection("Entrenamientos").stream()
        docs = list(trainings_ref)

        current_row = 0
        for doc in docs:
            data = doc.to_dict()
            doc_id = doc.id
            # Filtrar
            eq = data.get("equipo", "").lower()
            coach = data.get("entrenador", "").lower()
            fecha = data.get("fecha", "").lower()
            if eq_filter and eq_filter not in eq:
                continue
            if coach_filter and coach_filter not in coach:
                continue
            if fecha_filter and fecha_filter not in fecha:
                continue

            self.table.insertRow(current_row)
            self.row_to_doc_id[current_row] = doc_id

            # Columnas: docID, fecha, equipo, entrenador, titulo
            self.table.setItem(current_row, 0, QTableWidgetItem(doc_id))
            self.table.setItem(current_row, 1, QTableWidgetItem(data.get("fecha", "")))
            self.table.setItem(current_row, 2, QTableWidgetItem(data.get("equipo", "")))
            self.table.setItem(current_row, 3, QTableWidgetItem(data.get("entrenador", "")))
            self.table.setItem(current_row, 4, QTableWidgetItem(data.get("titulo", "")))

            current_row += 1

    # =========================
    # AÑADIR ENTRENAMIENTO
    # =========================
    def add_training(self):
        form = FormularioEntrenamiento(equipos_list=self.equipos_list, coaches_list=self.coaches_list)
        if form.exec_():
            new_data = form.get_data()

            # Generar docID
            new_id = self.generate_training_id()
            db.collection("Entrenamientos").document(new_id).set(new_data)
            QMessageBox.information(self, "Éxito", f"Entrenamiento '{new_data['titulo']}' agregado (doc {new_id}).")
            self.load_trainings()

    # =========================
    # EDITAR ENTRENAMIENTO
    # =========================
    def edit_training(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un entrenamiento para editar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID del entrenamiento.")
            return

        snap = db.collection("Entrenamientos").document(doc_id).get()
        if not snap.exists:
            QMessageBox.warning(self, "Error", f"El documento {doc_id} no existe en 'Entrenamientos'.")
            return

        data_entrenamiento = snap.to_dict()
        form = FormularioEntrenamiento(data_entrenamiento, self.equipos_list, self.coaches_list)
        if form.exec_():
            updated_data = form.get_data()
            db.collection("Entrenamientos").document(doc_id).update(updated_data)
            QMessageBox.information(self, "Éxito", f"Entrenamiento {doc_id} actualizado.")
            self.load_trainings()

    # =========================
    # ELIMINAR ENTRENAMIENTO
    # =========================
    def delete_selected_training(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un entrenamiento para eliminar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID del entrenamiento.")
            return

        confirm = QMessageBox.question(
            self, "Eliminar Entrenamiento",
            f"¿Seguro que deseas eliminar el entrenamiento con ID {doc_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db.collection("Entrenamientos").document(doc_id).delete()
            QMessageBox.information(self, "Eliminado", "Entrenamiento eliminado correctamente.")
            self.load_trainings()

# =========================
# MAIN (PRUEBA)
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EntrenamientosWidget()
    window.show()
    sys.exit(app.exec_())
