import sys, os, unicodedata
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------------------------------------------------
#  Firebase
# ------------------------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(
        r"C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ------------------------------------------------------------------
#  Login
# ------------------------------------------------------------------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Ventana sin minimizar, pantalla completa
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint |
                            Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.showFullScreen()

        # ---------- Estilos globales ----------
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #004d99, stop:1 #0099ff);
            }
            QLineEdit {
                background:white; border:1px solid #ccc;
                border-radius:8px; padding:6px 10px;
                font-size:15px;
            }
            QLineEdit:focus { border:2px solid #0066cc; }
            QLineEdit::placeholder { color:#888; }
            QPushButton {
                background:#0056b3; color:white;
                border:none; border-radius:8px;
                padding:10px; font-size:16px;
            }
            QPushButton:hover { background:#006de0; }
        """)

        # ---------- Tarjeta central ----------
        tarjeta = QFrame()
        tarjeta.setFixedWidth(420)
        tarjeta.setStyleSheet("background:white; border-radius:18px;")
        sombra = QGraphicsDropShadowEffect(blurRadius=24, xOffset=0, yOffset=6,
                                           color=QColor(0,0,0,80))
        tarjeta.setGraphicsEffect(sombra)

        t_layout = QVBoxLayout(tarjeta)
        t_layout.setContentsMargins(40, 40, 40, 40)
        t_layout.setSpacing(22)

        # Logo
        logo = QLabel()
        pix = QPixmap(r"C:\Users\ZANCADA\Desktop\TFG\AplicacionEscritorio\images\zancadas.png")
        logo.setPixmap(pix.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        t_layout.addWidget(logo)

        # Título
        titulo = QLabel("ZANCADA FC")
        titulo.setFont(QFont("Arial", 26, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        t_layout.addWidget(titulo)

        # Slogan
        slogan = QLabel("Pasión · Esfuerzo · Victoria")
        slogan.setFont(QFont("Arial", 14, QFont.StyleItalic))
        slogan.setStyleSheet("color:#555;")
        slogan.setAlignment(Qt.AlignCenter)
        t_layout.addWidget(slogan)

        # Email
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email del club")
        t_layout.addWidget(self.email)

        # Password
        self.pwd = QLineEdit()
        self.pwd.setPlaceholderText("Contraseña")
        self.pwd.setEchoMode(QLineEdit.Password)
        t_layout.addWidget(self.pwd)

        btn = QPushButton("Iniciar Sesión")
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            background:#0056b3; color:white;
            border:none; border-radius:8px;
            font-size:16px;
        """)
        btn.clicked.connect(self.handle_login)
        t_layout.addWidget(btn)

        # Un pequeño espacio al fondo, para separar de los bordes de la tarjeta
        t_layout.addStretch(1)

        # ---------- Centrar todo ----------
        wrapper = QVBoxLayout(self)
        wrapper.addStretch(1)
        wrapper.addWidget(tarjeta, alignment=Qt.AlignHCenter)
        wrapper.addStretch(1)

    # --------------------------------------------------------------
    #  Autenticación
    # --------------------------------------------------------------
    def handle_login(self):
        from main import MainWindow  # evitas import circular

        email = self.email.text().strip()
        passwd = self.pwd.text()

        # Validación rápida
        if not email or not passwd:
            QMessageBox.warning(self, "Campos vacíos",
                                "Rellena email y contraseña.")
            return
        ok_domain = { "gmail.com", "hotmail.com", "icloud.com" }
        domain = email.split("@")[-1]
        if domain not in ok_domain:
            QMessageBox.critical(
                self, "Email inválido",
                "Solo se permiten emails de Gmail, Hotmail o iCloud.")
            return

        try:
            doc = db.collection("Usuarios").document(email).get()
            if not doc.exists:
                QMessageBox.critical(self, "Error",
                                     "Usuario no encontrado en Firestore.")
                return
            data = doc.to_dict()
            self.main = MainWindow(data.get("equipo"),
                                   data.get("nombre"),
                                   data.get("rol"),
                                   email)
            self.main.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint |
                                     Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            self.main.showFullScreen()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Firebase", str(e))

# ------------------------------------------------------------------
#  Arranque
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LoginWindow()
    sys.exit(app.exec_())
