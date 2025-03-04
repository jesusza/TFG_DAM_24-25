import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLabel, QStackedWidget, QHBoxLayout, QInputDialog,
    QHeaderView
)
from PyQt5.QtCore import Qt
from login import db 

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
        self.table.setColumnCount(2)  # Dos columnas: Nombre del Equipo, Entrenador
        self.table.setHorizontalHeaderLabels(["Nombre del Equipo", "Entrenador"])

        # ⚙ Ajustes de estilo en la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ccc;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #0056b3;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
        """)
        # Redimensionar columnas al contenido
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # Ajustar la última columna al espacio sobrante
        self.table.horizontalHeader().setStretchLastSection(True)

        # Alinear encabezados al centro
        for col in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(col).setTextAlignment(Qt.AlignCenter)

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

            # Nombre del documento: Nombre del equipo
            self.table.setItem(row_idx, 0, QTableWidgetItem(equipo.id))
            # Entrenador
            entrenador = equipo_data.get("entrenador", "Sin asignar")
            self.table.setItem(row_idx, 1, QTableWidgetItem(entrenador))
    
    def add_team(self):
        """Añade un nuevo equipo a Firestore."""
        team_name, ok = QInputDialog.getText(self, "Nuevo Equipo", "Ingrese el nombre del equipo:")
        if ok and team_name.strip():
            entrenador, ok = QInputDialog.getText(self, "Entrenador", "Ingrese el nombre del entrenador:")
            if ok and entrenador.strip():
                db.collection("Equipos").document(team_name).set({
                    "nombre": team_name,
                    "entrenador": entrenador,
                    "jugadores": []
                })
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
                db.collection("Equipos").document(team_name).update({
                    "nombre": new_name,
                    "entrenador": new_coach
                })
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
        """Muestra los jugadores del equipo seleccionado desde la colección 'Jugadores'."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un equipo para ver sus jugadores.")
            return

        team_name = self.table.item(selected_row, 0).text()

        # Consultar la colección 'Jugadores' donde campo 'equipo' == team_name
        jugadores_ref = db.collection("Jugadores").where("equipo", "==", team_name).stream()
        nombres_jugadores = []
        for doc in jugadores_ref:
            data = doc.to_dict()
            # Si los jugadores tienen campo "nombre", lo tomamos
            nombre_jugador = data.get("nombre", doc.id)
            nombres_jugadores.append(nombre_jugador)

        if nombres_jugadores:
            msg = f"Jugadores de {team_name}:\n" + "\n".join(nombres_jugadores)
        else:
            msg = f"El equipo {team_name} no tiene jugadores registrados."

        QMessageBox.information(self, "Jugadores", msg)
