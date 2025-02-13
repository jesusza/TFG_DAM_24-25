import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QStackedWidget, QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt
from login import db  # Importamos db desde login.py

class EquiposWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Equipos")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        # Título
        self.title_label = QLabel("Gestión de Equipos")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Tabla para mostrar equipos
        self.table = QTableWidget()
        self.table.setColumnCount(2)  # Ahora tiene dos columnas: Nombre del Equipo y Entrenador
        self.table.setHorizontalHeaderLabels(["Nombre del Equipo", "Entrenador"])
        layout.addWidget(self.table)

        # Botones inferiores
        buttons_layout = QHBoxLayout()
        self.add_team_btn = QPushButton("Añadir Equipo")
        self.add_team_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
        self.add_team_btn.clicked.connect(self.add_team)

        self.edit_team_btn = QPushButton("Editar Equipo")
        self.edit_team_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.edit_team_btn.clicked.connect(self.edit_team)

        self.delete_team_btn = QPushButton("Eliminar Equipo")
        self.delete_team_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.delete_team_btn.clicked.connect(self.delete_selected_team)
        
        self.view_players_btn = QPushButton("Ver Jugadores")
        self.view_players_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; border-radius: 5px;")
        self.view_players_btn.clicked.connect(self.view_players)
        
        buttons_layout.addWidget(self.add_team_btn)
        buttons_layout.addWidget(self.edit_team_btn)
        buttons_layout.addWidget(self.delete_team_btn)
        buttons_layout.addWidget(self.view_players_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        self.load_teams()

    def load_teams(self):
        """Carga los equipos desde Firebase y los muestra en la tabla."""
        self.table.setRowCount(0)
        equipos_ref = db.collection("Equipos").stream()
        
        for row_idx, equipo in enumerate(equipos_ref):
            equipo_data = equipo.to_dict()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(equipo.id))
            self.table.setItem(row_idx, 1, QTableWidgetItem(equipo_data.get("entrenador", "Sin asignar")))
    
    def add_team(self):
        """Añade un nuevo equipo a Firestore."""
        from PyQt5.QtWidgets import QInputDialog
        team_name, ok = QInputDialog.getText(self, "Nuevo Equipo", "Ingrese el nombre del equipo:")
        if ok and team_name.strip():
            entrenador, ok = QInputDialog.getText(self, "Entrenador", "Ingrese el nombre del entrenador:")
            if ok and entrenador.strip():
                db.collection("Equipos").document(team_name).set({"nombre": team_name, "entrenador": entrenador, "jugadores": []})
                self.load_teams()
                QMessageBox.information(self, "Éxito", "Equipo añadido correctamente.")
            else:
                QMessageBox.warning(self, "Error", "Debe ingresar un nombre de entrenador válido.")
        else:
            QMessageBox.warning(self, "Error", "Debe ingresar un nombre de equipo válido.")
    
    def edit_team(self):
        """Edita un equipo seleccionado en la tabla."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un equipo para editar.")
            return
        team_name = self.table.item(selected_row, 0).text()
        new_name, ok = QInputDialog.getText(self, "Editar Equipo", "Nuevo nombre del equipo:")
        if ok and new_name.strip():
            new_coach, ok = QInputDialog.getText(self, "Editar Entrenador", "Nuevo nombre del entrenador:")
            if ok and new_coach.strip():
                db.collection("Equipos").document(team_name).update({"nombre": new_name, "entrenador": new_coach})
                self.load_teams()
                QMessageBox.information(self, "Éxito", "Equipo actualizado correctamente.")
    
    def delete_selected_team(self):
        """Elimina el equipo seleccionado."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un equipo para eliminar.")
            return
        team_name = self.table.item(selected_row, 0).text()
        confirm = QMessageBox.question(self, "Eliminar", f"¿Seguro que quieres eliminar {team_name}?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            db.collection("Equipos").document(team_name).delete()
            self.load_teams()
            QMessageBox.information(self, "Eliminado", "Equipo eliminado correctamente.")

    def view_players(self):
        """Muestra los jugadores del equipo seleccionado."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un equipo para ver sus jugadores.")
            return
        team_name = self.table.item(selected_row, 0).text()
        equipo_doc = db.collection("Equipos").document(team_name).get()
        
        if equipo_doc.exists:
            equipo_data = equipo_doc.to_dict()
            jugadores = equipo_data.get("jugadores", [])
            QMessageBox.information(self, "Jugadores", f"Jugadores de {team_name}:\n" + "\n".join(jugadores))
        else:
            QMessageBox.warning(self, "Error", "No se encontraron jugadores para este equipo.")
