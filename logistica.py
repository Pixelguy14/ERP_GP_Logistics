import sys
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTableView, QHeaderView, QToolBar, QAction, QDialog, QFormLayout, 
                            QLineEdit, QDateEdit, QComboBox, QMessageBox, QLabel, QSplitter,
                            QDialogButtonBox, QApplication, QFrame, QGridLayout, QSizePolicy, 
                            QStackedWidget, QSpinBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QDate, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor, QStandardItemModel, QStandardItem
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
            # Ocultar la columna de "Acciones"
            if index.column() == 7:
                return None
            value = self._data[index.row()][index.column()]
            # Formato para fechas
            if index.column() in [4, 5] and isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
            return str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            estado = self._data[index.row()][6]
            return {
                'Planificado': QColor(240, 248, 255),  # Azul claro
                'En proceso': QColor(255, 255, 224),    # Amarillo claro
                'Completado': QColor(240, 255, 240)     # Verde claro
            }.get(estado, QColor(255, 255, 255))

        return None

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid() and 0 <= index.row() < len(self._data):
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class AlmacenTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Nombre", "Ubicación", "Acciones"]

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.DisplayRole:
            # No mostrar contenido en la columna "Acciones"
            if index.column() == 3:
                return None
            return str(self._data[index.row()][index.column()])

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid() and 0 <= index.row() < len(self._data):
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class InventarioTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Almacén ID", "Producto", "Cantidad", "Acciones"]

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.DisplayRole:
            # No mostrar nada en la columna de "Acciones"
            if index.column() == 4:
                return None
            value = self._data[index.row()][index.column()]
            # Formatear la cantidad agregando "unidades"
            if index.column() == 3:
                return f"{value} unidades"
            return str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid() and 0 <= index.row() < len(self._data):
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class LogisticaDialog(QDialog):
    def __init__(self, parent=None, log_data=None):
        super().__init__(parent)
        self.log_data = log_data
        self.initUI()

    def initUI(self):
        # Determina el título de la ventana en función de si se está registrando o editando
        self.setWindowTitle("Registro Logístico" if not self.log_data else "Editar Registro")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #94a7cb;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a68be;
            }
            QPushButton:pressed {
                background-color: #1f3868;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)

        layout = QFormLayout()

        # Campo para "Origen"
        self.origen_label = QLabel("Origen:")
        self.origen_input = QLineEdit()
        layout.addRow(self.origen_label, self.origen_input)

        # Campo para "Destino"
        self.destino_label = QLabel("Destino:")
        self.destino_input = QLineEdit()
        layout.addRow(self.destino_label, self.destino_input)

        # Campo para "Fecha Salida"
        self.fecha_salida_label = QLabel("Fecha Salida:")
        self.fecha_salida = QDateEdit()
        self.fecha_salida.setCalendarPopup(True)
        layout.addRow(self.fecha_salida_label, self.fecha_salida)

        # Campo para "Fecha Llegada"
        self.fecha_llegada_label = QLabel("Fecha Llegada:")
        self.fecha_llegada = QDateEdit()
        self.fecha_llegada.setCalendarPopup(True)
        layout.addRow(self.fecha_llegada_label, self.fecha_llegada)

        # Campo para "Estado"
        self.estado_label = QLabel("Estado:")
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Planificado', 'En proceso', 'Completado'])
        layout.addRow(self.estado_label, self.estado_combo)

        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Precargar los datos si se está en modo edición
        if self.log_data:
            # Suponiendo que log_data es una lista con la siguiente estructura:
            # [ID, Usuario ID, Origen, Destino, Fecha Salida, Fecha Llegada, Estado, ...]
            self.origen_input.setText(self.log_data[2] or "")
            self.destino_input.setText(self.log_data[3] or "")
            # Manejo de la fecha de salida
            if isinstance(self.log_data[4], datetime):
                self.fecha_salida.setDate(QDate.fromString(self.log_data[4].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            else:
                self.fecha_salida.setDate(QDate.currentDate())
            # Manejo de la fecha de llegada
            if isinstance(self.log_data[5], datetime):
                self.fecha_llegada.setDate(QDate.fromString(self.log_data[5].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            else:
                self.fecha_llegada.setDate(QDate.currentDate())
            self.estado_combo.setCurrentText(self.log_data[6])
        else:
            # Si es un nuevo registro, se ponen las fechas actuales por defecto
            self.fecha_salida.setDate(QDate.currentDate())
            self.fecha_llegada.setDate(QDate.currentDate())

    def getLogData(self):
        """
        Retorna los datos ingresados en el diálogo en forma de diccionario.
        """
        return {
            "origen": self.origen_input.text(),
            "destino": self.destino_input.text(),
            "fecha_salida": self.fecha_salida.date().toString("yyyy-MM-dd"),
            "fecha_llegada": self.fecha_llegada.date().toString("yyyy-MM-dd"),
            "estado": self.estado_combo.currentText()
        }

class AlmacenDialog(QDialog):
    def __init__(self, parent=None, almacen_data=None):
        super().__init__(parent)
        self.almacen_data = almacen_data
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registro de Almacén" if not self.almacen_data else "Editar Almacén")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #94a7cb;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a68be;
            }
            QPushButton:pressed {
                background-color: #1f3868;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)

        layout = QFormLayout()

        # Campo para el nombre del almacén
        self.nombre_input = QLineEdit()
        layout.addRow("Nombre:", self.nombre_input)

        # Campo para la ubicación
        self.ubicacion_input = QLineEdit()
        layout.addRow("Ubicación:", self.ubicacion_input)

        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Precarga de datos en modo edición (se asume que almacen_data es una lista: [id, nombre, ubicación, ...])
        if self.almacen_data:
            self.nombre_input.setText(str(self.almacen_data[1]) if self.almacen_data[1] is not None else "")
            self.ubicacion_input.setText(str(self.almacen_data[2]) if self.almacen_data[2] is not None else "")

    def getAlmacenData(self):
        """
        Retorna los datos del almacén en un diccionario.
        """
        return {
            "nombre": self.nombre_input.text(),
            "ubicacion": self.ubicacion_input.text()
        }

class InventarioDialog(QDialog):
    def __init__(self, parent=None, inventario_data=None, resultados=None):
        super().__init__(parent)
        self.inventario_data = inventario_data
        # Se espera que "almacenes" sea una lista de tuplas o listas, donde el primer elemento sea el ID
        self.almacenes = [row[0] for row in resultados] if resultados else []
        """
        if self.almacenes == []:
            self.almacenes = self.inventario_data[0]
        """
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registro de Inventario" if not self.inventario_data else "Editar Inventario")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #94a7cb;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a68be;
            }
            QPushButton:pressed {
                background-color: #1f3868;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)

        layout = QFormLayout()

        # Campo para seleccionar el almacén
        # Se agregan los IDs de los almacenes. Puedes ajustar para mostrar nombres u otra información.
        if self.almacenes != []: 
            self.almacen_combo = QComboBox()
            self.almacen_combo.addItems([str(alm) for alm in self.almacenes])
        else:
            self.almacen_combo = QSpinBox()
            self.almacen_combo.setReadOnly(True)
        layout.addRow("Almacén:", self.almacen_combo)

        # Campo para ingresar el nombre del producto
        self.producto_input = QLineEdit()
        layout.addRow("Producto:", self.producto_input)

        # Campo para la cantidad del producto
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(0, 9999)
        layout.addRow("Cantidad:", self.cantidad_spin)

        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Precarga de datos en modo edición (se asume que inventario_data es una lista: [id, almacen_id, producto, cantidad, ...])
        if self.inventario_data:
            almacen_id = str(self.inventario_data[1])
            if self.almacenes != []: 
                index = self.almacen_combo.findText(almacen_id)
                if index != -1:
                    self.almacen_combo.setCurrentIndex(index)
            else:
                self.almacen_combo.setValue(int(self.inventario_data[0]) if self.inventario_data[0] is not None else 0)
            
            self.producto_input.setText(str(self.inventario_data[2]) if self.inventario_data[2] is not None else "")
            self.cantidad_spin.setValue(int(self.inventario_data[3]) if self.inventario_data[3] is not None else 0)

    def getInventarioData(self):
        """
        Retorna los datos del inventario en forma de diccionario.
        """
        if self.almacenes != []: 
            return {
                "almacen_id": self.almacen_combo.currentText(),
                "producto": self.producto_input.text(),
                "cantidad": self.cantidad_spin.value()
            }
        else:
            return {
                "almacen_id": self.almacen_combo.value(),
                "producto": self.producto_input.text(),
                "cantidad": self.cantidad_spin.value()
            }

class LogisticaWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.db_connection = None
        # Listas para almacenar la data obtenida (serán actualizadas por las consultas a la BD)
        self.log_data = []
        self.almacen_data = []
        self.inventario_data = []
        self.latestAlmacenRow = 0
        self.initUI(usu_id)
        self.loadDataMain(usu_id)
        
    def initUI(self, usu_id):
        self.setWindowTitle("Módulo de Logística - Grupo Porteo")
        self.showMaximized()   # Lo volvemos pantalla completa

        self.setStyleSheet("""
            QMainWindow {
                background-color: #3156A1;
                font-family: Arial;
            }
            QTableView {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: #94a7cb;
                selection-color: white;
            }
            QTableView::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #94a7cb;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #94a7cb;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a68be;
            }
            QPushButton:pressed {
                background-color: #1f3868;
            }
            QPushButton#deleteBtn {
                background-color: #dc3545;
            }
            QPushButton#deleteBtn:hover {
                background-color: #9c1b28;
            }
            QToolBar {
                background-color: #94a7cb;
                spacing: 10px;
                padding: 5px;
                border: none;
            }
            QToolBar QToolButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
            }
            QToolBar QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            QLabel#titleLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QFrame#chartFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Agregar el logo a la toolbar
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo-Grupo-Porteo.png")
        if logo_pixmap.isNull():
            print("Error: No se pudo cargar Logo-Grupo-Porteo.png")
        else:
            logo_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        self.toolbar.addWidget(logo_label)
        
        # Título en la toolbar
        title_label = QLabel("Sistema de Gestión de Logística")
        title_label.setObjectName("titleLabel")
        self.toolbar.addWidget(title_label)
        self.toolbar.addSeparator()
        
        # Botón para la vista de Gestión de Logística (vía primera página del StackedWidget)
        self.btn_logistica = QPushButton("Gestión de Logística")
        self.btn_logistica.setCursor(Qt.PointingHandCursor)
        self.btn_logistica.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0), self.loadDataMain(usu_id)))
        self.toolbar.addWidget(self.btn_logistica)
        
        # Botón para la vista de Gestión de Inventario (segunda página del StackedWidget)
        self.btn_inventario = QPushButton("Gestión de Almacenes e Inventario")
        self.btn_inventario.setCursor(Qt.PointingHandCursor)
        self.btn_inventario.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1), self.loadAlmacenData(usu_id)))
        self.toolbar.addWidget(self.btn_inventario)

        # Botón para la tercera pagina del StackedWidget, Reportes y Seguimiento
        self.btn_reportes = QPushButton("Reportes y Seguimiento")
        self.btn_reportes.setCursor(Qt.PointingHandCursor)
        self.btn_reportes.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(2), self.loadReportesData(usu_id)))
        self.toolbar.addWidget(self.btn_reportes)
        
        self.toolbar.addSeparator()
        
        # Spacer para empujar el botón de cerrar sesión a la derecha
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setStyleSheet("background-color: transparent;")
        self.toolbar.addWidget(spacer)
        
        # Botón de Cerrar Sesión
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        self.toolbar.addWidget(self.logout_btn)
        
        self.stacked_widget = QStackedWidget()
        
        # --- Primera vista: Panel de Logística ---
        log_view_widget = QWidget()
        log_layout = QVBoxLayout(log_view_widget)

        # Tabla principal de Logística
        self.table_view_log = QTableView()
        self.table_view_log.setAlternatingRowColors(True)
        self.table_view_log.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_log.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_log.verticalHeader().setVisible(False)
        self.table_view_log.verticalHeader().setDefaultSectionSize(50)
        self.table_view_log.setSortingEnabled(True)

        self.log_table_model = LogisticaTableModel()
        self.table_view_log.setModel(self.log_table_model)

        # Configurar ancho de columnas
        header_log = self.table_view_log.horizontalHeader()
        header_log.setSectionResizeMode(7, QHeaderView.Fixed)
        header_log.resizeSection(7, 300)

        log_layout.addWidget(self.table_view_log)

        # Panel de botones para Logística
        log_button_panel = QHBoxLayout()
        btn_new_log = QPushButton("Nuevo Registro", self)
        btn_new_log.clicked.connect(lambda: self.addLogRecord(usu_id))
        log_button_panel.addWidget(btn_new_log)

        btn_refresh_log = QPushButton("Actualizar", self)
        btn_refresh_log.clicked.connect(lambda: self.loadDataMain(usu_id))
        log_button_panel.addWidget(btn_refresh_log)

        log_button_panel.addStretch()
        log_layout.addLayout(log_button_panel)

        self.stacked_widget.addWidget(log_view_widget)

        # --- Segunda vista: Panel de Almacén con Inventario oculto ---
        alm_view_widget = QWidget()
        alm_layout = QVBoxLayout(alm_view_widget)

        splitter_alm = QSplitter(Qt.Vertical)

        # Tabla principal de Almacenes
        self.table_view_almacen = QTableView()
        self.table_view_almacen.setAlternatingRowColors(True)
        self.table_view_almacen.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_almacen.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_almacen.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_almacen.verticalHeader().setVisible(False)
        self.table_view_almacen.verticalHeader().setDefaultSectionSize(50)
        self.table_view_almacen.setSortingEnabled(True)

        self.almacen_table_model = AlmacenTableModel()
        self.table_view_almacen.setModel(self.almacen_table_model)

        # Configurar ancho de columnas
        header_alm = self.table_view_almacen.horizontalHeader()
        header_alm.setSectionResizeMode(3, QHeaderView.Fixed)
        header_alm.resizeSection(3, 300)

        splitter_alm.addWidget(self.table_view_almacen)

        # Tabla de Inventario (oculta inicialmente)
        self.table_view_inventario = QTableView()
        self.table_view_inventario.setAlternatingRowColors(True)
        self.table_view_inventario.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_inventario.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_inventario.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_inventario.verticalHeader().setVisible(False)
        self.table_view_inventario.verticalHeader().setDefaultSectionSize(50)
        self.table_view_inventario.setSortingEnabled(True)

        self.inventario_table_model = InventarioTableModel()
        self.table_view_inventario.setModel(self.inventario_table_model)

        splitter_alm.addWidget(self.table_view_inventario)
        self.table_view_inventario.hide()

        splitter_alm.setSizes([450, 550])
        splitter_alm.setStretchFactor(0, 0)
        splitter_alm.setStretchFactor(1, 0)

        alm_layout.addWidget(splitter_alm)

        # Panel de botones para Almacén
        alm_button_panel = QHBoxLayout()
        btn_new_alm = QPushButton("Nuevo Almacén", self)
        btn_new_alm.clicked.connect(lambda: self.addAlmacenRecord(usu_id))
        alm_button_panel.addWidget(btn_new_alm)

        btn_refresh_alm = QPushButton("Actualizar", self)
        btn_refresh_alm.clicked.connect(lambda: self.loadAlmacenData(usu_id))
        alm_button_panel.addWidget(btn_refresh_alm)

        btn_toggle_inv = QPushButton("Agregar al Inventario", self)
        btn_toggle_inv.clicked.connect(lambda: self.addInventarioRecord(usu_id))
        alm_button_panel.addWidget(btn_toggle_inv)

        alm_button_panel.addStretch()
        alm_layout.addLayout(alm_button_panel)

        self.stacked_widget.addWidget(alm_view_widget)

        # --- Tercera vista: Panel de Reportes y Seguimiento ---
        
        reportes_view_widget = QWidget()
        main_report_view_layout = QVBoxLayout(reportes_view_widget)

        splitter_reportes = QSplitter(Qt.Vertical)

        # Sección de Pedidos en Proceso
        pedidos_frame = QFrame()
        pedidos_frame.setStyleSheet("background-color: white; border-radius: 4px;")
        pedidos_layout = QVBoxLayout(pedidos_frame)

        lbl_pedidos = QLabel("Pedidos en Proceso")
        lbl_pedidos.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;")
        pedidos_layout.addWidget(lbl_pedidos)

        self.table_pedidos = QTableView()
        self.table_pedidos.setStyleSheet("border: none;") # Estilo consistente con el segundo código
        self.table_pedidos.setAlternatingRowColors(True)
        self.table_pedidos.setSelectionBehavior(QTableView.SelectRows)
        self.model_pedidos = LogisticaTableModel()
        
        self.table_pedidos.setModel(self.model_pedidos)
        pedidos_layout.addWidget(self.table_pedidos)

        splitter_reportes.addWidget(pedidos_frame)

        # Sección de Reportes Mensuales
        reportes_frame = QFrame()
        reportes_frame.setStyleSheet("background-color: white; border-radius: 4px;") # Estilo consistente
        monthly_report_frame_layout = QVBoxLayout(reportes_frame)

        lbl_reportes = QLabel("Reporte Mensual")
        lbl_reportes.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;") # Estilo consistente
        monthly_report_frame_layout.addWidget(lbl_reportes)

        # Controles de fecha
        fecha_panel = QHBoxLayout()
        self.date_edit_mes = QDateEdit()
        self.date_edit_mes.setDisplayFormat("MM/yyyy")
        self.date_edit_mes.setDate(QDate.currentDate())
        # Eliminado el estilo inline en QDateEdit para mantener la consistencia con el segundo código
        
        self.btn_generar_reporte = QPushButton("Generar Reporte")
        self.btn_generar_reporte.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;") # Estilo consistente
        self.btn_generar_reporte.clicked.connect(lambda: self.generarReporteMensual(usu_id))


        fecha_panel.addWidget(QLabel("Mes:")) # Etiqueta más concisa
        fecha_panel.addWidget(self.date_edit_mes)
        fecha_panel.addWidget(self.btn_generar_reporte)
        fecha_panel.addStretch()
        monthly_report_frame_layout.addLayout(fecha_panel)


        self.table_reporte = QTableView()
        self.table_reporte.setStyleSheet("border: none;") # Estilo consistente
        self.table_reporte.setAlternatingRowColors(True)
        self.model_reporte = QStandardItemModel()
        self.model_reporte.setHorizontalHeaderLabels(["Origen", "Destino", "Fecha Salida"])
        self.table_reporte.setModel(self.model_reporte)
        monthly_report_frame_layout.addWidget(self.table_reporte)

        splitter_reportes.addWidget(reportes_frame)

        splitter_reportes.setSizes([300, 300]) # Ajuste si necesitas más secciones
        main_report_view_layout.addWidget(splitter_reportes)

        self.stacked_widget.addWidget(reportes_view_widget)

        # Configuración del widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(central_widget)

    def connectToDatabase(self):
        try:
            load_dotenv()
            self.db_connection = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                database=os.environ.get("DB_DATABASE"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD")
            )
            return True
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"No se pudo conectar: {err}")
            return False
        
    def loadDataMain(self, usu_id):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            
            # Get all finance records
            cursor.execute("SELECT * FROM logistica ORDER BY log_usu_id DESC")
            self.log_data = cursor.fetchall()
            
            # Actualizamos los datos de la tabla
            self.log_table_model.refreshData(self.log_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.log_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editLogRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de eliminar
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteLogRecord(r, usu_id))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla, en la columna 7
                self.table_view_log.setIndexWidget(self.log_table_model.index(row, 7), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
    
    def loadInventarioData(self, row_alm, usu_id):
        record = self.almacen_data[row_alm]# usamos almacen_data por que queremos recuperar
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Get all finance records
            query = """SELECT * FROM inventario WHERE inv_alm_id=%s ORDER BY inv_producto DESC"""
            cursor.execute(query, (record[0], ))
            self.inventario_data = cursor.fetchall()
            
            # Actualizamos los datos de la tabla
            self.inventario_table_model.refreshData(self.inventario_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.inventario_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editInventarioRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de eliminar
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteInventarioRecord(r, usu_id))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla, en la columna 4
                self.table_view_inventario.setIndexWidget(self.inventario_table_model.index(row, 4), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadAlmacenData(self, usu_id):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            
            # Get all finance records
            cursor.execute("SELECT * FROM almacen ORDER BY alm_nombre DESC")
            self.almacen_data = cursor.fetchall()
            
            # Actualizamos los datos de la tabla
            self.almacen_table_model.refreshData(self.almacen_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.almacen_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editAlmacenRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de eliminar
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteAlmacenRecord(r, usu_id))
                layout.addWidget(delete_btn)
                
                # inventario button
                inventario_btn = QPushButton("Inventario")
                inventario_btn.setObjectName("inventarioBtn")
                inventario_btn.setFixedWidth(100)
                inventario_btn.setFixedHeight(30)
                inventario_btn.clicked.connect(lambda _, r=row: self.toggleInventarioView(r, usu_id))
                layout.addWidget(inventario_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla, en la columna 3
                self.table_view_almacen.setIndexWidget(self.almacen_table_model.index(row, 3), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
    
    def addLogRecord(self, usu_id):
        dialog = LogisticaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            log_data = dialog.getLogData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                user_id = usu_id
                query = """
                INSERT INTO logistica (log_usu_id, log_origen, log_destino, log_fecha_salida, log_fecha_llegada, log_estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user_id,
                    log_data["origen"],
                    log_data["destino"],
                    log_data["fecha_salida"],
                    log_data["fecha_llegada"],
                    log_data["estado"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro agregado correctamente")
                self.loadDataMain(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def addAlmacenRecord(self, usu_id):
        dialog = AlmacenDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            almacen_data = dialog.getAlmacenData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                user_id = usu_id
                query = """
                INSERT INTO almacen (alm_nombre, alm_ubicacion)
                VALUES (%s, %s)
                """
                cursor.execute(query, (
                    almacen_data["nombre"],
                    almacen_data["ubicacion"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro agregado correctamente")
                self.loadAlmacenData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()
        
    def addInventarioRecord(self, usu_id):
        if not self.connectToDatabase():
                return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT alm_id FROM almacen")
            resultados = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al ejecutar la consulta: {err}")
        #print(resultados)
        dialog = InventarioDialog(self, resultados=resultados)
        if dialog.exec_() == QDialog.Accepted:
            inventario_data = dialog.getInventarioData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                user_id = usu_id
                query = """
                INSERT INTO inventario (inv_alm_id, inv_producto, inv_cantidad)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (
                    inventario_data["almacen_id"],
                    inventario_data["producto"],
                    inventario_data["cantidad"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro agregado correctamente")
                if self.table_view_inventario.isVisible():
                    self.loadInventarioData(self.latestAlmacenRow,usu_id)
                else:
                    self.table_view_inventario.show()
                    self.loadInventarioData(self.latestAlmacenRow,usu_id)

                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editLogRecord(self, row, usu_id):
        record = self.log_data[row]
        
        dialog = LogisticaDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            log_data = dialog.getLogData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE logistica 
                SET log_origen = %s, log_destino = %s, 
                    log_fecha_salida = %s, log_fecha_llegada = %s, 
                    log_estado = %s
                WHERE log_id = %s
                """
                cursor.execute(query, (
                    log_data["origen"],
                    log_data["destino"],
                    log_data["fecha_salida"],
                    log_data["fecha_llegada"],
                    log_data["estado"],
                    record[0]  # log_id
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro actualizado correctamente")
                self.loadDataMain(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editAlmacenRecord(self, row, usu_id):
        record = self.almacen_data[row]
        
        dialog = AlmacenDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            almacen_data = dialog.getAlmacenData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE almacen 
                SET alm_nombre = %s, alm_ubicacion = %s
                WHERE alm_id = %s
                """
                cursor.execute(query, (
                    almacen_data["nombre"],
                    almacen_data["ubicacion"],
                    record[0]  # alm_id
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Almacén actualizado correctamente")
                self.loadAlmacenData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar almacén: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editInventarioRecord(self, row, usu_id):
        record = self.inventario_data[row]
        
        dialog = InventarioDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            inventario_data = dialog.getInventarioData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE inventario 
                SET inv_alm_id = %s, inv_producto = %s, inv_cantidad = %s
                WHERE inv_id = %s
                """
                cursor.execute(query, (
                    inventario_data["almacen_id"],
                    inventario_data["producto"],
                    inventario_data["cantidad"],
                    record[0]  # inv_id
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Inventario actualizado correctamente")
                self.loadInventarioData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar inventario: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteLogRecord(self, row, usu_id):
        record = self.log_data[row]
        
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el registro con ID {record[0]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                query = "DELETE FROM logistica WHERE log_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                self.loadDataMain(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteAlmacenRecord(self, row, usu_id):
        record = self.almacen_data[row]
        
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el almacén {record[1]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                # Verificar si tiene inventario asociado
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE inv_alm_id = %s", (record[0],))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    QMessageBox.warning(self, "Advertencia", 
                        "No se puede eliminar un almacén con inventario asociado")
                    return
                    
                query = "DELETE FROM almacen WHERE alm_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Almacén eliminado correctamente")
                self.loadAlmacenData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar almacén: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteInventarioRecord(self, row, usu_id):
        record = self.inventario_data[row]
        
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el registro de {record[2]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                query = "DELETE FROM inventario WHERE inv_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                self.loadInventarioData(self.latestAlmacenRow, usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def toggleInventarioView(self, row, usu_id):

        if self.table_view_inventario.isVisible() and row == self.latestAlmacenRow:
            self.table_view_inventario.hide()
        else:
            self.table_view_inventario.show()
            self.loadInventarioData(row,usu_id)
            self.latestAlmacenRow=row
    
    def loadReportesData(self, usu_id):
        self.cargarPedidosEnProceso(usu_id)
        self.generarReporteMensual(usu_id)

    def cargarPedidosEnProceso(self, usu_id):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM logistica WHERE log_estado = 'En proceso'")
            datos = cursor.fetchall()
            
            # Usamos el mismo modelo pero solo con las columnas necesarias
            self.model_pedidos.refreshData(datos)
            
            # Ocultar columnas no relevantes
            for col in [0, 1, 5, 6]:  # Ocultar ID, usuario_id, fecha llegada, estado
                self.table_pedidos.setColumnHidden(col, True)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar pedidos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def generarReporteMensual(self, usu_id):
        if not self.connectToDatabase():
            return
        
        try:
            fecha_seleccionada = self.date_edit_mes.date()
            inicio_mes = QDate(fecha_seleccionada.year(), fecha_seleccionada.month(), 1)
            fin_mes = inicio_mes.addMonths(1).addDays(-1)
            
            cursor = self.db_connection.cursor()
            query = """
            SELECT log_origen, log_destino, log_fecha_salida 
            FROM logistica 
            WHERE log_fecha_salida BETWEEN %s AND %s
            """
            cursor.execute(query, (
                inicio_mes.toString("yyyy-MM-dd"),
                fin_mes.toString("yyyy-MM-dd")
            ))
            
            resultados = cursor.fetchall()
            
            # Limpiar modelo existente
            self.model_reporte.clear()
            self.model_reporte.setHorizontalHeaderLabels(["Origen", "Destino", "Fecha Salida"])
            
            # Llenar con nuevos datos
            for row in resultados:
                items = [
                    QStandardItem(str(row[0])),
                    QStandardItem(str(row[1])),
                    QStandardItem(row[2].strftime("%Y-%m-%d") if isinstance(row[2], datetime) else str(row[2]))
                ]
                self.model_reporte.appendRow(items)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al generar reporte: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def logout(self):
        self.close()
        self.loginWindow.show()
