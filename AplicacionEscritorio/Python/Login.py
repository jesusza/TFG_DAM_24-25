import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import firebase_admin
from firebase_admin import credentials, auth, firestore
from main import MainWindow  # Importar la ventana principal

# Inicializar Firebase
cred = credentials.Certificate(os.path.join("C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python", "gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"))
firebase_admin.initialize_app(cred)
db = firestore.client()

class LoginWindow(QWidget):
    def __init__(self, login_success_callback, register_callback):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión - CRM")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: white;")
        self.setMinimumSize(600, 500)  # Redimensionable
        
        self.login_success_callback = login_success_callback
        self.register_callback = register_callback

        layout = QVBoxLayout()

        # Contenedor del logo y título
        header_layout = QVBoxLayout()

        # Logo
        self.logo = QLabel(self)
        pixmap = QPixmap("images/zancadacrm.png")
        self.logo.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.logo)

        # Título
        self.title = QLabel("Bienvenido a ZANCADA FC")
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title)

        layout.addLayout(header_layout)

        # Campo de equipo
        self.team_label = QLabel("Equipo:")
        layout.addWidget(self.team_label)
        self.team_input = QLineEdit()
        self.team_input.setPlaceholderText("Ingrese el nombre de su equipo")
        layout.addWidget(self.team_input)

        # Campo de usuario
        self.username_label = QLabel("Correo Electrónico:")
        layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingrese su email")
        layout.addWidget(self.username_input)

        # Campo de contraseña
        self.password_label = QLabel("Contraseña:")
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Selección de rol
        self.role_label = QLabel("Rol:")
        layout.addWidget(self.role_label)
        self.role_input = QComboBox()
        self.role_input.addItems(["Jugador", "Entrenador","Directivo"])
        layout.addWidget(self.role_input)

        # Contenedor de botones
        button_layout = QHBoxLayout()

        # Botón de inicio de sesión
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("background-color: #0056b3; color: white; padding: 10px; border-radius: 5px;")
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)

        # Botón de registro
        self.register_button = QPushButton("Registrar Empresa")
        self.register_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px; border-radius: 5px;")
        self.register_button.clicked.connect(self.handle_register)
        button_layout.addWidget(self.register_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def handle_login(self):
        team = self.team_input.text()
        email = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()
        
        if not team or not email or not password:
            QMessageBox.warning(self, "Error", "Por favor, complete todos los campos.")
            return

        try:
            user = auth.get_user_by_email(email)
            user_data = db.collection("Usuarios").document(user.uid).get()
            if user_data.exists:
                data = user_data.to_dict()
                if data.get("rol") == role and data.get("equipo") == team:
                    QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                    
                    # Cerrar login y abrir la ventana principal
                    self.main_window = MainWindow(team, role, email)
                    self.main_window.show()
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "Rol o equipo incorrecto.")
            else:
                QMessageBox.critical(self, "Error", "Usuario no encontrado en la base de datos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar sesión: {str(e)}")

    def handle_register(self):
        self.register_callback()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow(lambda user, role, team: print(f"Login exitoso: {user} ({role}, {team})"), lambda: print("Registro"))
    window.show()
    sys.exit(app.exec_())
