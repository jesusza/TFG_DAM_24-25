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
# FORMULARIO DE INGRESO
# ========================
class FormularioIngreso(QDialog):
    def __init__(self, ingreso_data=None):
        super().__init__()
        self.setWindowTitle("Formulario de Ingreso")
        self.setGeometry(300, 300, 400, 300)

        self.ingreso_data = ingreso_data or {}
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos
        self.fecha_input = QLineEdit(self.ingreso_data.get("fecha", ""))
        self.equipo_local_input = QLineEdit(self.ingreso_data.get("equipo_local", ""))
        self.equipo_visitante_input = QLineEdit(self.ingreso_data.get("equipo_visitante", ""))
        self.ingresos_bar_input = QLineEdit(str(self.ingreso_data.get("ingresos_bar", 0)))
        self.ingresos_entradas_input = QLineEdit(str(self.ingreso_data.get("ingresos_entradas", 0)))

        form_layout.addRow("Fecha (YYYY-MM-DD):", self.fecha_input)
        form_layout.addRow("Equipo Local:", self.equipo_local_input)
        form_layout.addRow("Equipo Visitante:", self.equipo_visitante_input)
        form_layout.addRow("Ingresos Bar:", self.ingresos_bar_input)
        form_layout.addRow("Ingresos Entradas:", self.ingresos_entradas_input)

        layout.addLayout(form_layout)

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
            "fecha": self.fecha_input.text().strip(),
            "equipo_local": self.equipo_local_input.text().strip(),
            "equipo_visitante": self.equipo_visitante_input.text().strip(),
            "ingresos_bar": int(self.ingresos_bar_input.text() or 0),
            "ingresos_entradas": int(self.ingresos_entradas_input.text() or 0)
        }

