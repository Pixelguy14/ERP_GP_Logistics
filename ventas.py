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

class VentaTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = ["ID", "Cliente", "Usuario ID", "Fecha de Venta", "Monto Total", "Estado", "Acciones"]
                        # 0,        1,         2,              3,               4,          5,         6
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role == Qt.DisplayRole:
            if index.column() == 6:  # Columna de acciones
                return None
            value = self._data[index.row()][index.column()]
            if index.column() == 3 and isinstance(value, datetime):  # Fecha
                return value.strftime("%Y-%m-%d")
            elif index.column() == 4:  # Monto total
                return f"${value:,.2f}"
            return str(value)

        elif role == Qt.TextAlignmentRole:
            if index.column() == 4:  # Monto total
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole: # Estado
            estado = self._data[index.row()][5]
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
        self._headers = ["ID", "Venta ID", "Inventario ID", "Cantidad", "Acciones"]

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

class VentaDialog(QDialog):
    def __init__(self, parent=None, venta_data=None):
        super().__init__(parent)
        self.venta_data = venta_data
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registro de Venta" if not self.venta_data else "Editar Venta")
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

        # Campo para cliente
        self.cliente_spin = QSpinBox()
        self.cliente_spin.setRange(1, 9999)
        layout.addRow("Cliente ID:", self.cliente_spin)

        # Campo para fecha
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setCalendarPopup(True)
        self.fecha_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha de Venta:", self.fecha_edit)

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
        if self.venta_data:
            self.cliente_spin.setValue(int(self.venta_data[1]))
            if isinstance(self.venta_data[3], datetime):
                self.fecha_edit.setDate(QDate.fromString(self.venta_data[3].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.monto_spin.setValue(float(self.venta_data[4]))
            self.estado_combo.setCurrentText(self.venta_data[5])

    def getVentaData(self):
        return {
            "cliente": self.cliente_spin.value(),
            "fecha": self.fecha_edit.date().toString("yyyy-MM-dd"),
            "monto_total": self.monto_spin.value(),
            "estado": self.estado_combo.currentText()
        }

class DetalleDialog(QDialog):
    def __init__(self, parent=None, detalle_data=None, inventario_items=None, tipo="solicitud"):
        super().__init__(parent)
        self.detalle_data = detalle_data
        self.inventario_items = inventario_items or []
        self.tipo = tipo  # "solicitud" o "venta"
        self.initUI()

    def initUI(self):
        title = f"Detalle de {'Solicitud' if self.tipo == 'solicitud' else 'Venta'}"
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

class VentasWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.usu_id = usu_id
        self.db_connection = None
        
        # Datos para las tablas
        self.ventas_data = []
        self.detalle_venta_data = []
        self.inventario_items = []
        
        # Variables para tracking
        self.selected_venta_id = None
        
        self.initUI()
        self.loadInitialData()

    def initUI(self):
        self.setWindowTitle("Módulo de Ventas - Grupo Porteo")
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
        title_label = QLabel("Sistema de Gestión de Ventas")
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
        
        # Pestaña de Ventas
        self.ventas_tab = QWidget()
        self.setupVentasTab()
        self.tab_widget.addTab(self.ventas_tab, "Ventas")

        # Pestaña de Reporte de Ventas
        self.reportes_ventas_tab = QWidget()
        self.setupReportesVentasTab()
        self.loadReportesData()
        self.tab_widget.addTab(self.reportes_ventas_tab, "Reportes de Ventas")
        
        self.setCentralWidget(self.tab_widget)

    def setupVentasTab(self):
        layout = QVBoxLayout()
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Vertical)
        
        # Tabla maestra de ventas
        ventas_frame = QFrame()
        ventas_frame.setFrameShape(QFrame.StyledPanel)
        ventas_layout = QVBoxLayout(ventas_frame)
        
        # Título
        ventas_title = QLabel("Registro de Ventas")
        ventas_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 5px;")
        ventas_layout.addWidget(ventas_title)
        
        # Tabla de ventas
        self.ventas_table = QTableView()
        self.ventas_table.setAlternatingRowColors(True)
        self.ventas_table.setSelectionBehavior(QTableView.SelectRows)
        self.ventas_table.setEditTriggers(QTableView.NoEditTriggers)
        self.ventas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ventas_table.verticalHeader().setVisible(False)
        self.ventas_table.verticalHeader().setDefaultSectionSize(50)
        self.ventas_table.setSortingEnabled(True)
        
        self.ventas_model = VentaTableModel()
        self.ventas_table.setModel(self.ventas_model)
        
        # Conectar selección de fila
        self.ventas_table.selectionModel().selectionChanged.connect(self.onVentaSelected)
        
        ventas_layout.addWidget(self.ventas_table)
        
        # Botones para ventas
        ventas_buttons = QHBoxLayout()
        btn_nueva_venta = QPushButton("Nueva Venta")
        btn_nueva_venta.clicked.connect(self.addVenta)
        ventas_buttons.addWidget(btn_nueva_venta)
        
        btn_refresh_ventas = QPushButton("Actualizar")
        btn_refresh_ventas.clicked.connect(self.loadVentas)
        ventas_buttons.addWidget(btn_refresh_ventas)
        
        ventas_buttons.addStretch()
        ventas_layout.addLayout(ventas_buttons)
        
        main_splitter.addWidget(ventas_frame)
        
        # Tabla de detalle de venta
        detalle_venta_frame = QFrame()
        detalle_venta_frame.setFrameShape(QFrame.StyledPanel)
        detalle_venta_layout = QVBoxLayout(detalle_venta_frame)
        
        detalle_venta_title = QLabel("Detalle de Venta")
        detalle_venta_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333; padding: 5px;")
        detalle_venta_layout.addWidget(detalle_venta_title)
        
        self.detalle_venta_table = QTableView()
        self.detalle_venta_table.setAlternatingRowColors(True)
        self.detalle_venta_table.setSelectionBehavior(QTableView.SelectRows)
        self.detalle_venta_table.setEditTriggers(QTableView.NoEditTriggers)
        self.detalle_venta_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_venta_table.verticalHeader().setVisible(False)
        self.detalle_venta_table.verticalHeader().setDefaultSectionSize(40)
        
        self.detalle_venta_model = DetalleTableModel()
        self.detalle_venta_table.setModel(self.detalle_venta_model)
        
        detalle_venta_layout.addWidget(self.detalle_venta_table)
        
        # Botones para detalle de venta
        detalle_venta_buttons = QHBoxLayout()
        btn_agregar_detalle_comp = QPushButton("Agregar Producto")
        btn_agregar_detalle_comp.clicked.connect(self.addDetalleVenta)
        detalle_venta_buttons.addWidget(btn_agregar_detalle_comp)
        
        btn_completar_venta = QPushButton("Completar Venta")
        btn_completar_venta.clicked.connect(self.completarVenta)
        btn_completar_venta.setStyleSheet("background-color: #4CAF50;")
        detalle_venta_buttons.addWidget(btn_completar_venta)
        
        detalle_venta_buttons.addStretch()
        detalle_venta_layout.addLayout(detalle_venta_buttons)
        
        main_splitter.addWidget(detalle_venta_frame)
        
        # Configurar tamaños
        main_splitter.setSizes([400, 300])
        
        layout.addWidget(main_splitter)
        self.ventas_tab.setLayout(layout)

    def setupReportesVentasTab(self):
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        # Sección de Cotizaciones Pendientes
        cotizaciones_frame = QFrame()
        cotizaciones_frame.setStyleSheet("background-color: white; border-radius: 4px;")
        cotizaciones_layout = QVBoxLayout(cotizaciones_frame)
        
        cotizaciones_title = QLabel("Cotizaciones Pendientes")
        cotizaciones_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;")
        cotizaciones_layout.addWidget(cotizaciones_title)
        
        self.cotizaciones_table = QTableView()
        self.cotizaciones_table.setStyleSheet("border: none;")
        self.cotizaciones_model = VentaTableModel()
        self.cotizaciones_table.setModel(self.cotizaciones_model)
        cotizaciones_layout.addWidget(self.cotizaciones_table)
        splitter.addWidget(cotizaciones_frame)

        # Sección de Ventas Completadas
        ventas_completadas_frame = QFrame()
        ventas_completadas_frame.setStyleSheet("background-color: white; border-radius: 4px;")
        ventas_completadas_layout = QVBoxLayout(ventas_completadas_frame)
        
        ventas_completadas_title = QLabel("Ventas Completadas")
        ventas_completadas_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;")
        ventas_completadas_layout.addWidget(ventas_completadas_title)
        
        self.ventas_completadas_table = QTableView()
        self.ventas_completadas_table.setStyleSheet("border: none;")
        self.ventas_completadas_model = VentaTableModel()
        self.ventas_completadas_table.setModel(self.ventas_completadas_model)
        ventas_completadas_layout.addWidget(self.ventas_completadas_table)
        splitter.addWidget(ventas_completadas_frame)

        # Sección de Reporte Mensual
        reporte_mensual_frame = QFrame()
        reporte_mensual_frame.setStyleSheet("background-color: white; border-radius: 4px;")
        reporte_mensual_layout = QVBoxLayout(reporte_mensual_frame)
        
        reporte_mensual_title = QLabel("Reporte Mensual")
        reporte_mensual_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;")
        reporte_mensual_layout.addWidget(reporte_mensual_title)
        
        # Controles de fecha
        fecha_panel = QHBoxLayout()
        self.date_edit_reporte = QDateEdit()
        self.date_edit_reporte.setDisplayFormat("MM/yyyy")
        self.date_edit_reporte.setDate(QDate.currentDate())
        btn_generar_reporte = QPushButton("Generar Reporte")
        btn_generar_reporte.clicked.connect(self.generarReporteMensual)
        btn_generar_reporte.setStyleSheet("background-color: #4CAF50; color: white;")
        
        fecha_panel.addWidget(QLabel("Mes:"))
        fecha_panel.addWidget(self.date_edit_reporte)
        fecha_panel.addWidget(btn_generar_reporte)
        fecha_panel.addStretch()
        reporte_mensual_layout.addLayout(fecha_panel)
        
        self.reporte_mensual_table = QTableView()
        self.reporte_mensual_table.setStyleSheet("border: none;")
        self.reporte_mensual_model = QStandardItemModel()
        self.reporte_mensual_model.setHorizontalHeaderLabels(["Fecha Venta", "Monto Total"])
        self.reporte_mensual_table.setModel(self.reporte_mensual_model)
        reporte_mensual_layout.addWidget(self.reporte_mensual_table)
        splitter.addWidget(reporte_mensual_frame)

        splitter.setSizes([300, 300, 300])
        layout.addWidget(splitter)
        self.reportes_ventas_tab.setLayout(layout)

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
        self.loadVentas()
        return
    
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

    def loadVentas(self):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM venta ORDER BY ven_fecha_venta DESC")
            self.ventas_data = cursor.fetchall()
            self.ventas_model.refreshData(self.ventas_data)
            
            # Configurar botones de acción
            for row in range(len(self.ventas_data)):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editVenta(r))
                layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteVenta(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                self.ventas_table.setIndexWidget(self.ventas_model.index(row, 6), widget)
            
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar ventas: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def onVentaSelected(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            row = indexes[0].row()
            venta = self.ventas_data[row]
            self.selected_venta_id = venta[0]
            
            # Cargar detalle
            self.loadDetalleVenta(venta[0])

    def loadDetalleVenta(self, venta_id):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM detalle_venta WHERE ven_id = %s", (venta_id,))
            self.detalle_venta_data = cursor.fetchall()
            self.detalle_venta_model.refreshData(self.detalle_venta_data)
            
            # Configurar botones de acción
            for row in range(len(self.detalle_venta_data)):
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(2, 2, 2, 2)
                
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(25)
                edit_btn.clicked.connect(lambda _, r=row: self.editDetalleVenta(r))
                layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(25)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteDetalleVenta(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                self.detalle_venta_table.setIndexWidget(self.detalle_venta_model.index(row, 4), widget)
            
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar detalle: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    # Métodos CRUD para Ventas
    def addVenta(self):
        dialog = VentaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getVentaData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO venta (ven_cliente, ven_usu_id, ven_fecha_venta, ven_monto_total, ven_estado)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data["cliente"], self.usu_id, data["fecha"], 
                    data["monto_total"], data["estado"]
                ))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Venta creada correctamente")
                self.loadVentas()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al crear venta: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editVenta(self, row):
        record = self.ventas_data[row]
        dialog = VentaDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getVentaData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                UPDATE venta 
                SET ven_cliente = %s, ven_fecha_venta = %s, ven_monto_total = %s, ven_estado = %s
                WHERE ven_id = %s
                """
                cursor.execute(query, (
                    data["cliente"], data["fecha"],
                    data["monto_total"], data["estado"], record[0]
                ))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Venta actualizada correctamente")
                self.loadVentas()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar venta: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteVenta(self, row):
        record = self.ventas_data[row]
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la venta {record[0]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                
                # Eliminar detalles primero
                cursor.execute("DELETE FROM detalle_venta WHERE ven_id = %s", (record[0],))
                # Eliminar venta
                cursor.execute("DELETE FROM venta WHERE ven_id = %s", (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Venta eliminada correctamente")
                self.loadVentas()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar venta: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def addDetalleVenta(self):
        if not self.selected_venta_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una venta primero")
            return
            
        dialog = DetalleDialog(self, inventario_items=self.inventario_items, tipo="venta")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getDetalleData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                INSERT INTO detalle_venta (ven_id, inv_id, cantidad)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (self.selected_venta_id, data["inventario_id"], data["cantidad"]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto agregado al detalle")
                self.loadDetalleVenta(self.selected_venta_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editDetalleVenta(self, row):
        record = self.detalle_venta_data[row]
        dialog = DetalleDialog(self, record, self.inventario_items, "venta")
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getDetalleData()
            
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                query = """
                UPDATE detalle_venta 
                SET inv_id = %s, cantidad = %s
                WHERE dv_id = %s
                """
                cursor.execute(query, (data["inventario_id"], data["cantidad"], record[0]))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Detalle actualizado correctamente")
                self.loadDetalleVenta(self.selected_venta_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteDetalleVenta(self, row):
        record = self.detalle_venta_data[row]
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
                cursor.execute("DELETE FROM detalle_venta WHERE dv_id = %s", (record[0],))
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto eliminado del detalle")
                self.loadDetalleVenta(self.selected_venta_id)
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar detalle: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def completarVenta(self):
        if not self.selected_venta_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione una venta primero")
            return
            
        # Verificar que la venta tenga detalles
        if not self.detalle_venta_data:
            QMessageBox.warning(self, "Advertencia", "La venta debe tener productos en el detalle antes de completarla")
            return
            
        reply = QMessageBox.question(
            self, "Completar Venta",
            "¿Está seguro que desea completar esta venta? Esto actualizará el inventario.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
            try:
                cursor = self.db_connection.cursor()
                
                # Actualizar estado de la venta
                cursor.execute("UPDATE venta SET ven_estado = 'Completada' WHERE ven_id = %s", 
                             (self.selected_venta_id,))
                
                # Actualizar inventario con las cantidades ventadas
                for detalle in self.detalle_venta_data:
                    inv_id = detalle[2]
                    cantidad_ventada = detalle[3]
                    
                    cursor.execute("""
                        UPDATE inventario 
                        SET inv_cantidad = inv_cantidad - %s 
                        WHERE inv_id = %s
                    """, (cantidad_ventada, inv_id))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Venta completada e inventario actualizado")
                self.loadVentas()
                self.loadInventarioItems()  # Recargar inventario actualizado
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al completar venta: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    # Métodos para cargar datos del reporte
    def loadReportesData(self):
        self.loadCotizacionesPendientes()
        self.loadVentasCompletadas()
        self.generarReporteMensual()

    def loadCotizacionesPendientes(self):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM venta WHERE ven_estado = 'Pendiente'")
            self.cotizaciones_model.refreshData(cursor.fetchall())
            self.ajustarColumnas(self.cotizaciones_table)
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar ventas: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadVentasCompletadas(self):
        if not self.connectToDatabase():
            return
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM venta WHERE ven_estado = 'Completada'")
            datos = cursor.fetchall()
            self.ventas_completadas_model.refreshData(datos)
            self.ajustarColumnas(self.ventas_completadas_table)
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar ventas: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def generarReporteMensual(self):
        if not self.connectToDatabase():
            return
        try:
            fecha = self.date_edit_reporte.date()
            inicio_mes = QDate(fecha.year(), fecha.month(), 1)
            fin_mes = inicio_mes.addMonths(1).addDays(-1)

            cursor = self.db_connection.cursor()
            query = """
            SELECT ven_fecha_venta, ven_monto_total 
            FROM venta 
            WHERE ven_fecha_venta BETWEEN %s AND %s
            ORDER BY ven_fecha_venta
            """
            cursor.execute(query, (
                inicio_mes.toString("yyyy-MM-dd"),
                fin_mes.toString("yyyy-MM-dd")
            ))
            
            self.reporte_mensual_model.clear()
            self.reporte_mensual_model.setHorizontalHeaderLabels(["Fecha Venta", "Monto Total"])
            
            for row in cursor.fetchall():
                fecha = QStandardItem(row[0].strftime("%d-%m-%Y"))
                monto = QStandardItem(f"${row[1]:,.2f}")
                self.reporte_mensual_model.appendRow([fecha, monto])
                
            self.ajustarColumnas(self.reporte_mensual_table)
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {err}")

    def ajustarColumnas(self, tabla):
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.verticalHeader().setVisible(False)

    def logout(self):
        self.close()
        self.loginWindow.show()