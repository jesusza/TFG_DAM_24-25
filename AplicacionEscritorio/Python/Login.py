import sys
import os
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, auth, firestore
from PyQt5.QtGui import QPixmap

# Verificar si Firebase ya está inicializado antes de hacerlo
if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join("C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python", "gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"))
    firebase_admin.initialize_app(cred)

# Cliente Firestore (debe inicializarse después de la verificación)
db = firestore.client()

class LoginWindow(QWidget):
    def __init__(self, login_success_callback):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión - CRM")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: white;")
        self.setMinimumSize(600, 500)
        
        self.login_success_callback = login_success_callback

        layout = QVBoxLayout()

        # Logo
        self.logo = QLabel(self)

        image_path = os.path.abspath("images/zancadacrm.png")
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"Error: No se pudo cargar la imagen en {image_path}")

        self.logo.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)

        # Título
        self.title = QLabel("Bienvenido a ZANCADA FC")
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Campo de usuario
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su email")
        layout.addWidget(self.username_input)

        # Campo de contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Botón de inicio de sesión
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("background-color: #0056b3; color: white; padding: 10px; border-radius: 5px;")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)

    def handle_login(self):
        from main import MainWindow  # Importación diferida
        
        email = self.username_input.text().strip()
        password = self.password_input.text()

        # Validación de dominio de email
        allowed_domains = ["gmail.com", "hotmail.com", "icloud.com"]
        email_domain = email.split("@")[1] if "@" in email else ""
        if email_domain not in allowed_domains:
            QMessageBox.critical(self, "Error", "Solo se permiten emails de Gmail, Hotmail o iCloud.")
            return
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos.")
            return

        try:
            # Buscar en Firestore usando el email como ID
            user_data = db.collection("Usuarios").document(email).get()
            if user_data.exists:
                data = user_data.to_dict()
                role = data.get("rol")  # Obtener el rol directamente desde Firestore
                QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                self.main_window = MainWindow(data.get("equipo"), data.get("nombre"), role, email)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.critical(self, "Error", f"Usuario '{email}' no encontrado en Firestore.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en Firebase: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow(lambda team, name, role, email: print(f"Login exitoso: {email} ({role}, {team})"))
    window.show()
    sys.exit(app.exec_())