# ========================
# WIDGET PRINCIPAL
# ========================
class IngresosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Ingresos")
        self.setGeometry(200, 200, 900, 600)

        self.row_to_doc_id = {}

        layout = QVBoxLayout()

        self.title_label = QLabel("Gestión de Ingresos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filtro por equipo (ComboBox)
        self.equipo_selector = QComboBox()
        self.equipo_selector.currentIndexChanged.connect(self.load_incomes)
        layout.addWidget(self.equipo_selector)

        # Tabla estilizada
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Equipo Local", "Equipo Visitante",
            "Ingresos Bar", "Ingresos Entradas", "Ingreso Total"
        ])
        self.table.setAlternatingRowColors(True)  # Filas alternadas
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
        # Ajuste de columnas
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Alinear encabezados al centro
        for col in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(col).setTextAlignment(Qt.AlignCenter)

        layout.addWidget(self.table)

        # Botones inferiores
        buttons_layout = QHBoxLayout()

        self.add_income_btn = QPushButton("Añadir Ingreso")
        self.add_income_btn.setStyleSheet(
            "background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;"
        )
        self.add_income_btn.clicked.connect(self.add_income)

        self.edit_income_btn = QPushButton("Editar Ingreso")
        self.edit_income_btn.setStyleSheet(
            "background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;"
        )
        self.edit_income_btn.clicked.connect(self.edit_income)

        self.delete_income_btn = QPushButton("Eliminar Ingreso")
        self.delete_income_btn.setStyleSheet(
            "background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;"
        )
        self.delete_income_btn.clicked.connect(self.delete_selected_income)

        self.graph_income_btn = QPushButton("Ver Gráfico")
        self.graph_income_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;"
        )
        self.graph_income_btn.clicked.connect(self.show_graph)

        buttons_layout.addWidget(self.add_income_btn)
        buttons_layout.addWidget(self.edit_income_btn)
        buttons_layout.addWidget(self.delete_income_btn)
        buttons_layout.addWidget(self.graph_income_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.load_teams()
        self.load_incomes()

    # ========================
    # Cargar equipos
    # ========================
    def load_teams(self):
        self.equipo_selector.clear()
        self.equipo_selector.addItem("Todos")
        equipos_ref = db.collection("Equipos").stream()
        for eq in equipos_ref:
            data = eq.to_dict()
            nombre_equipo = data.get("nombre", eq.id)
            self.equipo_selector.addItem(nombre_equipo)

    # ========================
    # Cargar Ingresos
    # ========================
    def load_incomes(self, index=None):
        """Carga ingresos de Firestore y muestra en la tabla con estilo."""
        self.table.setRowCount(0)
        self.row_to_doc_id.clear()

        equipo_filtro = self.equipo_selector.currentText()
        ingresos_ref = db.collection("Ingresos").stream()

        current_row = 0
        for doc in ingresos_ref:
            ingreso_data = doc.to_dict()
            if "fecha" not in ingreso_data:
                continue

            if equipo_filtro != "Todos" and ingreso_data.get("equipo_local", "") != equipo_filtro:
                continue

            fecha_str = ingreso_data["fecha"]
            equipo_local = ingreso_data.get("equipo_local", "Desconocido")
            equipo_visitante = ingreso_data.get("equipo_visitante", "Desconocido")
            bar = int(ingreso_data.get("ingresos_bar", 0))
            entradas = int(ingreso_data.get("ingresos_entradas", 0))
            total = bar + entradas

            # Guardar el doc.id para editar/eliminar
            self.row_to_doc_id[current_row] = doc.id

            # Insertar fila
            self.table.insertRow(current_row)
            self.table.setItem(current_row, 0, QTableWidgetItem(fecha_str))
            self.table.setItem(current_row, 1, QTableWidgetItem(equipo_local))
            self.table.setItem(current_row, 2, QTableWidgetItem(equipo_visitante))

            item_bar = QTableWidgetItem(str(bar))
            item_bar.setBackground(Qt.darkYellow)
            self.table.setItem(current_row, 3, item_bar)

            item_entradas = QTableWidgetItem(str(entradas))
            item_entradas.setBackground(Qt.blue)
            self.table.setItem(current_row, 4, item_entradas)

            item_total = QTableWidgetItem(str(total))
            item_total.setBackground(Qt.green)
            self.table.setItem(current_row, 5, item_total)

            current_row += 1
    # ========================
    # Añadir Ingreso
    # ========================
    def add_income(self):
        formulario = FormularioIngreso()
        if formulario.exec_():
            data = formulario.get_data()
            db.collection("Ingresos").add(data)
            QMessageBox.information(self, "Éxito", "Ingreso añadido correctamente.")
            self.load_incomes()

    # ========================
    # Editar Ingreso
    # ========================
    def edit_income(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un ingreso para editar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró la referencia del documento.")
            return

        ref_doc = db.collection("Ingresos").document(doc_id).get()
        if not ref_doc.exists:
            QMessageBox.warning(self, "Error", "El ingreso seleccionado no existe en la base de datos.")
            return

        data = ref_doc.to_dict()
        formulario = FormularioIngreso(data)
        if formulario.exec_():
            nuevo_data = formulario.get_data()
            db.collection("Ingresos").document(doc_id).update(nuevo_data)
            QMessageBox.information(self, "Éxito", "Ingreso actualizado correctamente.")
            self.load_incomes()

    # ========================
    # Eliminar Ingreso
    # ========================
    def delete_selected_income(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un ingreso para eliminar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró la referencia del documento.")
            return

        confirm = QMessageBox.question(
            self, "Eliminar", "¿Seguro que quieres eliminar este ingreso?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db.collection("Ingresos").document(doc_id).delete()
            QMessageBox.information(self, "Eliminado", "Ingreso eliminado correctamente.")
            self.load_incomes()

    # ========================
    # Mostrar Gráfico
    # ========================
    def show_graph(self):
        equipo_filtro = self.equipo_selector.currentText()
        ingresos_ref = db.collection("Ingresos").stream()

        labels = []
        bars = []
        entradas = []
        totales = []

        for doc in ingresos_ref:
            data = doc.to_dict()
            if "fecha" not in data:
                continue

            if equipo_filtro != "Todos" and data.get("equipo_local", "") != equipo_filtro:
                continue

            fecha = data["fecha"]
            eq_local = data.get("equipo_local", "")
            label_x = f"{fecha}\n{eq_local}"

            bar_val = int(data.get("ingresos_bar", 0))
            entradas_val = int(data.get("ingresos_entradas", 0))
            total_val = bar_val + entradas_val

            labels.append(label_x)
            bars.append(bar_val)
            entradas.append(entradas_val)
            totales.append(total_val)

        if not labels:
            QMessageBox.warning(self, "Sin Datos", "No hay datos para graficar con este filtro.")
            return

        import numpy as np
        x = np.arange(len(labels))
        width = 0.3

        plt.figure(figsize=(10, 5))

        # Barras lado a lado
        plt.bar(x - width, bars, width=width, color="orange", label="Ingresos Bar")
        plt.bar(x, entradas, width=width, color="blue", label="Ingresos Entradas")
        plt.bar(x + width, totales, width=width, color="green", alpha=0.7, label="Total Ingresos")

        plt.xticks(x, labels, rotation=45)
        plt.xlabel("Fecha y Equipo Local")
        plt.ylabel("Ingresos (€)")
        if equipo_filtro == "Todos":
            plt.title("Ingresos por Partido (Todos los equipos)")
        else:
            plt.title(f"Ingresos por Partido - {equipo_filtro}")
        plt.legend()
        plt.tight_layout()
        plt.show()

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IngresosWidget()
    window.show()
    sys.exit(app.exec_())
