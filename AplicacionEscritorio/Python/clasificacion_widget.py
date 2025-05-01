import sys, unicodedata
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------------------------------------------------
#  Firebase
# ------------------------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(
        r"C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/"
        r"gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ------------------------------------------------------------------
#  Categorías y utilidades
# ------------------------------------------------------------------
CATEGORIAS_BASE = {
    "aficionado":  "Aficionado",
    "juvenil":     "Juvenil",
    "cadete":      "Cadete",
    "infantil":    "Infantil",
    "alevin":      "Alevin",
    "benjamin":    "Benjamin",
    "prebenjamin": "Prebenjamin",
}
STRIP_CHARS = str.maketrans("", "", " -_.")

def sin_acentos(txt: str) -> str:
    nfkd = unicodedata.normalize("NFKD", txt)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().translate(STRIP_CHARS)

def detectar_categoria(nombre_equipo: str) -> str | None:
    norm = sin_acentos(nombre_equipo)
    for clave, categoria in CATEGORIAS_BASE.items():
        if clave in norm:
            return categoria
    return None

# ------------------------------------------------------------------
#  Widget de Clasificación
# ------------------------------------------------------------------
class ClasificacionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clasificación por Categorías")
        self.setGeometry(300, 200, 900, 520)

        layout = QVBoxLayout(self)

        # título
        titulo = QLabel("Clasificación del Club")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:18px;font-weight:bold;")
        layout.addWidget(titulo)

        # filtro
        self.cbo = QComboBox()
        self.cbo.addItem("Todas")
        self.cbo.addItems(CATEGORIAS_BASE.values())
        self.cbo.currentIndexChanged.connect(self.load_table)
        layout.addWidget(self.cbo)

        # botones
        btn_calc = QPushButton("Calcular Clasificación")
        btn_calc.setStyleSheet("background:#0074cc;color:white;padding:8px;")
        btn_calc.clicked.connect(self.calcular_clasificacion)
        layout.addWidget(btn_calc)

        btn_graph = QPushButton("Ver Gráfico de Clasificación")
        btn_graph.setStyleSheet("background:#4CAF50;color:white;padding:8px;")
        btn_graph.clicked.connect(self.show_graph)
        layout.addWidget(btn_graph)

        # tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Categoría", "Puntos", "Jugados", "Ganados", "Empatados", "Perdidos"]
        )
        layout.addWidget(self.table)

        self.load_table()

    # --------------------------------------------------------------
    #  Cálculo y guardado
    # --------------------------------------------------------------
    def calcular_clasificacion(self):
        stats = {v: {"puntos": 0, "jugados": 0,
                     "ganados": 0, "empatados": 0, "perdidos": 0}
                 for v in CATEGORIAS_BASE.values()}

        partidos = (db.collection("Calendario")
                      .where("estado", "==", "Finalizado")
                      .stream())

        for doc in partidos:
            p = doc.to_dict()

            # datos del partido
            loc_name = p.get("equipo_local", "")
            vis_name = p.get("equipo_visitante", "")
            gl = int(p.get("goles_local") or 0)
            gv = int(p.get("goles_visitante") or 0)

            cat_loc = detectar_categoria(loc_name)
            cat_vis = detectar_categoria(vis_name)

            # ------- local -------
            if cat_loc:
                s = stats[cat_loc]
                s["jugados"] += 1
                if gl > gv:
                    s["ganados"] += 1;  s["puntos"] += 3
                elif gl == gv:
                    s["empatados"] += 1;  s["puntos"] += 1
                else:
                    s["perdidos"] += 1

            # ------- visitante -------
            if cat_vis:
                s = stats[cat_vis]
                s["jugados"] += 1
                if gv > gl:
                    s["ganados"] += 1;  s["puntos"] += 3
                elif gv == gl:
                    s["empatados"] += 1;  s["puntos"] += 1
                else:
                    s["perdidos"] += 1

        # guardar en la colección Clasificacion
        for cat, st in stats.items():
            db.collection("Clasificacion").document(cat).set(st)

        QMessageBox.information(self, "Éxito",
                                "Clasificación actualizada correctamente.")
        self.load_table()

    # --------------------------------------------------------------
    #  Tabla
    # --------------------------------------------------------------
    def load_table(self):
        self.table.setRowCount(0)
        filtro = self.cbo.currentText()

        for doc in db.collection("Clasificacion").stream():
            cat = doc.id
            if filtro != "Todas" and cat != filtro:
                continue
            st = doc.to_dict()
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(cat))
            self.table.setItem(r, 1, QTableWidgetItem(str(st.get("puntos", 0))))
            self.table.setItem(r, 2, QTableWidgetItem(str(st.get("jugados", 0))))
            self.table.setItem(r, 3, QTableWidgetItem(str(st.get("ganados", 0))))
            self.table.setItem(r, 4, QTableWidgetItem(str(st.get("empatados", 0))))
            self.table.setItem(r, 5, QTableWidgetItem(str(st.get("perdidos", 0))))

    # --------------------------------------------------------------
    #  Gráfico de puntos
    # --------------------------------------------------------------
    def show_graph(self):
        cats, puntos = [], []
        for doc in db.collection("Clasificacion").stream():
            cats.append(doc.id)
            puntos.append(doc.to_dict().get("puntos", 0))

        if not cats:
            QMessageBox.warning(self, "Sin datos", "No hay datos para mostrar.")
            return

        import numpy as np
        x = np.arange(len(cats))
        plt.figure(figsize=(8, 5))
        plt.bar(x, puntos, color="#0056b3")
        plt.xticks(x, cats)
        plt.ylabel("Puntos")
        plt.title("Clasificación General por Categoría")
        plt.tight_layout()
        plt.show()

# ------------------------------------------------------------------
#  Arranque independiente de prueba
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ClasificacionWidget()
    w.show()
    sys.exit(app.exec_())