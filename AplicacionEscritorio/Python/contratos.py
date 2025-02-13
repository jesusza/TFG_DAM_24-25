import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
import firebase_admin
from firebase_admin import credentials, firestore
from formularioContratos import FormularioContrato

# Conectar con Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

class ContratosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Contratos")
        self.setGeometry(200, 200, 900, 600)

        layout = QVBoxLayout()

        # Título
        self.title_label = QLabel("Gestión de Contratos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Tabla para mostrar contratos
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # 7 columnas incluyendo estado
        self.table.setHorizontalHeaderLabels(["Nombre", "Fecha Inicio", "Fecha Fin", "Rol", "Equipo", "Salario", "Estado"])
        self.table.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.table)

        # Botones inferiores
        buttons_layout = QHBoxLayout()
        self.add_contract_btn = QPushButton("Añadir Contrato")
        self.add_contract_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
        self.add_contract_btn.clicked.connect(self.add_contract)

        self.edit_contract_btn = QPushButton("Editar Contrato")
        self.edit_contract_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.edit_contract_btn.clicked.connect(self.edit_contract)

        self.delete_contract_btn = QPushButton("Eliminar Contrato")
        self.delete_contract_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.delete_contract_btn.clicked.connect(self.delete_selected_contract)

        buttons_layout.addWidget(self.add_contract_btn)
        buttons_layout.addWidget(self.edit_contract_btn)
        buttons_layout.addWidget(self.delete_contract_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        self.load_contracts()

    def load_contracts(self):
        """Carga los contratos desde Firebase y los muestra en la tabla."""
        self.table.setRowCount(0)
        contratos_ref = db.collection("Contratos").stream()

        for row_idx, contrato in enumerate(contratos_ref):
            contrato_data = contrato.to_dict()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(contrato_data["nombre"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(contrato_data["fecha_inicio"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(contrato_data["fecha_vencimiento"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(contrato_data["rol"]))
            self.table.setItem(row_idx, 4, QTableWidgetItem(contrato_data["equipo"]))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(contrato_data["salario_anual"])))

            # Calcular estado
            estado = self.calculate_status(contrato_data["fecha_vencimiento"])
            estado_item = QTableWidgetItem(estado)

            # Asignar color de fondo al estado
            estado_color = self.get_status_color(contrato_data["fecha_vencimiento"])
            estado_item.setBackground(estado_color)

            self.table.setItem(row_idx, 6, estado_item)

    def add_contract(self):
        """Abre el formulario para añadir un contrato."""
        formulario = FormularioContrato()
        if formulario.exec_():
            nuevo_contrato = formulario.get_data()
            db.collection("Contratos").document(nuevo_contrato["nombre"]).set(nuevo_contrato)
            self.load_contracts()
            QMessageBox.information(self, "Éxito", "Contrato añadido correctamente.")

    def edit_contract(self):
        """Edita un contrato seleccionado en la tabla."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un contrato para editar.")
            return

        nombre = self.table.item(selected_row, 0).text()
        contrato_ref = db.collection("Contratos").document(nombre)
        contrato = contrato_ref.get()

        if not contrato.exists:
            QMessageBox.warning(self, "Error", "El contrato seleccionado no existe en la base de datos.")
            return

        contrato_data = contrato.to_dict()
        formulario = FormularioContrato(contrato_data)
        if formulario.exec_():
            contrato_actualizado = formulario.get_data()
            contrato_ref.update(contrato_actualizado)
            self.load_contracts()
            QMessageBox.information(self, "Éxito", "Contrato actualizado correctamente.")

    def delete_selected_contract(self):
        """Elimina el contrato seleccionado."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un contrato para eliminar.")
            return

        nombre = self.table.item(selected_row, 0).text()
        confirm = QMessageBox.question(self, "Eliminar", f"¿Seguro que quieres eliminar {nombre}?", QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            db.collection("Contratos").document(nombre).delete()
            self.load_contracts()
            QMessageBox.information(self, "Eliminado", "Contrato eliminado correctamente.")

    def calculate_status(self, fecha_vencimiento):
        """Calcula el estado del contrato según la fecha de vencimiento."""
        if not fecha_vencimiento or fecha_vencimiento == "Desconocido":
            return "Desconocido"
        
        fecha_fin = QDate.fromString(fecha_vencimiento, "yyyy-MM-dd")
        hoy = QDate.currentDate()
        dias_restantes = hoy.daysTo(fecha_fin)
        
        if dias_restantes < 0:
            return "Vencido"
        elif dias_restantes <= 180:
            return "Menos de 6 meses"
        elif dias_restantes <= 730:
            return "Menos de 2 años"
        else:
            return "Más de 2 años"

    def get_status_color(self, fecha_vencimiento):
        """Devuelve un color de fondo según el estado del contrato."""
        status = self.calculate_status(fecha_vencimiento)
        
        colores = {
            "Vencido": QColor(255, 0, 0),  # Rojo
            "Menos de 6 meses": QColor(255, 255, 0),  # Amarillo
            "Menos de 2 años": QColor(255, 165, 0),  # Naranja
            "Más de 2 años": QColor(0, 128, 0)  # Verde
        }

        return colores.get(status, QColor(255, 255, 255))  # Blanco por defecto

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ContratosWidget()
    window.show()
    sys.exit(app.exec_())
