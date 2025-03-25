import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt

if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

class ResultadosWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resultados del Año")
        self.setGeometry(200, 200, 1000, 600)
        layout = QVBoxLayout()

        # Filtro
        self.combo_filtro = QComboBox()
        self.combo_filtro.addItem("Todos")
        self.combo_filtro.addItems(["Juvenil", "Cadete", "Infantil", "Alevin", "Benjamin", "Prebenjamin"])
        self.combo_filtro.currentIndexChanged.connect(self.load_resultados)
        layout.addWidget(self.combo_filtro)

        # Título
        self.title = QLabel("Resultados del Año - Todos los Partidos")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Fecha", "Hora", "Equipo Local", "Goles Local", "Goles Visitante", "Equipo Visitante", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QHeaderView::section { background-color: #0056b3; color: white; }")
        layout.addWidget(self.table)

        # Botón para gráfico
        self.btn_grafico = QPushButton("Gráfico Puntos por Categoría")
        self.btn_grafico.setStyleSheet("background-color: #0074cc; color: white; padding: 8px; border-radius: 5px;")
        self.btn_grafico.clicked.connect(self.generar_grafico)
        layout.addWidget(self.btn_grafico)

        self.setLayout(layout)
        self.load_resultados()

    def load_resultados(self):
        self.table.setRowCount(0)
        filtro_categoria = self.combo_filtro.currentText()
        partidos = list(db.collection("Calendario").stream())

        for doc in partidos:
            data = doc.to_dict()
            categoria = data.get("equipo_local", "").capitalize()
            if filtro_categoria != "Todos" and categoria != filtro_categoria:
                continue

            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(data.get("fecha", "")))
            self.table.setItem(row_pos, 1, QTableWidgetItem(data.get("hora", "")))
            self.table.setItem(row_pos, 2, QTableWidgetItem(data.get("equipo_local", "")))
            self.table.setItem(row_pos, 3, QTableWidgetItem(str(data.get("goles_local", 0))))
            self.table.setItem(row_pos, 4, QTableWidgetItem(str(data.get("goles_visitante", 0))))
            self.table.setItem(row_pos, 5, QTableWidgetItem(data.get("equipo_visitante", "")))
            self.table.setItem(row_pos, 6, QTableWidgetItem(data.get("estado", "")))

        self.actualizar_clasificacion(partidos)

    def actualizar_clasificacion(self, partidos):
        clasificacion = {}

        for doc in partidos:
            data = doc.to_dict()
            if data.get("estado") != "Finalizado":
                continue

            categoria = data.get("equipo_local", "").capitalize()
            goles_local = int(data.get("goles_local", 0))
            goles_visitante = int(data.get("goles_visitante", 0))

            if categoria not in clasificacion:
                clasificacion[categoria] = {
                    "categoria": categoria,
                    "puntos": 0,
                    "partidos_ganados": 0,
                    "partidos_perdidos": 0,
                    "partidos_empatados": 0,
                    "goles_favor": 0,
                    "goles_contra": 0
                }

            clasificacion[categoria]["goles_favor"] += goles_local
            clasificacion[categoria]["goles_contra"] += goles_visitante

            if goles_local > goles_visitante:
                clasificacion[categoria]["puntos"] += 3
                clasificacion[categoria]["partidos_ganados"] += 1
            elif goles_local == goles_visitante:
                clasificacion[categoria]["puntos"] += 1
                clasificacion[categoria]["partidos_empatados"] += 1
            else:
                clasificacion[categoria]["partidos_perdidos"] += 1

        # Guardar en Firebase
        for cat, datos in clasificacion.items():
            doc_ref = db.collection("Clasificacion").document(cat)
            doc_ref.set(datos, merge=True)

    def generar_grafico(self):
        docs = db.collection("Clasificacion").stream()
        categorias = []
        puntos = []

        for doc in docs:
            data = doc.to_dict()
            categorias.append(data.get("categoria", doc.id))
            puntos.append(int(data.get("puntos", 0)))

        if not categorias:
            QMessageBox.information(self, "Sin datos", "No hay datos de clasificación.")
            return

        import numpy as np
        x = np.arange(len(categorias))
        plt.figure(figsize=(8, 5))
        plt.bar(x, puntos, color="green")
        plt.xticks(x, categorias)
        plt.title("Clasificación por Puntos - Club")
        plt.xlabel("Categoría")
        plt.ylabel("Puntos")
        plt.tight_layout()
        plt.show()

