import sys
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTableView, QHeaderView, QToolBar, QAction, QDialog, QFormLayout, 
                            QLineEdit, QDateEdit, QComboBox, QMessageBox, QLabel, QSplitter,
                            QDialogButtonBox, QApplication, QFrame, QGridLayout, QSizePolicy, 
                            QStackedWidget, QSpinBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QDate, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class LogisticaTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Usuario ID", "Origen", "Destino", "Fecha Salida", "Fecha Llegada", "Estado", "Acciones"]
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            if index.column() == 7: return None
            value = self._data[index.row()][index.column()]
            
            if index.column() in [4,5] and isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
                
            return str(value)
            
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
            
        elif role == Qt.BackgroundRole:
            estado = self._data[index.row()][6]
            return {
                'Planificado': QColor(240, 248, 255),  # Azul claro
                'En proceso': QColor(255, 255, 224),   # Amarillo claro
                'Completado': QColor(240, 255, 240)    # Verde claro
            }.get(estado, QColor(255, 255, 255))
            
        return None
        
    def rowCount(self, parent=None): return len(self._data)
    def columnCount(self, parent=None): return 8

class AlmacenTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Nombre", "Ubicación", "Acciones"]
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            if index.column() == 3: return None
            return str(self._data[index.row()][index.column()])
            
        return None
        
    def rowCount(self, parent=None): return len(self._data)
    def columnCount(self, parent=None): return 4

class InventarioTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Almacén ID", "Producto", "Cantidad", "Acciones"]
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            if index.column() == 4: return None
            value = self._data[index.row()][index.column()]
            if index.column() == 3: return f"{value} unidades"
            return str(value)
            
        return None
        
    def rowCount(self, parent=None): return len(self._data)
    def columnCount(self, parent=None): return 5

class LogisticaDialog(QDialog):
    def __init__(self, parent=None, log_data=None):
        super().__init__(parent)
        self.log_data = log_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro Logístico" if not self.log_data else "Editar Registro")
        layout = QFormLayout()

        self.origen_input = QLineEdit()
        self.destino_input = QLineEdit()
        
        self.fecha_salida = QDateEdit()
        self.fecha_salida.setCalendarPopup(True)
        
        self.fecha_llegada = QDateEdit()
        self.fecha_llegada.setCalendarPopup(True)
        
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Planificado', 'En proceso', 'Completado'])

        layout.addRow("Origen:", self.origen_input)
        layout.addRow("Destino:", self.destino_input)
        layout.addRow("Fecha Salida:", self.fecha_salida)
        layout.addRow("Fecha Llegada:", self.fecha_llegada)
        layout.addRow("Estado:", self.estado_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)

class AlmacenDialog(QDialog):
    def __init__(self, parent=None, almacen_data=None):
        super().__init__(parent)
        self.almacen_data = almacen_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Almacén" if not self.almacen_data else "Editar Almacén")
        layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.ubicacion_input = QLineEdit()

        layout.addRow("Nombre:", self.nombre_input)
        layout.addRow("Ubicación:", self.ubicacion_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(button_box)
        
        self.setLayout(layout)

class InventarioDialog(QDialog):
    def __init__(self, parent=None, inventario_data=None, almacenes=None):
        super().__init__(parent)
        self.inventario_data = inventario_data
        self.almacenes = almacenes or []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Inventario" if not self.inventario_data else "Editar Inventario")
        layout = QFormLayout()

        self.almacen_combo = QComboBox()
        self.almacen_combo.addItems([str(alm[0]) for alm in self.almacenes])
        
        self.producto_input = QLineEdit()
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(0, 9999)

        layout.addRow("Almacén:", self.almacen_combo)
        layout.addRow("Producto:", self.producto_input)
        layout.addRow("Cantidad:", self.cantidad_spin)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(button_box)
        
        self.setLayout(layout)

class LogisticaWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        self.loginWindow = loginWindow
        self.usu_id = usu_id
        self.initUI()
        #self.loadData()

    def initUI(self):
        self.setWindowTitle("Módulo de Logística - Grupo Porteo")
        self.showMaximized()
        
        # Configuración de toolbar similar a RRHHWindow
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Botones de navegación
        self.btn_logistica = QPushButton("Gestión Logística")
        self.btn_almacenes = QPushButton("Gestión de Almacenes")
        self.btn_inventario = QPushButton("Gestión de Inventario")
        
        # Configuración de stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Vistas
        self.setupLogisticaView()
        self.setupAlmacenesView()
        self.setupInventarioView()
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setupLogisticaView(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.log_table = QTableView()
        self.log_model = LogisticaTableModel()
        self.log_table.setModel(self.log_model)
        
        btn_add = QPushButton("Nuevo Registro")
        btn_add.clicked.connect(self.addLogistica)
        
        layout.addWidget(self.log_table)
        layout.addWidget(btn_add)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def setupAlmacenesView(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.alm_table = QTableView()
        self.alm_model = AlmacenTableModel()
        self.alm_table.setModel(self.alm_model)
        
        btn_add = QPushButton("Nuevo Almacén")
        btn_add.clicked.connect(self.addAlmacen)
        
        layout.addWidget(self.alm_table)
        layout.addWidget(btn_add)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def setupInventarioView(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.inv_table = QTableView()
        self.inv_model = InventarioTableModel()
        self.inv_table.setModel(self.inv_model)
        
        btn_add = QPushButton("Nuevo Inventario")
        btn_add.clicked.connect(self.addInventario)
        
        layout.addWidget(self.inv_table)
        layout.addWidget(btn_add)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    """
    def loadData(self):
        # Cargar datos de logística
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM logistica")
        self.log_data = cursor.fetchall()
        self.log_model.refreshData(self.log_data)
        
        # Cargar almacenes
        cursor.execute("SELECT * FROM almacen")
        self.almacenes = cursor.fetchall()
        self.alm_model.refreshData(self.almacenes)
        
        # Cargar inventario
        cursor.execute("SELECT * FROM inventario")
        self.inventario = cursor.fetchall()
        self.inv_model.refreshData(self.inventario)
    """
    def addLogistica(self):
        dialog = LogisticaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Obtener datos y ejecutar INSERT
            pass

    def addAlmacen(self):
        dialog = AlmacenDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Obtener datos y ejecutar INSERT
            pass

    def addInventario(self):
        dialog = InventarioDialog(self, almacenes=self.almacenes)
        if dialog.exec_() == QDialog.Accepted:
            # Obtener datos y ejecutar INSERT
            pass

    # Implementar métodos similares para editar/eliminar