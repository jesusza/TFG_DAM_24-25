import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt

# Inicialización de Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

class ClasificacionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clasificación por Categorías")
        self.setGeometry(300, 200, 900, 500)

        self.layout = QVBoxLayout()

        # Título
        self.title_label = QLabel("Clasificación del Club")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Filtro por categoría
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(["Todas", "Juvenil", "Cadete", "Infantil", "Alevín", "Benjamín", "Prebenjamín"])
        self.categoria_combo.currentIndexChanged.connect(self.load_table)
        self.layout.addWidget(self.categoria_combo)

        # Botón para calcular clasificación
        self.calcular_btn = QPushButton("Calcular Clasificación")
        self.calcular_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px;")
        self.calcular_btn.clicked.connect(self.calcular_clasificacion)
        self.layout.addWidget(self.calcular_btn)

        # Botón para mostrar gráfico general
        self.graph_btn = QPushButton("Ver Gráfico de Clasificación")
        self.graph_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.graph_btn.clicked.connect(self.show_graph)
        self.layout.addWidget(self.graph_btn)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Categoría", "Puntos", "Jugados", "Ganados", "Empatados", "Perdidos"])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.load_table()

    def calcular_clasificacion(self):
        categorias = ["Juvenil", "Cadete", "Infantil", "Alevín", "Benjamín", "Prebenjamín"]
        clasificacion = {cat: {"puntos": 0, "jugados": 0, "ganados": 0, "empatados": 0, "perdidos": 0} for cat in categorias}

        partidos_ref = db.collection("Calendario").stream()

        for doc in partidos_ref:
            data = doc.to_dict()
            categoria = data.get("equipo_local", "")
            estado = data.get("estado", "")
            if categoria not in categorias or estado.lower() != "finalizado":
                continue

            goles_local = int(data.get("goles_local", 0))
            goles_visitante = int(data.get("goles_visitante", 0))

            clasificacion[categoria]["jugados"] += 1

            if goles_local > goles_visitante:
                clasificacion[categoria]["puntos"] += 3
                clasificacion[categoria]["ganados"] += 1
            elif goles_local == goles_visitante:
                clasificacion[categoria]["puntos"] += 1
                clasificacion[categoria]["empatados"] += 1
            else:
                clasificacion[categoria]["perdidos"] += 1

        # Guardar en colección Clasificacion
        for cat, stats in clasificacion.items():
            db.collection("Clasificacion").document(cat).set(stats)

        QMessageBox.information(self, "Éxito", "Clasificación actualizada correctamente.")
        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        selected_cat = self.categoria_combo.currentText()

        docs = db.collection("Clasificacion").stream()
        row = 0
        for doc in docs:
            cat = doc.id
            data = doc.to_dict()

            if selected_cat != "Todas" and cat != selected_cat:
                continue

            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(cat))
            self.table.setItem(row, 1, QTableWidgetItem(str(data.get("puntos", 0))))
            self.table.setItem(row, 2, QTableWidgetItem(str(data.get("jugados", 0))))
            self.table.setItem(row, 3, QTableWidgetItem(str(data.get("ganados", 0))))
            self.table.setItem(row, 4, QTableWidgetItem(str(data.get("empatados", 0))))
            self.table.setItem(row, 5, QTableWidgetItem(str(data.get("perdidos", 0))))
            row += 1

    def show_graph(self):
        docs = db.collection("Clasificacion").stream()
        categorias = []
        puntos = []

        for doc in docs:
            categorias.append(doc.id)
            puntos.append(doc.to_dict().get("puntos", 0))

        if not categorias:
            QMessageBox.warning(self, "Sin datos", "No hay datos para mostrar.")
            return

        import numpy as np
        x = np.arange(len(categorias))
        plt.figure(figsize=(8, 5))
        plt.bar(x, puntos, color='blue')
        plt.xticks(x, categorias)
        plt.ylabel("Puntos")
        plt.title("Clasificación General por Categoría")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClasificacionWidget()
    window.show()
    sys.exit(app.exec_())
