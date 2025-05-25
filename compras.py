import sys
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTableView, QHeaderView, QToolBar, QAction, QDialog, QFormLayout, 
                            QLineEdit, QDateEdit, QComboBox, QMessageBox, QLabel, QSplitter,
                            QDialogButtonBox, QApplication, QFrame, QGridLayout, QSizePolicy, 
                            QStackedWidget, QSpinBox, QTabWidget, QTextEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QDate, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

class SolicitudCompraTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Usuario ID", "Fecha", "Descripción", "Estado", "Acciones"]

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.DisplayRole:
            if index.column() == 5:  # Columna de acciones
                return None
            value = self._data[index.row()][index.column()]
            if index.column() == 2 and isinstance(value, datetime):  # Fecha
                return value.strftime("%Y-%m-%d")
            return str(value)

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            estado = self._data[index.row()][4]
            return {
                'Pendiente': QColor(255, 255, 224),    # Amarillo claro
                'Aprobada': QColor(240, 255, 240),     # Verde claro
                'Rechazada': QColor(255, 240, 240)     # Rojo claro
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

    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class CompraTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Proveedor", "Usuario ID", "Fecha", "Solicitud ID", "Monto Total", "Estado", "Acciones"]

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.DisplayRole:
            if index.column() == 7:  # Columna de acciones
                return None
            value = self._data[index.row()][index.column()]
            if index.column() == 3 and isinstance(value, datetime):  # Fecha
                return value.strftime("%Y-%m-%d")
            elif index.column() == 5:  # Monto total
                return f"${value:,.2f}"
            return str(value)

        elif role == Qt.TextAlignmentRole:
            if index.column() == 5:  # Monto total
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            estado = self._data[index.row()][6]
            return {
                'Pendiente': QColor(255, 255, 224),    # Amarillo claro
                'Completada': QColor(240, 255, 240)    # Verde claro
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

    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class DetalleTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Referencia ID", "Inventario ID", "Cantidad", "Acciones"]

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.DisplayRole:
            if index.column() == 4:  # Columna de acciones
                return None
            value = self._data[index.row()][index.column()]
            if index.column() == 3:  # Cantidad
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

    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class SolicitudCompraDialog(QDialog):
    def __init__(self, parent=None, solicitud_data=None):
        super().__init__(parent)
        self.solicitud_data = solicitud_data
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Solicitud de Compra" if not self.solicitud_data else "Editar Solicitud")
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
            QLineEdit, QDateEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)

        layout = QFormLayout()

        # Campo para fecha
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha:", self.fecha_edit)

        # Campo para descripción
        self.descripcion_edit = QTextEdit()
        self.descripcion_edit.setMaximumHeight(100)
        layout.addRow("Descripción:", self.descripcion_edit)

        # Campo para estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Pendiente', 'Aprobada', 'Rechazada'])
        layout.addRow("Estado:", self.estado_combo)

        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Precargar datos si se está editando
        if self.solicitud_data:
            if isinstance(self.solicitud_data[2], datetime):
                self.fecha_edit.setDate(QDate.fromString(self.solicitud_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.descripcion_edit.setPlainText(self.solicitud_data[3] or "")
            self.estado_combo.setCurrentText(self.solicitud_data[4])

    def getSolicitudData(self):
        return {
            "fecha": self.fecha_edit.date().toString("yyyy-MM-dd"),
            "descripcion": self.descripcion_edit.toPlainText(),
            "estado": self.estado_combo.currentText()
        }

class CompraDialog(QDialog):
    def __init__(self, parent=None, compra_data=None, solicitudes_aprobadas=None):
        super().__init__(parent)
        self.compra_data = compra_data
        self.solicitudes_aprobadas = solicitudes_aprobadas or []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registro de Compra" if not self.compra_data else "Editar Compra")
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
            QLineEdit, QDateEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)

        layout = QFormLayout()

        # Campo para proveedor
        self.proveedor_spin = QSpinBox()
        self.proveedor_spin.setRange(1, 9999)
        layout.addRow("Proveedor ID:", self.proveedor_spin)

        # Campo para fecha
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha Compra:", self.fecha_edit)

        # Campo para solicitud
        self.solicitud_combo = QComboBox()
        if self.solicitudes_aprobadas:
            self.solicitud_combo.addItems([str(sol[0]) for sol in self.solicitudes_aprobadas])
        else:
            self.solicitud_combo.addItem("Sin solicitudes disponibles")
        layout.addRow("Solicitud ID:", self.solicitud_combo)

        # Campo para monto total
        self.monto_spin = QDoubleSpinBox()
        self.monto_spin.setRange(0.01, 999999.99)
        self.monto_spin.setDecimals(2)
        self.monto_spin.setPrefix("$")
        layout.addRow("Monto Total:", self.monto_spin)

        # Campo para estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Pendiente', 'Completada'])
        layout.addRow("Estado:", self.estado_combo)

        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Precargar datos si se está editando
        if self.compra_data:
            self.proveedor_spin.setValue(int(self.compra_data[1]))
            if isinstance(self.compra_data[3], datetime):
                self.fecha_edit.setDate(QDate.fromString(self.compra_data[3].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            if self.compra_data[4]:
                index = self.solicitud_combo.findText(str(self.compra_data[4]))
                if index != -1:
                    self.solicitud_combo.setCurrentIndex(index)
            self.monto_spin.setValue(float(self.compra_data[5]))
            self.estado_combo.setCurrentText(self.compra_data[6])

    def getCompraData(self):
        return {
            "proveedor": self.proveedor_spin.value(),
            "fecha": self.fecha_edit.date().toString("yyyy-MM-dd"),
            "solicitud_id": self.solicitud_combo.currentText() if self.solicitud_combo.currentText() != "Sin solicitudes disponibles" else None,
            "monto_total": self.monto_spin.value(),
            "estado": self.estado_combo.currentText()
        }

class DetalleDialog(QDialog):
    def __init__(self, parent=None, detalle_data=None, inventario_items=None, tipo="solicitud"):
        super().__init__(parent)
        self.detalle_data = detalle_data
        self.inventario_items = inventario_items or []
        self.tipo = tipo  # "solicitud" o "compra"
        self.initUI()

    def initUI(self):
        title = f"Detalle de {'Solicitud' if self.tipo == 'solicitud' else 'Compra'}"
        if self.detalle_data:
            title = f"Editar {title}"
        self.setWindowTitle(title)
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
            QLineEdit, QDateEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)

        layout = QFormLayout()

        # Campo para inventario
        self.inventario_combo = QComboBox()
        if self.inventario_items:
            for item in self.inventario_items:
                self.inventario_combo.addItem(f"{item[0]} - {item[2]}", item[0])  # ID - Producto
        else:
            self.inventario_combo.addItem("Sin productos disponibles")
        layout.addRow("Producto:", self.inventario_combo)

        # Campo para cantidad
        self.cantidad_spin = QSpinBox()
        self.cantidad_spin.setRange(1, 9999)
        layout.addRow("Cantidad:", self.cantidad_spin)

        # Botones de acción
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Precargar datos si se está editando
        if self.detalle_data:
            # Buscar el item en el combo por ID
            for i in range(self.inventario_combo.count()):
                if self.inventario_combo.itemData(i) == self.detalle_data[2]:
                    self.inventario_combo.setCurrentIndex(i)
                    break
            self.cantidad_spin.setValue(int(self.detalle_data[3]))

    def getDetalleData(self):
        return {
            "inventario_id": self.inventario_combo.currentData(),
            "cantidad": self.cantidad_spin.value()
        }

class ComprasWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.usu_id = usu_id
        self.db_connection = None
        
        # Datos para las tablas
        self.solicitudes_data = []
        self.compras_data = []
        self.detalle_solicitud_data = []
        self.detalle_compra_data = []
        self.inventario_items = []
        
        # Variables para tracking
        self.selected_solicitud_id = None
        self.selected_compra_id = None
        
        self.initUI()
        self.loadInitialData()

    def initUI(self):
        self.setWindowTitle("Módulo de Compras - Grupo Porteo")
        self.showMaximized()

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
                background-color: #94a7cb;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #3a68be;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #94a7cb;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #1f3868;
            }
            QFrame {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            QLabel {
                color: #333;
            }
            QSplitter::handle {
                background-color: #94a7cb;
                height: 4px;
            }
            QTabBar::tab {
                font-weight: normal; 
                padding: 5px 15px; 
                min-width: 80px;
            }

            QTabBar::tab:selected {
                font-weight: bold;
                padding: 5px 20px;
                min-width: 110px;
            }

            QTabBar::tab:!selected {
                padding: 5px 15px;
            }
        """)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo-Grupo-Porteo-White.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        logo_label.setStyleSheet("background-color: transparent; border: none;")
        self.toolbar.addWidget(logo_label)

        # Título
        title_label = QLabel("Sistema de Gestión de Compras")
        title_label.setObjectName("titleLabel")
        self.toolbar.addWidget(title_label)
        self.toolbar.addSeparator()

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setStyleSheet("background-color: transparent;")
        self.toolbar.addWidget(spacer)

        # Botón de cerrar sesión
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        self.toolbar.addWidget(self.logout_btn)

        # Widget principal con pestañas
        self.tab_widget = QTabWidget()
        
        # Pestaña de Solicitudes
        self.solicitudes_tab = QWidget()
        self.setupSolicitudesTab()
        self.tab_widget.addTab(self.solicitudes_tab, "Solicitudes de Compra")
        
        # Pestaña de Compras
        self.compras_tab = QWidget()
        self.setupComprasTab()
        self.tab_widget.addTab(self.compras_tab, "Compras")
        
        self.setCentralWidget(self.tab_widget)

    def setupSolicitudesTab(self):
        layout = QVBoxLayout()
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #94a7cb;
                height: 4px;
                border-radius: 2px;
            }
        """)
        
        # Tabla maestra de solicitudes
        solicitudes_frame = QFrame()
        solicitudes_frame.setFrameShape(QFrame.StyledPanel)
        solicitudes_layout = QVBoxLayout(solicitudes_frame)
        
        # Título
        solicitudes_title = QLabel("Solicitudes de Compra")
        solicitudes_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        solicitudes_layout.addWidget(solicitudes_title)
        
        # Tabla de solicitudes
        self.solicitudes_table = QTableView()
        self.solicitudes_table.setAlternatingRowColors(True)
        self.solicitudes_table.setSelectionBehavior(QTableView.SelectRows)
        self.solicitudes_table.setEditTriggers(QTableView.NoEditTriggers)
        self.solicitudes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.solicitudes_table.verticalHeader().setVisible(False)
        self.solicitudes_table.verticalHeader().setDefaultSectionSize(50)
        self.solicitudes_table.setSortingEnabled(True)
        
        self.solicitudes_model = SolicitudCompraTableModel()
        self.solicitudes_table.setModel(self.solicitudes_model)
        
        # Conectar selección de fila
        self.solicitudes_table.selectionModel().selectionChanged.connect(self.onSolicitudSelected)
        
        solicitudes_layout.addWidget(self.solicitudes_table)
        
        # Botones para solicitudes
        solicitudes_buttons = QHBoxLayout()
        btn_nueva_solicitud = QPushButton("Nueva Solicitud")
        btn_nueva_solicitud.clicked.connect(self.addSolicitud)
        solicitudes_buttons.addWidget(btn_nueva_solicitud)
        
        btn_refresh_solicitudes = QPushButton("Actualizar")
        btn_refresh_solicitudes.clicked.connect(self.loadSolicitudes)
        solicitudes_buttons.addWidget(btn_refresh_solicitudes)
        
        solicitudes_buttons.addStretch()
        solicitudes_layout.addLayout(solicitudes_buttons)
        
        main_splitter.addWidget(solicitudes_frame)
        
        # Splitter para detalle
        detalle_splitter = QSplitter(Qt.Horizontal)
        
        # Tabla de detalle de solicitud
        detalle_solicitud_frame = QFrame()
        detalle_solicitud_frame.setFrameShape(QFrame.StyledPanel)
        detalle_solicitud_layout = QVBoxLayout(detalle_solicitud_frame)
        
        detalle_solicitud_title = QLabel("Detalle de Solicitud")
        detalle_solicitud_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; padding: 5px;")
        detalle_solicitud_layout.addWidget(detalle_solicitud_title)
        
        self.detalle_solicitud_table = QTableView()
        self.detalle_solicitud_table.setAlternatingRowColors(True)
        self.detalle_solicitud_table.setSelectionBehavior(QTableView.SelectRows)
        self.detalle_solicitud_table.setEditTriggers(QTableView.NoEditTriggers)
        self.detalle_solicitud_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_solicitud_table.verticalHeader().setVisible(False)
        self.detalle_solicitud_table.verticalHeader().setDefaultSectionSize(40)
        
        self.detalle_solicitud_model = DetalleTableModel()
        self.detalle_solicitud_table.setModel(self.detalle_solicitud_model)
        
        detalle_solicitud_layout.addWidget(self.detalle_solicitud_table)
        
        # Botones para detalle de solicitud
        detalle_solicitud_buttons = QHBoxLayout()
        btn_agregar_detalle_sol = QPushButton("Agregar Producto")
        btn_agregar_detalle_sol.clicked.connect(self.addDetalleSolicitud)
        detalle_solicitud_buttons.addWidget(btn_agregar_detalle_sol)
        
        detalle_solicitud_buttons.addStretch()
        detalle_solicitud_layout.addLayout(detalle_solicitud_buttons)
        
        detalle_splitter.addWidget(detalle_solicitud_frame)
        
        # Formulario de gestión
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_frame.setMaximumWidth(300)
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("Gestión de Solicitud")
        form_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; padding: 5px;")
        form_layout.addWidget(form_title)
        
        # Información de la solicitud seleccionada
        self.info_solicitud = QLabel("Seleccione una solicitud para ver detalles")
        self.info_solicitud.setWordWrap(True)
        self.info_solicitud.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px solid #dee2e6;
                color: #333;
            }
        """)
        form_layout.addWidget(self.info_solicitud)
        
        # Botones de acción
        btn_aprobar = QPushButton("Aprobar Solicitud")
        btn_aprobar.clicked.connect(self.aprobarSolicitud)
        btn_aprobar.setStyleSheet("background-color: #4CAF50;")
        form_layout.addWidget(btn_aprobar)
        
        btn_rechazar = QPushButton("Rechazar Solicitud")
        btn_rechazar.clicked.connect(self.rechazarSolicitud)
        btn_rechazar.setStyleSheet("background-color: #f44336;")
        form_layout.addWidget(btn_rechazar)
        
        btn_generar_compra = QPushButton("Generar Compra")
        btn_generar_compra.clicked.connect(self.generarCompraFromSolicitud)
        btn_generar_compra.setStyleSheet("background-color: #2196F3;")
        form_layout.addWidget(btn_generar_compra)
        
        form_layout.addStretch()
        
        detalle_splitter.addWidget(form_frame)
        
        main_splitter.addWidget(detalle_splitter)
        
        # Configurar tamaños
        main_splitter.setSizes([400, 300])
        detalle_splitter.setSizes([500, 300])
        
        layout.addWidget(main_splitter)
        self.solicitudes_tab.setLayout(layout)

    def setupComprasTab(self):
        layout = QVBoxLayout()
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Vertical)
        
        # Tabla maestra de compras
        compras_frame = QFrame()
        compras_frame.setFrameShape(QFrame.StyledPanel)
        compras_layout = QVBoxLayout(compras_frame)
        
        # Título
        compras_title = QLabel("Registro de Compras")
        compras_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        compras_layout.addWidget(compras_title)
        
        # Tabla de compras
        self.compras_table = QTableView()
        self.compras_table.setAlternatingRowColors(True)
        self.compras_table.setSelectionBehavior(QTableView.SelectRows)
        self.compras_table.setEditTriggers(QTableView.NoEditTriggers)
        self.compras_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.compras_table.verticalHeader().setVisible(False)
        self.compras_table.verticalHeader().setDefaultSectionSize(50)
        self.compras_table.setSortingEnabled(True)
        
        self.compras_model = CompraTableModel()
        self.compras_table.setModel(self.compras_model)
        
        # Conectar selección de fila
        self.compras_table.selectionModel().selectionChanged.connect(self.onCompraSelected)
        
        compras_layout.addWidget(self.compras_table)
        
        # Botones para compras
        compras_buttons = QHBoxLayout()
        btn_nueva_compra = QPushButton("Nueva Compra")
        btn_nueva_compra.clicked.connect(self.addCompra)
        compras_buttons.addWidget(btn_nueva_compra)
        
        btn_refresh_compras = QPushButton("Actualizar")
        btn_refresh_compras.clicked.connect(self.loadCompras)
        compras_buttons.addWidget(btn_refresh_compras)
        
        compras_buttons.addStretch()
        compras_layout.addLayout(compras_buttons)
        
        main_splitter.addWidget(compras_frame)
        
        # Tabla de detalle de compra
        detalle_compra_frame = QFrame()
        detalle_compra_frame.setFrameShape(QFrame.StyledPanel)
        detalle_compra_layout = QVBoxLayout(detalle_compra_frame)
        
        detalle_compra_title = QLabel("Detalle de Compra")
        detalle_compra_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; padding: 5px;")
        detalle_compra_layout.addWidget(detalle_compra_title)
        
        self.detalle_compra_table = QTableView()
        self.detalle_compra_table.setAlternatingRowColors(True)
        self.detalle_compra_table.setSelectionBehavior(QTableView.SelectRows)
        self.detalle_compra_table.setEditTriggers(QTableView.NoEditTriggers)
        self.detalle_compra_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_compra_table.verticalHeader().setVisible(False)
        self.detalle_compra_table.verticalHeader().setDefaultSectionSize(40)
        
        self.detalle_compra_model = DetalleTableModel()
        self.detalle_compra_table.setModel(self.detalle_compra_model)
        
        detalle_compra_layout.addWidget(self.detalle_compra_table)
        
        # Botones para detalle de compra
        detalle_compra_buttons = QHBoxLayout()
        btn_agregar_detalle_comp = QPushButton("Agregar Producto")
        btn_agregar_detalle_comp.clicked.connect(self.addDetalleCompra)
        detalle_compra_buttons.addWidget(btn_agregar_detalle_comp)
        
        btn_completar_compra = QPushButton("Completar Compra")
        btn_completar_compra.clicked.connect(self.completarCompra)
        btn_completar_compra.setStyleSheet("background-color: #4CAF50;")
        detalle_compra_buttons.addWidget(btn_completar_compra)
        
        detalle_compra_buttons.addStretch()
        detalle_compra_layout.addLayout(detalle_compra_buttons)
        
        main_splitter.addWidget(detalle_compra_frame)
        
        # Configurar tamaños
        main_splitter.setSizes([400, 300])
        
        layout.addWidget(main_splitter)
        self.compras_tab.setLayout(layout)

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

    def loadInitialData(self):
        self.loadInventarioItems()
        self.loadSolicitudes()
        self.loadCompras()

    def loadInventarioItems(self):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT inv_id, inv_alm_id, inv_producto, inv_cantidad FROM inventario ORDER BY inv_producto")
            self.inventario_items = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar inventario: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadSolicitudes(self):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM solicitud_compra ORDER BY sol_fecha DESC")
            self.solicitudes_data = cursor.fetchall()
            self.solicitudes_model.refreshData(self.solicitudes_data)
            
            # Configurar botones de acción
            for row in range(len(self.solicitudes_data)):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editSolicitud(r))
                layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteSolicitud(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                self.solicitudes_table.setIndexWidget(self.solicitudes_model.index(row, 5), widget)
            
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar solicitudes: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadCompras(self):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM compra ORDER BY com_fecha_compra DESC")
            self.compras_data = cursor.fetchall()
            self.compras_model.refreshData(self.compras_data)
            
            # Configurar botones de acción
            for row in range(len(self.compras_data)):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editCompra(r))
                layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteCompra(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                self.compras_table.setIndexWidget(self.compras_model.index(row, 7), widget)
            
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar compras: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def onSolicitudSelected(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            solicitud = self.solicitudes_data[row]
            self.selected_solicitud_id = solicitud[0]
            
            # Actualizar información
            info_text = f"""
            <b>Solicitud ID:</b> {solicitud[0]}<br>
            <b>Fecha:</b> {solicitud[2]}<br>
            <b>Estado:</b> {solicitud[4]}<br>
            <b>Descripción:</b> {solicitud[3] or 'Sin descripción'}
            """
            self.info_solicitud.setText(info_text)
            
            # Cargar detalle
            self.loadDetalleSolicitud(solicitud[0])

    def onCompraSelected(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            compra = self.compras_data[row]
            self.selected_compra_id = compra[0]
            
            # Cargar detalle
            self.loadDetalleCompra(compra[0])

    def loadDetalleSolicitud(self, solicitud_id):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM detalle_solicitud WHERE sol_id = %s", (solicitud_id,))
            self.detalle_solicitud_data = cursor.fetchall()
            self.detalle_solicitud_model.refreshData(self.detalle_solicitud_data)
            
            # Configurar botones de acción
            for row in range(len(self.detalle_solicitud_data)):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(2, 2, 2, 2)
                
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(25)
                edit_btn.clicked.connect(lambda _, r=row: self.editDetalleSolicitud(r))
                layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(25)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteDetalleSolicitud(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                self.detalle_solicitud_table.setIndexWidget(self.detalle_solicitud_model.index(row, 4), widget)
            
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar detalle: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadDetalleCompra(self, compra_id):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM detalle_compra WHERE com_id = %s", (compra_id,))
            self.detalle_compra_data = cursor.fetchall()
            self.detalle_compra_model.refreshData(self.detalle_compra_data)
            
            # Configurar botones de acción
            for row in range(len(self.detalle_compra_data)):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(2, 2, 2, 2)
                
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(25)
                edit_btn.clicked.connect(lambda _, r=row: self.editDetalleCompra(r))
                layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(25)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteDetalleCompra(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                self.detalle_compra_table.setIndexWidget(self.detalle_compra_model.index(row, 4), widget)
            
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar detalle: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    # Métodos CRUD para Solicitudes
    def addSolicitud(self):
        dialog = SolicitudCompraDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getSolicitudData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO solicitud_compra (sol_usu_id, sol_fecha, sol_descripcion, sol_estado)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (self.usu_id, data["fecha"], data["descripcion"], data["estado"]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Solicitud creada correctamente")
                self.loadSolicitudes()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al crear solicitud: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editSolicitud(self, row):
        record = self.solicitudes_data[row]
        dialog = SolicitudCompraDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getSolicitudData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                UPDATE solicitud_compra 
                SET sol_fecha = %s, sol_descripcion = %s, sol_estado = %s
                WHERE sol_id = %s
                """
                cursor.execute(query, (data["fecha"], data["descripcion"], data["estado"], record[0]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Solicitud actualizada correctamente")
                self.loadSolicitudes()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar solicitud: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteSolicitud(self, row):
        record = self.solicitudes_data[row]
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la solicitud {record[0]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                
                # Eliminar detalles primero
                cursor.execute("DELETE FROM detalle_solicitud WHERE sol_id = %s", (record[0],))
                # Eliminar solicitud
                cursor.execute("DELETE FROM solicitud_compra WHERE sol_id = %s", (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Solicitud eliminada correctamente")
                self.loadSolicitudes()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar solicitud: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    # Métodos para gestión de solicitudes
    def aprobarSolicitud(self):
        if not self.selected_solicitud_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una solicitud primero")
            return
            
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE solicitud_compra SET sol_estado = 'Aprobada' WHERE sol_id = %s", 
                         (self.selected_solicitud_id,))
            self.db_connection.commit()
            cursor.close()
            
            QMessageBox.information(self, "Éxito", "Solicitud aprobada correctamente")
            self.loadSolicitudes()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al aprobar solicitud: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def rechazarSolicitud(self):
        if not self.selected_solicitud_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una solicitud primero")
            return
            
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE solicitud_compra SET sol_estado = 'Rechazada' WHERE sol_id = %s", 
                         (self.selected_solicitud_id,))
            self.db_connection.commit()
            cursor.close()
            
            QMessageBox.information(self, "Éxito", "Solicitud rechazada")
            self.loadSolicitudes()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al rechazar solicitud: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def generarCompraFromSolicitud(self):
        if not self.selected_solicitud_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una solicitud aprobada primero")
            return
            
        # Verificar que la solicitud esté aprobada
        solicitud_actual = None
        for sol in self.solicitudes_data:
            if sol[0] == self.selected_solicitud_id:
                solicitud_actual = sol
                break
                
        if not solicitud_actual or solicitud_actual[4] != 'Aprobada':
            QMessageBox.warning(self, "Advertencia", "La solicitud debe estar aprobada para generar una compra")
            return
            
        # Cambiar a la pestaña de compras y crear nueva compra
        self.tab_widget.setCurrentIndex(1)
        
        # Obtener solicitudes aprobadas para el diálogo
        solicitudes_aprobadas = [(self.selected_solicitud_id, f"Solicitud {self.selected_solicitud_id}")]
        
        dialog = CompraDialog(self, solicitudes_aprobadas=solicitudes_aprobadas)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getCompraData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO compra (com_proveedor, com_usu_id, com_fecha_compra, com_sol_id, com_monto_total, com_estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data["proveedor"], self.usu_id, data["fecha"], 
                    data["solicitud_id"], data["monto_total"], data["estado"]
                ))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Compra generada correctamente")
                self.loadCompras()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al generar compra: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    # Métodos CRUD para Compras
    def addCompra(self):
        # Obtener solicitudes aprobadas
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT sol_id, sol_descripcion FROM solicitud_compra WHERE sol_estado = 'Aprobada'")
            solicitudes_aprobadas = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al obtener solicitudes: {err}")
            return
        finally:
            if self.db_connection:
                self.db_connection.close()
        
        dialog = CompraDialog(self, solicitudes_aprobadas=solicitudes_aprobadas)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getCompraData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO compra (com_proveedor, com_usu_id, com_fecha_compra, com_sol_id, com_monto_total, com_estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data["proveedor"], self.usu_id, data["fecha"], 
                    data["solicitud_id"], data["monto_total"], data["estado"]
                ))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Compra creada correctamente")
                self.loadCompras()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al crear compra: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editCompra(self, row):
        record = self.compras_data[row]
        
        # Obtener solicitudes aprobadas
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT sol_id, sol_descripcion FROM solicitud_compra WHERE sol_estado = 'Aprobada'")
            solicitudes_aprobadas = cursor.fetchall()
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al obtener solicitudes: {err}")
            return
        finally:
            if self.db_connection:
                self.db_connection.close()
        
        dialog = CompraDialog(self, record, solicitudes_aprobadas)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getCompraData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                UPDATE compra 
                SET com_proveedor = %s, com_fecha_compra = %s, com_sol_id = %s, 
                    com_monto_total = %s, com_estado = %s
                WHERE com_id = %s
                """
                cursor.execute(query, (
                    data["proveedor"], data["fecha"], data["solicitud_id"], 
                    data["monto_total"], data["estado"], record[0]
                ))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Compra actualizada correctamente")
                self.loadCompras()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar compra: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteCompra(self, row):
        record = self.compras_data[row]
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la compra {record[0]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                
                # Eliminar detalles primero
                cursor.execute("DELETE FROM detalle_compra WHERE com_id = %s", (record[0],))
                # Eliminar compra
                cursor.execute("DELETE FROM compra WHERE com_id = %s", (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Compra eliminada correctamente")
                self.loadCompras()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar compra: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    # Métodos para detalles
    def addDetalleSolicitud(self):
        if not self.selected_solicitud_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una solicitud primero")
            return
            
        dialog = DetalleDialog(self, inventario_items=self.inventario_items, tipo="solicitud")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getDetalleData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO detalle_solicitud (sol_id, inv_id, cantidad)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (self.selected_solicitud_id, data["inventario_id"], data["cantidad"]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto agregado al detalle")
                self.loadDetalleSolicitud(self.selected_solicitud_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def addDetalleCompra(self):
        if not self.selected_compra_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una compra primero")
            return
            
        dialog = DetalleDialog(self, inventario_items=self.inventario_items, tipo="compra")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getDetalleData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO detalle_compra (com_id, inv_id, cantidad)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (self.selected_compra_id, data["inventario_id"], data["cantidad"]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto agregado al detalle")
                self.loadDetalleCompra(self.selected_compra_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editDetalleSolicitud(self, row):
        record = self.detalle_solicitud_data[row]
        dialog = DetalleDialog(self, record, self.inventario_items, "solicitud")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getDetalleData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                UPDATE detalle_solicitud 
                SET inv_id = %s, cantidad = %s
                WHERE ds_id = %s
                """
                cursor.execute(query, (data["inventario_id"], data["cantidad"], record[0]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Detalle actualizado correctamente")
                self.loadDetalleSolicitud(self.selected_solicitud_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editDetalleCompra(self, row):
        record = self.detalle_compra_data[row]
        dialog = DetalleDialog(self, record, self.inventario_items, "compra")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getDetalleData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                UPDATE detalle_compra 
                SET inv_id = %s, cantidad = %s
                WHERE dc_id = %s
                """
                cursor.execute(query, (data["inventario_id"], data["cantidad"], record[0]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Detalle actualizado correctamente")
                self.loadDetalleCompra(self.selected_compra_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteDetalleSolicitud(self, row):
        record = self.detalle_solicitud_data[row]
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro que desea eliminar este producto del detalle?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM detalle_solicitud WHERE ds_id = %s", (record[0],))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto eliminado del detalle")
                self.loadDetalleSolicitud(self.selected_solicitud_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteDetalleCompra(self, row):
        record = self.detalle_compra_data[row]
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro que desea eliminar este producto del detalle?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM detalle_compra WHERE dc_id = %s", (record[0],))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto eliminado del detalle")
                self.loadDetalleCompra(self.selected_compra_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def completarCompra(self):
        if not self.selected_compra_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una compra primero")
            return
            
        # Verificar que la compra tenga detalles
        if not self.detalle_compra_data:
            QMessageBox.warning(self, "Advertencia", "La compra debe tener productos en el detalle antes de completarla")
            return
            
        reply = QMessageBox.question(
            self, "Completar Compra",
            "¿Está seguro que desea completar esta compra? Esto actualizará el inventario.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                
                # Actualizar estado de la compra
                cursor.execute("UPDATE compra SET com_estado = 'Completada' WHERE com_id = %s", 
                             (self.selected_compra_id,))
                
                # Actualizar inventario con las cantidades compradas
                for detalle in self.detalle_compra_data:
                    inv_id = detalle[2]
                    cantidad_comprada = detalle[3]
                    
                    cursor.execute("""
                        UPDATE inventario 
                        SET inv_cantidad = inv_cantidad + %s 
                        WHERE inv_id = %s
                    """, (cantidad_comprada, inv_id))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Compra completada e inventario actualizado")
                self.loadCompras()
                self.loadInventarioItems()  # Recargar inventario actualizado
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al completar compra: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def logout(self):
        self.close()
        self.loginWindow.show()