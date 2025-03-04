import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QDialog, QFormLayout, QLineEdit, QHeaderView, QSpinBox, QInputDialog
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# CONFIGURACIÓN DE FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "C:/Users/ZANCADA/Desktop/TFG/AplicacionEscritorio/Python/gestion-club-futbol-firebase-adminsdk-fbsvc-c4fe34cec8.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# FORMULARIO PRODUCTO
# =========================
class FormularioProducto(QDialog):
    """
    Formulario para crear/editar un producto en la colección 'Inventario'.
    Campos: nombre, categoria, precio, cantidad, [unidades_vendidas opcional].
    """
    def __init__(self, producto_data=None):
        super().__init__()
        self.setWindowTitle("Formulario de Producto")
        self.setGeometry(300, 300, 400, 300)

        self.producto_data = producto_data or {}
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos
        self.nombre_input = QLineEdit(self.producto_data.get("nombre", ""))
        self.categoria_input = QLineEdit(self.producto_data.get("categoria", ""))
        self.precio_input = QLineEdit(str(self.producto_data.get("precio", 0.0)))
        self.cantidad_input = QLineEdit(str(self.producto_data.get("cantidad", 0)))
        # Opcional: 'unidades_vendidas'
        self.vendidas_input = QLineEdit(str(self.producto_data.get("unidades_vendidas", 0)))

        form_layout.addRow("Nombre:", self.nombre_input)
        form_layout.addRow("Categoría:", self.categoria_input)
        form_layout.addRow("Precio:", self.precio_input)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        form_layout.addRow("Unidades Vendidas:", self.vendidas_input)

        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        """Retorna los datos del producto en un diccionario."""
        return {
            "nombre": self.nombre_input.text().strip(),
            "categoria": self.categoria_input.text().strip(),
            "precio": float(self.precio_input.text() or 0.0),
            "cantidad": int(self.cantidad_input.text() or 0),
            "unidades_vendidas": int(self.vendidas_input.text() or 0)
        }

