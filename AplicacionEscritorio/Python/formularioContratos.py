import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QDateEdit
from PyQt5.QtCore import QDate

class FormularioContrato(QDialog):
    def __init__(self, contrato=None):
        super().__init__()
        self.setWindowTitle("Formulario de Contrato")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        # Campos del formulario
        self.nombre_label = QLabel("Nombre:")
        self.nombre_input = QLineEdit(contrato["nombre"] if contrato else "")
        layout.addWidget(self.nombre_label)
        layout.addWidget(self.nombre_input)

        self.fecha_inicio_label = QLabel("Fecha Inicio:")
        self.fecha_inicio_input = QDateEdit(QDate.fromString(contrato["fecha_inicio"], "yyyy-MM-dd") if contrato else QDate.currentDate())
        self.fecha_inicio_input.setCalendarPopup(True)
        layout.addWidget(self.fecha_inicio_label)
        layout.addWidget(self.fecha_inicio_input)

        self.fecha_fin_label = QLabel("Fecha Fin:")
        self.fecha_fin_input = QDateEdit(QDate.fromString(contrato["fecha_vencimiento"], "yyyy-MM-dd") if contrato else QDate.currentDate())
        self.fecha_fin_input.setCalendarPopup(True)
        layout.addWidget(self.fecha_fin_label)
        layout.addWidget(self.fecha_fin_input)

        self.rol_label = QLabel("Rol:")
        self.rol_input = QLineEdit(contrato["rol"] if contrato else "")
        layout.addWidget(self.rol_label)
        layout.addWidget(self.rol_input)

        self.equipo_label = QLabel("Equipo:")
        self.equipo_input = QLineEdit(contrato["equipo"] if contrato else "")
        layout.addWidget(self.equipo_label)
        layout.addWidget(self.equipo_input)

        self.salario_label = QLabel("Salario:")
        self.salario_input = QLineEdit(str(contrato["salario_anual"]) if contrato else "")
        layout.addWidget(self.salario_label)
        layout.addWidget(self.salario_input)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            "nombre": self.nombre_input.text(),
            "fecha_inicio": self.fecha_inicio_input.date().toString("yyyy-MM-dd"),
            "fecha_vencimiento": self.fecha_fin_input.date().toString("yyyy-MM-dd"),
            "rol": self.rol_input.text(),
            "equipo": self.equipo_input.text(),
            "salario_anual": self.salario_input.text()
        }