# =========================
# WIDGET PRINCIPAL: InventarioWidget
# =========================
class InventarioWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Inventario")
        self.setGeometry(200, 200, 1100, 600)

        # Diccionario fila->docID
        self.row_to_doc_id = {}

        layout = QVBoxLayout()

        self.title_label = QLabel("Gestión de Inventario")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Filtros (búsqueda por nombre, y filtro min_cantidad)
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre de producto...")
        self.search_input.textChanged.connect(self.load_products)
        filter_layout.addWidget(self.search_input)

        self.min_cantidad_input = QLineEdit()
        self.min_cantidad_input.setPlaceholderText("Cantidad mínima...")
        self.min_cantidad_input.textChanged.connect(self.load_products)
        filter_layout.addWidget(self.min_cantidad_input)

        layout.addLayout(filter_layout)

        # Tabla: docID, nombre, categoria, precio, cantidad, unidades_vendidas
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "DocID", "Nombre", "Categoría", "Precio", "Cantidad", "Vendidas"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #0056b3;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        for col in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(col).setTextAlignment(Qt.AlignCenter)

        layout.addWidget(self.table)

        # Botones inferiores
        buttons_layout = QHBoxLayout()

        self.add_product_btn = QPushButton("Añadir Producto")
        self.add_product_btn.setStyleSheet("background-color: #0074cc; color: white; padding: 10px; border-radius: 5px;")
        self.add_product_btn.clicked.connect(self.add_product)

        self.edit_product_btn = QPushButton("Editar Producto")
        self.edit_product_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.edit_product_btn.clicked.connect(self.edit_product)

        self.sell_btn = QPushButton("Realizar Venta")
        self.sell_btn.setStyleSheet("background-color: #FFA500; color: white; padding: 10px; border-radius: 5px;")
        self.sell_btn.clicked.connect(self.sell_product)

        self.delete_product_btn = QPushButton("Eliminar Producto")
        self.delete_product_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 10px; border-radius: 5px;")
        self.delete_product_btn.clicked.connect(self.delete_selected_product)

        # Botones de gráficos
        self.graph_stock_btn = QPushButton("Gráfico +Stock")
        self.graph_stock_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.graph_stock_btn.clicked.connect(self.show_graph_stock)

        self.graph_sold_btn = QPushButton("Gráfico +Vendidos")
        self.graph_sold_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.graph_sold_btn.clicked.connect(self.show_graph_sold)

        self.graph_entradas_btn = QPushButton("Gráfico Entradas")
        self.graph_entradas_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.graph_entradas_btn.clicked.connect(self.show_graph_entradas)

        self.graph_ingresos_btn = QPushButton("Gráfico Ingresos")
        self.graph_ingresos_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.graph_ingresos_btn.clicked.connect(self.show_graph_ingresos)

        # Ordenar
        buttons_layout.addWidget(self.add_product_btn)
        buttons_layout.addWidget(self.edit_product_btn)
        buttons_layout.addWidget(self.sell_btn)
        buttons_layout.addWidget(self.delete_product_btn)
        buttons_layout.addWidget(self.graph_stock_btn)
        buttons_layout.addWidget(self.graph_sold_btn)
        buttons_layout.addWidget(self.graph_entradas_btn)
        buttons_layout.addWidget(self.graph_ingresos_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.load_products()

    # ========================
    # GENERAR DOCID TIPO MXXX
    # ========================
    def generate_product_id(self):
        """Busca el mayor número en IDs tipo 'MXXX' y genera el siguiente."""
        coll_ref = db.collection("Inventario")
        last_index = 0

        all_docs = coll_ref.stream()
        for d in all_docs:
            if d.id.startswith("M"):
                # Extraer la parte numérica
                num_str = d.id[1:]  # si es M001
                try:
                    number = int(num_str)
                    if number > last_index:
                        last_index = number
                except ValueError:
                    pass

        new_id_number = last_index + 1
        new_id = f"M{new_id_number:03d}"  # 'M001', 'M002', ...
        return new_id

    # ========================
    # CARGAR PRODUCTOS
    # ========================
    def load_products(self):
        """Filtra por nombre y min_cantidad."""
        self.table.setRowCount(0)
        self.row_to_doc_id.clear()

        name_filter = self.search_input.text().strip().lower()
        min_cant_str = self.min_cantidad_input.text().strip()
        try:
            min_cant = int(min_cant_str) if min_cant_str else 0
        except ValueError:
            min_cant = 0

        prod_ref = db.collection("Inventario")
        docs = list(prod_ref.stream())
        current_row = 0
        for doc in docs:
            data = doc.to_dict()
            # Filtro por nombre
            nombre_prod = data.get("nombre", "").lower()
            if name_filter and name_filter not in nombre_prod:
                continue

            # Filtro por cantidad
            cantidad = int(data.get("cantidad", 0))
            if cantidad < min_cant:
                continue

            self.table.insertRow(current_row)
            self.row_to_doc_id[current_row] = doc.id

            # Columnas: docID, nombre, categoria, precio, cantidad, unidades_vendidas
            self.table.setItem(current_row, 0, QTableWidgetItem(doc.id))
            self.table.setItem(current_row, 1, QTableWidgetItem(data.get("nombre", "")))
            self.table.setItem(current_row, 2, QTableWidgetItem(data.get("categoria", "")))
            self.table.setItem(current_row, 3, QTableWidgetItem(str(data.get("precio", 0.0))))
            self.table.setItem(current_row, 4, QTableWidgetItem(str(data.get("cantidad", 0))))
            self.table.setItem(current_row, 5, QTableWidgetItem(str(data.get("unidades_vendidas", 0))))

            current_row += 1

    # ========================
    # AÑADIR PRODUCTO
    # ========================
    def add_product(self):
        form = FormularioProducto()
        if form.exec_():
            new_data = form.get_data()

            # Generar docID
            new_id = self.generate_product_id()

            db.collection("Inventario").document(new_id).set(new_data)
            QMessageBox.information(self, "Éxito", f"Producto '{new_data['nombre']}' agregado (doc {new_id}).")
            self.load_products()

    # ========================
    # EDITAR PRODUCTO
    # ========================
    def edit_product(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un producto para editar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID de producto.")
            return

        snap = db.collection("Inventario").document(doc_id).get()
        if not snap.exists:
            QMessageBox.warning(self, "Error", f"El documento {doc_id} no existe en 'Inventario'.")
            return

        data_producto = snap.to_dict()
        form = FormularioProducto(data_producto)
        if form.exec_():
            updated_data = form.get_data()
            db.collection("Inventario").document(doc_id).update(updated_data)
            QMessageBox.information(self, "Éxito", f"Producto {doc_id} actualizado.")
            self.load_products()

    # ========================
    # REALIZAR VENTA
    # ========================
    def sell_product(self):
        """
        Descuenta stock de un producto. Pide cuántas unidades vender.
        Si stock resultante < 0 => error.
        También incrementa 'unidades_vendidas' si existe.
        """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un producto para realizar venta.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID de producto.")
            return

        snap = db.collection("Inventario").document(doc_id).get()
        if not snap.exists:
            QMessageBox.warning(self, "Error", f"El producto {doc_id} no existe en 'Inventario'.")
            return

        data_producto = snap.to_dict()
        stock_actual = int(data_producto.get("cantidad", 0))
        vendidas_actual = int(data_producto.get("unidades_vendidas", 0))

        # Pedir cuántas vender
        num_venta, ok = QInputDialog.getInt(self, "Venta", f"¿Cuántas unidades desea vender? (Stock: {stock_actual})", 1, 1, stock_actual)
        if not ok:
            return

        # Comprobar
        if num_venta > stock_actual:
            QMessageBox.warning(self, "Error", "No hay suficiente stock para esa venta.")
            return

        nuevo_stock = stock_actual - num_venta
        nuevas_vendidas = vendidas_actual + num_venta

        # Actualizar en Firestore
        db.collection("Inventario").document(doc_id).update({
            "cantidad": nuevo_stock,
            "unidades_vendidas": nuevas_vendidas
        })
        QMessageBox.information(self, "Venta realizada", f"Se vendieron {num_venta} unidades. Quedan {nuevo_stock}.")
        self.load_products()

    # ========================
    # ELIMINAR PRODUCTO
    # ========================
    def delete_selected_product(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Seleccione un producto para eliminar.")
            return

        doc_id = self.row_to_doc_id.get(selected_row)
        if not doc_id:
            QMessageBox.warning(self, "Error", "No se encontró docID del producto.")
            return

        confirm = QMessageBox.question(
            self, "Eliminar Producto",
            f"¿Seguro que deseas eliminar el producto con ID {doc_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            db.collection("Inventario").document(doc_id).delete()
            QMessageBox.information(self, "Eliminado", "Producto eliminado correctamente.")
            self.load_products()

    # ========================
    # GRÁFICO DE PRODUCTOS CON MÁS STOCK
    # ========================
    def show_graph_stock(self):
        """
        Muestra un gráfico de barras con los 5 (o 10) productos
        de mayor 'cantidad'.
        """
        prod_ref = db.collection("Inventario").stream()
        productos = []
        for doc in prod_ref:
            data = doc.to_dict()
            nombre = data.get("nombre", doc.id)
            cant = int(data.get("cantidad", 0))
            productos.append((nombre, cant))

        # Ordenar desc por stock
        productos.sort(key=lambda x: x[1], reverse=True)
        # Tomar top 5
        top = productos[:5]

        if not top:
            QMessageBox.warning(self, "Sin Datos", "No hay productos en Inventario.")
            return

        nombres = [p[0] for p in top]
        cantidades = [p[1] for p in top]

        import numpy as np
        x = np.arange(len(nombres))
        plt.figure(figsize=(6, 4))
        plt.bar(x, cantidades, color="blue")
        plt.xticks(x, nombres, rotation=45)
        plt.title("Productos con más Stock (Top 5)")
        plt.xlabel("Producto")
        plt.ylabel("Cantidad")
        plt.tight_layout()
        plt.show()

    # ========================
    # GRÁFICO DE PRODUCTOS MÁS VENDIDOS
    # ========================
    def show_graph_sold(self):
        """
        Muestra un gráfico de los productos con mayor 'unidades_vendidas'.
        """
        prod_ref = db.collection("Inventario").stream()
        ventas = []
        for doc in prod_ref:
            data = doc.to_dict()
            nombre = data.get("nombre", doc.id)
            vendidas = int(data.get("unidades_vendidas", 0))
            ventas.append((nombre, vendidas))

        ventas.sort(key=lambda x: x[1], reverse=True)
        top = ventas[:5]

        if not top:
            QMessageBox.warning(self, "Sin Datos", "No hay productos en Inventario.")
            return

        nombres = [p[0] for p in top]
        vendidas_list = [p[1] for p in top]

        import numpy as np
        x = np.arange(len(nombres))
        plt.figure(figsize=(6, 4))
        plt.bar(x, vendidas_list, color="orange")
        plt.xticks(x, nombres, rotation=45)
        plt.title("Productos más Vendidos (Top 5)")
        plt.xlabel("Producto")
        plt.ylabel("Unidades Vendidas")
        plt.tight_layout()
        plt.show()

    # ========================
    # GRÁFICO DE INGRESOS POR ENTRADAS
    # ========================
    def show_graph_entradas(self):
        """
        Genera un gráfico de los ingresos por entradas (campo 'ingresos_entradas')
        en la colección 'Ingresos'.
        """
        ingresos_ref = db.collection("Ingresos").stream()
        fechas = []
        entradas_vals = []

        for doc in ingresos_ref:
            data = doc.to_dict()
            fecha = data.get("fecha", doc.id)
            ing_entradas = int(data.get("ingresos_entradas", 0))
            fechas.append(fecha)
            entradas_vals.append(ing_entradas)

        if not fechas:
            QMessageBox.warning(self, "Sin Datos", "No hay datos de 'Ingresos' para Entradas.")
            return

        import numpy as np
        x = np.arange(len(fechas))
        plt.figure(figsize=(8, 5))
        plt.bar(x, entradas_vals, color="green")
        plt.xticks(x, fechas, rotation=45)
        plt.title("Ingresos por Entradas (Colección 'Ingresos')")
        plt.xlabel("Fechas / Partidos")
        plt.ylabel("€ Ingresos Entradas")
        plt.tight_layout()
        plt.show()

    # ========================
    # GRÁFICO DE INGRESOS TOTALES (Bar + Entradas)
    # ========================
    def show_graph_ingresos(self):
        """
        Genera un gráfico apilado o comparativo con 'ingresos_bar' y 'ingresos_entradas'
        para ver el total de ingresos por partido.
        """
        ingresos_ref = db.collection("Ingresos").stream()
        fechas = []
        bar_vals = []
        entradas_vals = []
        total_vals = []

        for doc in ingresos_ref:
            data = doc.to_dict()
            fecha = data.get("fecha", doc.id)
            bar = int(data.get("ingresos_bar", 0))
            entradas = int(data.get("ingresos_entradas", 0))
            total = bar + entradas
            fechas.append(fecha)
            bar_vals.append(bar)
            entradas_vals.append(entradas)
            total_vals.append(total)

        if not fechas:
            QMessageBox.warning(self, "Sin Datos", "No hay datos de 'Ingresos'.")
            return

        import numpy as np
        x = np.arange(len(fechas))
        width = 0.3
        plt.figure(figsize=(8, 5))

        # Gráfico de barras lado a lado
        plt.bar(x - width, bar_vals, width=width, color="blue", label="Bar")
        plt.bar(x, entradas_vals, width=width, color="orange", label="Entradas")
        plt.bar(x + width, total_vals, width=width, color="green", alpha=0.7, label="Total")

        plt.xticks(x, fechas, rotation=45)
        plt.xlabel("Fechas / Partidos")
        plt.ylabel("€ Ingresos")
        plt.title("Ingresos Totales (Bar + Entradas)")
        plt.legend()
        plt.tight_layout()
        plt.show()

# =========================
# MAIN (PRUEBA)
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventarioWidget()
    window.show()
    sys.exit(app.exec_())
