import sys
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTableView, QHeaderView, QToolBar, QAction, QLabel, QSplitter,
                            QApplication, QFrame, QGridLayout, QSizePolicy, QStackedWidget,
                            QMessageBox, QDateEdit, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QDate, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Modelo base para todas las tablas
class GenericTableModel(QAbstractTableModel):
    def __init__(self, data=None, headers=None):
        super().__init__()
        self._data = data if data is not None else []
        self._headers = headers if headers is not None else []
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            value = self._data[index.row()][index.column()]
            
            # Formato para fechas
            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
                
            # Formato para valores monetarios
            if isinstance(value, float) and any(h.lower().find('monto') >= 0 or h.lower().find('salario') >= 0 for h in self._headers):
                if index.column() < len(self._headers) and (
                    'monto' in self._headers[index.column()].lower() or 
                    'salario' in self._headers[index.column()].lower() or
                    'costo' in self._headers[index.column()].lower()):
                    return f"${value:,.2f}"
                
            return str(value)
            
        elif role == Qt.TextAlignmentRole:
            # Alinear valores monetarios a la derecha
            if index.column() < len(self._headers) and (
                'monto' in self._headers[index.column()].lower() or 
                'salario' in self._headers[index.column()].lower() or
                'costo' in self._headers[index.column()].lower() or
                'cantidad' in self._headers[index.column()].lower()):
                return Qt.AlignRight | Qt.AlignVCenter
                
        return None
        
    def rowCount(self, parent=None):
        return len(self._data)
        
    def columnCount(self, parent=None):
        return len(self._headers) if self._headers else 0
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self._headers):
            return self._headers[section]
        return None
        
    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


# Gráfico genérico para visualizaciones
class GenericChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def plot_bar_chart(self, labels, values, title, xlabel, ylabel, color='#c1272d'):
        self.axes.clear()
        self.axes.bar(labels, values, color=color)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Rotar etiquetas para mejor legibilidad
        plt.setp(self.axes.get_xticklabels(), rotation=45, ha='right')
        
        # Formato para valores monetarios si es necesario
        if any(isinstance(v, float) for v in values) and ('monto' in ylabel.lower() or 'costo' in ylabel.lower()):
            self.axes.yaxis.set_major_formatter('${x:,.0f}')
            
        self.fig.tight_layout()
        self.draw()
        
    def plot_pie_chart(self, labels, values, title):
        self.axes.clear()
        
        # Colores para el gráfico de pastel
        colors = ['#c1272d', '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#607D8B', '#795548', '#E91E63']
        
        # Explotar la primera rebanada
        explode = [0.1] + [0] * (len(labels) - 1) if len(labels) > 0 else []
        
        self.axes.pie(values, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        self.axes.axis('equal')  # Asegura que el pastel sea un círculo
        
        self.axes.set_title(title)
        
        self.fig.tight_layout()
        self.draw()


class GestionWindow(QMainWindow):
    def __init__(self, loginWindow):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.db_connection = None
        self.initUI()
        
    def initUI(self):
        # Propiedades de la ventana
        #self.setWindowTitle("Sistema de Gestión Integral - Grupo Porteo")
        self.setWindowTitle("Modulo de Gestión - Grupo Porteo")
        self.showMaximized()  # Pantalla completa
        
        # Estilo de la aplicación
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: Arial;
            }
            QTableView {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: #c1272d;
                selection-color: white;
            }
            QTableView::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #c1272d;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #c1272d;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a01c21;
            }
            QPushButton:pressed {
                background-color: #7d161a;
            }
            QPushButton#activeModule {
                background-color: #7d161a;
                border-bottom: 3px solid white;
            }
            QToolBar {
                background-color: #c1272d;
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
            QComboBox, QDateEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLabel#moduleTitle {
                font-size: 20px;
                font-weight: bold;
                color: #c1272d;
                padding: 10px 0;
            }
        """)
        
        # Toolbar superior
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Logo en la toolbar
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo-Grupo-Porteo.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        self.toolbar.addWidget(logo_label)
        
        # Título en la toolbar
        title_label = QLabel("Sistema de Gestión Integral")
        title_label.setObjectName("titleLabel")
        self.toolbar.addWidget(title_label)
        
        self.toolbar.addSeparator()
        
        # Botones de módulos
        self.btn_finanzas = QPushButton("Finanzas")
        self.btn_finanzas.setCursor(Qt.PointingHandCursor)
        self.btn_finanzas.clicked.connect(lambda: self.cambiarModulo(0, self.btn_finanzas))
        self.toolbar.addWidget(self.btn_finanzas)
        
        self.btn_rrhh = QPushButton("Recursos Humanos")
        self.btn_rrhh.setCursor(Qt.PointingHandCursor)
        self.btn_rrhh.clicked.connect(lambda: self.cambiarModulo(1, self.btn_rrhh))
        self.toolbar.addWidget(self.btn_rrhh)
        
        self.btn_logistica = QPushButton("Logística")
        self.btn_logistica.setCursor(Qt.PointingHandCursor)
        self.btn_logistica.clicked.connect(lambda: self.cambiarModulo(2, self.btn_logistica))
        self.toolbar.addWidget(self.btn_logistica)
        
        self.btn_compras = QPushButton("Compras")
        self.btn_compras.setCursor(Qt.PointingHandCursor)
        self.btn_compras.clicked.connect(lambda: self.cambiarModulo(3, self.btn_compras))
        self.toolbar.addWidget(self.btn_compras)
        
        self.btn_ventas = QPushButton("Ventas")
        self.btn_ventas.setCursor(Qt.PointingHandCursor)
        self.btn_ventas.clicked.connect(lambda: self.cambiarModulo(4, self.btn_ventas))
        self.toolbar.addWidget(self.btn_ventas)
        
        self.btn_mantenimiento = QPushButton("Mantenimiento")
        self.btn_mantenimiento.setCursor(Qt.PointingHandCursor)
        self.btn_mantenimiento.clicked.connect(lambda: self.cambiarModulo(5, self.btn_mantenimiento))
        self.toolbar.addWidget(self.btn_mantenimiento)
        
        # Lista de botones para gestionar el estilo activo
        self.module_buttons = [
            self.btn_finanzas, self.btn_rrhh, self.btn_logistica,
            self.btn_compras, self.btn_ventas, self.btn_mantenimiento
        ]
        
        # Spacer para el botón de cerrar sesión
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setStyleSheet("background-color: transparent;")
        self.toolbar.addWidget(spacer)
        
        # Botón de cerrar sesión
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        self.toolbar.addWidget(self.logout_btn)
        
        # Widget apilado para los diferentes módulos
        self.stacked_widget = QStackedWidget()
        
        # Crear las vistas para cada módulo
        self.setupFinanzasView()
        self.setupRRHHView()
        self.setupLogisticaView()
        self.setupComprasView()
        self.setupVentasView()
        self.setupMantenimientoView()
        
        # Widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(central_widget)
        
        # Iniciar con el módulo de finanzas activo
        self.cambiarModulo(0, self.btn_finanzas)
        
    def setupFinanzasView(self):
        # Widget para el módulo de Finanzas
        finanzas_widget = QWidget()
        layout = QVBoxLayout(finanzas_widget)
        
        # Título del módulo
        title_label = QLabel("Gestión de Finanzas")
        title_label.setObjectName("moduleTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        # Filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QFormLayout(filter_frame)
        
        # Filtro por tipo
        self.finanzas_tipo_combo = QComboBox()
        self.finanzas_tipo_combo.addItems(["Todos", "Ingresos", "Gastos"])
        filter_layout.addRow("Tipo:", self.finanzas_tipo_combo)
        
        # Filtro por fecha
        self.finanzas_fecha_inicio = QDateEdit()
        self.finanzas_fecha_inicio.setCalendarPopup(True)
        self.finanzas_fecha_inicio.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addRow("Fecha inicio:", self.finanzas_fecha_inicio)
        
        self.finanzas_fecha_fin = QDateEdit()
        self.finanzas_fecha_fin.setCalendarPopup(True)
        self.finanzas_fecha_fin.setDate(QDate.currentDate())
        filter_layout.addRow("Fecha fin:", self.finanzas_fecha_fin)
        
        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.cargarDatosFinanzas)
        filter_layout.addRow("", search_btn)
        
        layout.addWidget(filter_frame)
        
        # Splitter para tabla y gráficos
        splitter = QSplitter(Qt.Vertical)
        
        # Tabla de finanzas
        self.finanzas_table = QTableView()
        self.finanzas_table.setAlternatingRowColors(True)
        self.finanzas_table.setSelectionBehavior(QTableView.SelectRows)
        self.finanzas_table.setEditTriggers(QTableView.NoEditTriggers)
        self.finanzas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.finanzas_table.verticalHeader().setVisible(False)
        self.finanzas_table.setSortingEnabled(True)
        
        # Modelo para la tabla
        self.finanzas_model = GenericTableModel(
            headers=["ID", "Usuario", "Fecha", "Descripción", "Monto", "Tipo"]
        )
        self.finanzas_table.setModel(self.finanzas_model)
        
        splitter.addWidget(self.finanzas_table)
        
        # Frame para gráficos
        charts_frame = QFrame()
        charts_frame.setObjectName("chartFrame")
        charts_layout = QGridLayout(charts_frame)
        
        # Gráficos
        self.finanzas_bar_chart = GenericChart(width=8, height=4)
        charts_layout.addWidget(self.finanzas_bar_chart, 0, 0)
        
        self.finanzas_pie_chart = GenericChart(width=4, height=4)
        charts_layout.addWidget(self.finanzas_pie_chart, 0, 1)
        
        splitter.addWidget(charts_frame)
        
        # Configurar tamaños iniciales
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        
        self.stacked_widget.addWidget(finanzas_widget)
        
    def setupRRHHView(self):
        # Widget para el módulo de RRHH
        rrhh_widget = QWidget()
        layout = QVBoxLayout(rrhh_widget)
        
        # Título del módulo
        title_label = QLabel("Gestión de Recursos Humanos")
        title_label.setObjectName("moduleTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Pestañas para las diferentes tablas
        tabs_layout = QHBoxLayout()
        
        # Botones para cambiar entre tablas
        self.btn_usuarios = QPushButton("Usuarios")
        self.btn_usuarios.clicked.connect(lambda: self.cambiarTablaRRHH(0))
        tabs_layout.addWidget(self.btn_usuarios)
        
        self.btn_rrhh_data = QPushButton("Datos RRHH")
        self.btn_rrhh_data.clicked.connect(lambda: self.cambiarTablaRRHH(1))
        tabs_layout.addWidget(self.btn_rrhh_data)
        
        self.btn_evaluaciones = QPushButton("Evaluaciones")
        self.btn_evaluaciones.clicked.connect(lambda: self.cambiarTablaRRHH(2))
        tabs_layout.addWidget(self.btn_evaluaciones)
        
        layout.addLayout(tabs_layout)
        
        # Widget apilado para las tablas
        self.rrhh_stacked = QStackedWidget()
        
        # Tabla de usuarios
        usuarios_widget = QWidget()
        usuarios_layout = QVBoxLayout(usuarios_widget)
        
        self.usuarios_table = QTableView()
        self.usuarios_table.setAlternatingRowColors(True)
        self.usuarios_table.setSelectionBehavior(QTableView.SelectRows)
        self.usuarios_table.setEditTriggers(QTableView.NoEditTriggers)
        self.usuarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usuarios_table.verticalHeader().setVisible(False)
        self.usuarios_table.setSortingEnabled(True)
        
        self.usuarios_model = GenericTableModel(
            headers=["ID", "Nombre", "Correo", "Puesto", "Fecha Contratación", "Salario", "Módulo"]
        )
        self.usuarios_table.setModel(self.usuarios_model)
        
        usuarios_layout.addWidget(self.usuarios_table)
        self.rrhh_stacked.addWidget(usuarios_widget)
        
        # Tabla de datos RRHH
        rrhh_data_widget = QWidget()
        rrhh_data_layout = QVBoxLayout(rrhh_data_widget)
        
        self.rrhh_data_table = QTableView()
        self.rrhh_data_table.setAlternatingRowColors(True)
        self.rrhh_data_table.setSelectionBehavior(QTableView.SelectRows)
        self.rrhh_data_table.setEditTriggers(QTableView.NoEditTriggers)
        self.rrhh_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rrhh_data_table.verticalHeader().setVisible(False)
        self.rrhh_data_table.setSortingEnabled(True)
        
        self.rrhh_data_model = GenericTableModel(
            headers=["ID", "Usuario ID", "Estado", "Tipo Contrato", "Beneficios", "Observaciones"]
        )
        self.rrhh_data_table.setModel(self.rrhh_data_model)
        
        rrhh_data_layout.addWidget(self.rrhh_data_table)
        self.rrhh_stacked.addWidget(rrhh_data_widget)
        
        # Tabla de evaluaciones
        evaluaciones_widget = QWidget()
        evaluaciones_layout = QVBoxLayout(evaluaciones_widget)
        
        self.evaluaciones_table = QTableView()
        self.evaluaciones_table.setAlternatingRowColors(True)
        self.evaluaciones_table.setSelectionBehavior(QTableView.SelectRows)
        self.evaluaciones_table.setEditTriggers(QTableView.NoEditTriggers)
        self.evaluaciones_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.evaluaciones_table.verticalHeader().setVisible(False)
        self.evaluaciones_table.setSortingEnabled(True)
        
        self.evaluaciones_model = GenericTableModel(
            headers=["ID", "Usuario ID", "Fecha", "Puntaje", "Comentarios"]
        )
        self.evaluaciones_table.setModel(self.evaluaciones_model)
        
        evaluaciones_layout.addWidget(self.evaluaciones_table)
        self.rrhh_stacked.addWidget(evaluaciones_widget)
        
        layout.addWidget(self.rrhh_stacked)
        
        # Gráfico para RRHH
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.rrhh_chart = GenericChart(width=10, height=4)
        chart_layout.addWidget(self.rrhh_chart)
        
        layout.addWidget(chart_frame)
        
        self.stacked_widget.addWidget(rrhh_widget)
        
    def setupLogisticaView(self):
        # Widget para el módulo de Logística
        logistica_widget = QWidget()
        layout = QVBoxLayout(logistica_widget)
        
        # Título del módulo
        title_label = QLabel("Gestión de Logística")
        title_label.setObjectName("moduleTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Pestañas para las diferentes tablas
        tabs_layout = QHBoxLayout()
        
        # Botones para cambiar entre tablas
        self.btn_logistica_main = QPushButton("Logística")
        self.btn_logistica_main.clicked.connect(lambda: self.cambiarTablaLogistica(0))
        tabs_layout.addWidget(self.btn_logistica_main)
        
        self.btn_almacenes = QPushButton("Almacenes")
        self.btn_almacenes.clicked.connect(lambda: self.cambiarTablaLogistica(1))
        tabs_layout.addWidget(self.btn_almacenes)
        
        self.btn_inventario = QPushButton("Inventario")
        self.btn_inventario.clicked.connect(lambda: self.cambiarTablaLogistica(2))
        tabs_layout.addWidget(self.btn_inventario)
        
        layout.addLayout(tabs_layout)
        
        # Widget apilado para las tablas
        self.logistica_stacked = QStackedWidget()
        
        # Tabla de logística
        logistica_main_widget = QWidget()
        logistica_main_layout = QVBoxLayout(logistica_main_widget)
        
        self.logistica_table = QTableView()
        self.logistica_table.setAlternatingRowColors(True)
        self.logistica_table.setSelectionBehavior(QTableView.SelectRows)
        self.logistica_table.setEditTriggers(QTableView.NoEditTriggers)
        self.logistica_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logistica_table.verticalHeader().setVisible(False)
        self.logistica_table.setSortingEnabled(True)
        
        self.logistica_model = GenericTableModel(
            headers=["ID", "Usuario ID", "Origen", "Destino", "Fecha Salida", "Fecha Llegada", "Estado"]
        )
        self.logistica_table.setModel(self.logistica_model)
        
        logistica_main_layout.addWidget(self.logistica_table)
        self.logistica_stacked.addWidget(logistica_main_widget)
        
        # Tabla de almacenes
        almacenes_widget = QWidget()
        almacenes_layout = QVBoxLayout(almacenes_widget)
        
        self.almacenes_table = QTableView()
        self.almacenes_table.setAlternatingRowColors(True)
        self.almacenes_table.setSelectionBehavior(QTableView.SelectRows)
        self.almacenes_table.setEditTriggers(QTableView.NoEditTriggers)
        self.almacenes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.almacenes_table.verticalHeader().setVisible(False)
        self.almacenes_table.setSortingEnabled(True)
        
        self.almacenes_model = GenericTableModel(
            headers=["ID", "Nombre", "Ubicación"]
        )
        self.almacenes_table.setModel(self.almacenes_model)
        
        almacenes_layout.addWidget(self.almacenes_table)
        self.logistica_stacked.addWidget(almacenes_widget)
        
        # Tabla de inventario
        inventario_widget = QWidget()
        inventario_layout = QVBoxLayout(inventario_widget)
        
        self.inventario_table = QTableView()
        self.inventario_table.setAlternatingRowColors(True)
        self.inventario_table.setSelectionBehavior(QTableView.SelectRows)
        self.inventario_table.setEditTriggers(QTableView.NoEditTriggers)
        self.inventario_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventario_table.verticalHeader().setVisible(False)
        self.inventario_table.setSortingEnabled(True)
        
        self.inventario_model = GenericTableModel(
            headers=["ID", "Almacén ID", "Producto", "Cantidad"]
        )
        self.inventario_table.setModel(self.inventario_model)
        
        inventario_layout.addWidget(self.inventario_table)
        self.logistica_stacked.addWidget(inventario_widget)
        
        layout.addWidget(self.logistica_stacked)
        
        # Gráfico para Logística
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.logistica_chart = GenericChart(width=10, height=4)
        chart_layout.addWidget(self.logistica_chart)
        
        layout.addWidget(chart_frame)
        
        self.stacked_widget.addWidget(logistica_widget)
        
    def setupComprasView(self):
        # Widget para el módulo de Compras
        compras_widget = QWidget()
        layout = QVBoxLayout(compras_widget)
        
        # Título del módulo
        title_label = QLabel("Gestión de Compras")
        title_label.setObjectName("moduleTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Pestañas para las diferentes tablas
        tabs_layout = QHBoxLayout()
        
        # Botones para cambiar entre tablas
        self.btn_solicitudes = QPushButton("Solicitudes")
        self.btn_solicitudes.clicked.connect(lambda: self.cambiarTablaCompras(0))
        tabs_layout.addWidget(self.btn_solicitudes)
        
        self.btn_compras_main = QPushButton("Compras")
        self.btn_compras_main.clicked.connect(lambda: self.cambiarTablaCompras(1))
        tabs_layout.addWidget(self.btn_compras_main)
        
        self.btn_detalle_compra = QPushButton("Detalle Compras")
        self.btn_detalle_compra.clicked.connect(lambda: self.cambiarTablaCompras(2))
        tabs_layout.addWidget(self.btn_detalle_compra)
        
        self.btn_detalle_solicitud = QPushButton("Detalle Solicitudes")
        self.btn_detalle_solicitud.clicked.connect(lambda: self.cambiarTablaCompras(3))
        tabs_layout.addWidget(self.btn_detalle_solicitud)
        
        layout.addLayout(tabs_layout)
        
        # Widget apilado para las tablas
        self.compras_stacked = QStackedWidget()
        
        # Tabla de solicitudes
        solicitudes_widget = QWidget()
        solicitudes_layout = QVBoxLayout(solicitudes_widget)
        
        self.solicitudes_table = QTableView()
        self.solicitudes_table.setAlternatingRowColors(True)
        self.solicitudes_table.setSelectionBehavior(QTableView.SelectRows)
        self.solicitudes_table.setEditTriggers(QTableView.NoEditTriggers)
        self.solicitudes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.solicitudes_table.verticalHeader().setVisible(False)
        self.solicitudes_table.setSortingEnabled(True)
        
        self.solicitudes_model = GenericTableModel(
            headers=["ID", "Usuario ID", "Fecha", "Descripción", "Estado"]
        )
        self.solicitudes_table.setModel(self.solicitudes_model)
        
        solicitudes_layout.addWidget(self.solicitudes_table)
        self.compras_stacked.addWidget(solicitudes_widget)
        
        # Tabla de compras
        compras_main_widget = QWidget()
        compras_main_layout = QVBoxLayout(compras_main_widget)
        
        self.compras_table = QTableView()
        self.compras_table.setAlternatingRowColors(True)
        self.compras_table.setSelectionBehavior(QTableView.SelectRows)
        self.compras_table.setEditTriggers(QTableView.NoEditTriggers)
        self.compras_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.compras_table.verticalHeader().setVisible(False)
        self.compras_table.setSortingEnabled(True)
        
        self.compras_model = GenericTableModel(
            headers=["ID", "Proveedor", "Usuario ID", "Fecha", "Solicitud ID", "Monto Total", "Estado"]
        )
        self.compras_table.setModel(self.compras_model)
        
        compras_main_layout.addWidget(self.compras_table)
        self.compras_stacked.addWidget(compras_main_widget)
        
        # Tabla de detalle de compra
        detalle_compra_widget = QWidget()
        detalle_compra_layout = QVBoxLayout(detalle_compra_widget)
        
        self.detalle_compra_table = QTableView()
        self.detalle_compra_table.setAlternatingRowColors(True)
        self.detalle_compra_table.setSelectionBehavior(QTableView.SelectRows)
        self.detalle_compra_table.setEditTriggers(QTableView.NoEditTriggers)
        self.detalle_compra_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_compra_table.verticalHeader().setVisible(False)
        self.detalle_compra_table.setSortingEnabled(True)
        
        self.detalle_compra_model = GenericTableModel(
            headers=["ID", "Compra ID", "Inventario ID", "Cantidad"]
        )
        self.detalle_compra_table.setModel(self.detalle_compra_model)
        
        detalle_compra_layout.addWidget(self.detalle_compra_table)
        self.compras_stacked.addWidget(detalle_compra_widget)
        
        # Tabla de detalle de solicitud
        detalle_solicitud_widget = QWidget()
        detalle_solicitud_layout = QVBoxLayout(detalle_solicitud_widget)
        
        self.detalle_solicitud_table = QTableView()
        self.detalle_solicitud_table.setAlternatingRowColors(True)
        self.detalle_solicitud_table.setSelectionBehavior(QTableView.SelectRows)
        self.detalle_solicitud_table.setEditTriggers(QTableView.NoEditTriggers)
        self.detalle_solicitud_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_solicitud_table.verticalHeader().setVisible(False)
        self.detalle_solicitud_table.setSortingEnabled(True)
        
        self.detalle_solicitud_model = GenericTableModel(
            headers=["ID", "Solicitud ID", "Inventario ID", "Cantidad"]
        )
        self.detalle_solicitud_table.setModel(self.detalle_solicitud_model)
        
        detalle_solicitud_layout.addWidget(self.detalle_solicitud_table)
        self.compras_stacked.addWidget(detalle_solicitud_widget)
        
        layout.addWidget(self.compras_stacked)
        
        # Gráfico para Compras
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.compras_chart = GenericChart(width=10, height=4)
        chart_layout.addWidget(self.compras_chart)
        
        layout.addWidget(chart_frame)
        
        self.stacked_widget.addWidget(compras_widget)
        
    def setupVentasView(self):
        # Widget para el módulo de Ventas
        ventas_widget = QWidget()
        layout = QVBoxLayout(ventas_widget)
        
        # Título del módulo
        title_label = QLabel("Gestión de Ventas")
        title_label.setObjectName("moduleTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Pestañas para las diferentes tablas
        tabs_layout = QHBoxLayout()
        
        # Botones para cambiar entre tablas
        self.btn_ventas_main = QPushButton("Ventas")
        self.btn_ventas_main.clicked.connect(lambda: self.cambiarTablaVentas(0))
        tabs_layout.addWidget(self.btn_ventas_main)
        
        self.btn_detalle_venta = QPushButton("Detalle Ventas")
        self.btn_detalle_venta.clicked.connect(lambda: self.cambiarTablaVentas(1))
        tabs_layout.addWidget(self.btn_detalle_venta)
        
        layout.addLayout(tabs_layout)
        
        # Widget apilado para las tablas
        self.ventas_stacked = QStackedWidget()
        
        # Tabla de ventas
        ventas_main_widget = QWidget()
        ventas_main_layout = QVBoxLayout(ventas_main_widget)
        
        self.ventas_table = QTableView()
        self.ventas_table.setAlternatingRowColors(True)
        self.ventas_table.setSelectionBehavior(QTableView.SelectRows)
        self.ventas_table.setEditTriggers(QTableView.NoEditTriggers)
        self.ventas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ventas_table.verticalHeader().setVisible(False)
        self.ventas_table.setSortingEnabled(True)
        
        self.ventas_model = GenericTableModel(
            headers=["ID", "Cliente", "Usuario ID", "Fecha", "Monto Total", "Estado"]
        )
        self.ventas_table.setModel(self.ventas_model)
        
        ventas_main_layout.addWidget(self.ventas_table)
        self.ventas_stacked.addWidget(ventas_main_widget)
        
        # Tabla de detalle de venta
        detalle_venta_widget = QWidget()
        detalle_venta_layout = QVBoxLayout(detalle_venta_widget)
        
        self.detalle_venta_table = QTableView()
        self.detalle_venta_table.setAlternatingRowColors(True)
        self.detalle_venta_table.setSelectionBehavior(QTableView.SelectRows)
        self.detalle_venta_table.setEditTriggers(QTableView.NoEditTriggers)
        self.detalle_venta_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detalle_venta_table.verticalHeader().setVisible(False)
        self.detalle_venta_table.setSortingEnabled(True)
        
        self.detalle_venta_model = GenericTableModel(
            headers=["ID", "Venta ID", "Inventario ID", "Cantidad"]
        )
        self.detalle_venta_table.setModel(self.detalle_venta_model)
        
        detalle_venta_layout.addWidget(self.detalle_venta_table)
        self.ventas_stacked.addWidget(detalle_venta_widget)
        
        layout.addWidget(self.ventas_stacked)
        
        # Gráfico para Ventas
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.ventas_chart = GenericChart(width=10, height=4)
        chart_layout.addWidget(self.ventas_chart)
        
        layout.addWidget(chart_frame)
        
        self.stacked_widget.addWidget(ventas_widget)
        
    def setupMantenimientoView(self):
        # Widget para el módulo de Mantenimiento
        mantenimiento_widget = QWidget()
        layout = QVBoxLayout(mantenimiento_widget)
        
        # Título del módulo
        title_label = QLabel("Gestión de Mantenimiento")
        title_label.setObjectName("moduleTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Pestañas para las diferentes tablas
        tabs_layout = QHBoxLayout()
        
        # Botones para cambiar entre tablas
        self.btn_mantenimiento_main = QPushButton("Mantenimiento")
        self.btn_mantenimiento_main.clicked.connect(lambda: self.cambiarTablaMantenimiento(0))
        tabs_layout.addWidget(self.btn_mantenimiento_main)
        
        self.btn_incidencias = QPushButton("Incidencias")
        self.btn_incidencias.clicked.connect(lambda: self.cambiarTablaMantenimiento(1))
        tabs_layout.addWidget(self.btn_incidencias)
        
        layout.addLayout(tabs_layout)
        
        # Widget apilado para las tablas
        self.mantenimiento_stacked = QStackedWidget()
        
        # Tabla de mantenimiento
        mantenimiento_main_widget = QWidget()
        mantenimiento_main_layout = QVBoxLayout(mantenimiento_main_widget)
        
        self.mantenimiento_table = QTableView()
        self.mantenimiento_table.setAlternatingRowColors(True)
        self.mantenimiento_table.setSelectionBehavior(QTableView.SelectRows)
        self.mantenimiento_table.setEditTriggers(QTableView.NoEditTriggers)
        self.mantenimiento_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mantenimiento_table.verticalHeader().setVisible(False)
        self.mantenimiento_table.setSortingEnabled(True)
        
        self.mantenimiento_model = GenericTableModel(
            headers=["ID", "Vehículo ID", "Usuario ID", "Fecha Programada", "Descripción", "Costo", "Estado"]
        )
        self.mantenimiento_table.setModel(self.mantenimiento_model)
        
        mantenimiento_main_layout.addWidget(self.mantenimiento_table)
        self.mantenimiento_stacked.addWidget(mantenimiento_main_widget)
        
        # Tabla de incidencias
        incidencias_widget = QWidget()
        incidencias_layout = QVBoxLayout(incidencias_widget)
        
        self.incidencias_table = QTableView()
        self.incidencias_table.setAlternatingRowColors(True)
        self.incidencias_table.setSelectionBehavior(QTableView.SelectRows)
        self.incidencias_table.setEditTriggers(QTableView.NoEditTriggers)
        self.incidencias_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.incidencias_table.verticalHeader().setVisible(False)
        self.incidencias_table.setSortingEnabled(True)
        
        self.incidencias_model = GenericTableModel(
            headers=["ID", "Usuario ID", "Fecha", "Descripción", "Estado"]
        )
        self.incidencias_table.setModel(self.incidencias_model)
        
        incidencias_layout.addWidget(self.incidencias_table)
        self.mantenimiento_stacked.addWidget(incidencias_widget)
        
        layout.addWidget(self.mantenimiento_stacked)
        
        # Gráfico para Mantenimiento
        chart_frame = QFrame()
        chart_frame.setObjectName("chartFrame")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.mantenimiento_chart = GenericChart(width=10, height=4)
        chart_layout.addWidget(self.mantenimiento_chart)
        
        layout.addWidget(chart_frame)
        
        self.stacked_widget.addWidget(mantenimiento_widget)
        
    def cambiarModulo(self, index, button):
        # Cambiar al módulo seleccionado
        self.stacked_widget.setCurrentIndex(index)
        
        # Actualizar estilo de botones
        for btn in self.module_buttons:
            btn.setObjectName("")
            btn.setStyleSheet("")
        
        button.setObjectName("activeModule")
        button.setStyleSheet("")
        
        # Cargar datos del módulo seleccionado
        if index == 0:  # Finanzas
            self.cargarDatosFinanzas()
        elif index == 1:  # RRHH
            self.cargarDatosRRHH()
            self.cambiarTablaRRHH(0)  # Iniciar con la tabla de usuarios
        elif index == 2:  # Logística
            self.cargarDatosLogistica()
            self.cambiarTablaLogistica(0)  # Iniciar con la tabla de logística
        elif index == 3:  # Compras
            self.cargarDatosCompras()
            self.cambiarTablaCompras(0)  # Iniciar con la tabla de solicitudes
        elif index == 4:  # Ventas
            self.cargarDatosVentas()
            self.cambiarTablaVentas(0)  # Iniciar con la tabla de ventas
        elif index == 5:  # Mantenimiento
            self.cargarDatosMantenimiento()
            self.cambiarTablaMantenimiento(0)  # Iniciar con la tabla de mantenimiento
            
    def cambiarTablaRRHH(self, index):
        self.rrhh_stacked.setCurrentIndex(index)
        
    def cambiarTablaLogistica(self, index):
        self.logistica_stacked.setCurrentIndex(index)
        
    def cambiarTablaCompras(self, index):
        self.compras_stacked.setCurrentIndex(index)
        
    def cambiarTablaVentas(self, index):
        self.ventas_stacked.setCurrentIndex(index)
        
    def cambiarTablaMantenimiento(self, index):
        self.mantenimiento_stacked.setCurrentIndex(index)
        
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
            
    def cargarDatosFinanzas(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener filtros
            tipo_filtro = self.finanzas_tipo_combo.currentText()
            fecha_inicio = self.finanzas_fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.finanzas_fecha_fin.date().toString("yyyy-MM-dd")
            
            # Construir consulta según filtros
            query = "SELECT fin_id, fin_usu_id, fin_fecha, fin_desc, fin_monto, fin_tipo FROM finanza WHERE 1=1"
            params = []
            
            if tipo_filtro == "Ingresos":
                query += " AND fin_tipo = 'ingreso'"
            elif tipo_filtro == "Gastos":
                query += " AND fin_tipo = 'gasto'"
                
            query += " AND fin_fecha BETWEEN %s AND %s ORDER BY fin_fecha DESC"
            params.extend([fecha_inicio, fecha_fin])
            
            cursor.execute(query, params)
            finanzas_data = cursor.fetchall()
            
            # Actualizar modelo de tabla
            self.finanzas_model.refreshData(finanzas_data)
            
            # Cargar datos para gráficos
            cursor.execute("""
                SELECT DATE_FORMAT(fin_fecha, '%Y-%m') as mes, SUM(fin_monto) 
                FROM finanza 
                WHERE fin_tipo = 'ingreso' AND fin_fecha BETWEEN %s AND %s 
                GROUP BY mes 
                ORDER BY mes
            """, (fecha_inicio, fecha_fin))
            income_data = cursor.fetchall()
            
            cursor.execute("""
                SELECT DATE_FORMAT(fin_fecha, '%Y-%m') as mes, SUM(fin_monto) 
                FROM finanza 
                WHERE fin_tipo = 'gasto' AND fin_fecha BETWEEN %s AND %s 
                GROUP BY mes 
                ORDER BY mes
            """, (fecha_inicio, fecha_fin))
            expense_data = cursor.fetchall()
            
            # Datos para gráfico de barras
            meses = []
            ingresos = []
            gastos = []
            
            # Crear diccionarios para facilitar la búsqueda
            income_dict = {mes: monto for mes, monto in income_data}
            expense_dict = {mes: monto for mes, monto in expense_data}
            
            # Unir todos los meses únicos
            all_months = sorted(set(list(income_dict.keys()) + list(expense_dict.keys())))
            
            for mes in all_months:
                meses.append(mes)
                ingresos.append(income_dict.get(mes, 0))
                gastos.append(expense_dict.get(mes, 0))
            
            # Actualizar gráfico de barras
            if meses:
                # Crear datos para gráfico de barras comparativo
                import numpy as np
                x = np.arange(len(meses))
                width = 0.35
                
                self.finanzas_bar_chart.axes.clear()
                self.finanzas_bar_chart.axes.bar(x - width/2, ingresos, width, label='Ingresos', color='#4CAF50')
                self.finanzas_bar_chart.axes.bar(x + width/2, gastos, width, label='Gastos', color='#F44336')
                
                self.finanzas_bar_chart.axes.set_title('Ingresos vs Gastos por Mes')
                self.finanzas_bar_chart.axes.set_xlabel('Mes')
                self.finanzas_bar_chart.axes.set_ylabel('Monto ($)')
                self.finanzas_bar_chart.axes.set_xticks(x)
                self.finanzas_bar_chart.axes.set_xticklabels(meses)
                self.finanzas_bar_chart.axes.legend()
                
                # Formato para valores monetarios
                self.finanzas_bar_chart.axes.yaxis.set_major_formatter('${x:,.0f}')
                
                # Rotar etiquetas para mejor legibilidad
                plt.setp(self.finanzas_bar_chart.axes.get_xticklabels(), rotation=45, ha='right')
                
                self.finanzas_bar_chart.fig.tight_layout()
                self.finanzas_bar_chart.draw()
            
            # Datos para gráfico de pastel
            cursor.execute("""
                SELECT SUM(fin_monto) FROM finanza 
                WHERE fin_tipo = 'ingreso' AND fin_fecha BETWEEN %s AND %s
            """, (fecha_inicio, fecha_fin))
            total_ingresos = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT SUM(fin_monto) FROM finanza 
                WHERE fin_tipo = 'gasto' AND fin_fecha BETWEEN %s AND %s
            """, (fecha_inicio, fecha_fin))
            total_gastos = cursor.fetchone()[0] or 0
            
            # Actualizar gráfico de pastel
            self.finanzas_pie_chart.plot_pie_chart(
                ['Ingresos', 'Gastos'],
                [total_ingresos, total_gastos],
                'Distribución de Finanzas'
            )
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos de finanzas: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
                
    def cargarDatosRRHH(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Cargar datos de usuarios
            cursor.execute("""
                SELECT usu_id, usu_nombre, usu_correo, usu_puesto, 
                       usu_fecha_contratacion, usu_salario, usu_mod 
                FROM usuario 
                ORDER BY usu_id
            """)
            usuarios_data = cursor.fetchall()
            self.usuarios_model.refreshData(usuarios_data)
            
            # Cargar datos de RRHH
            cursor.execute("""
                SELECT reh_id, reh_usu_id, reh_estado, reh_tipo_contrato, 
                       reh_beneficios, reh_observaciones 
                FROM recursoshumanos 
                ORDER BY reh_id
            """)
            rrhh_data = cursor.fetchall()
            self.rrhh_data_model.refreshData(rrhh_data)
            
            # Cargar datos de evaluaciones
            cursor.execute("""
                SELECT eva_id, eva_usu_id, eva_fecha, eva_puntaje, eva_comentarios 
                FROM evaluacion_desempeno 
                ORDER BY eva_fecha DESC
            """)
            evaluaciones_data = cursor.fetchall()
            self.evaluaciones_model.refreshData(evaluaciones_data)
            
            # Datos para gráfico
            cursor.execute("""
                SELECT u.usu_mod, COUNT(*) 
                FROM usuario u 
                GROUP BY u.usu_mod 
                ORDER BY COUNT(*) DESC
            """)
            modulos_data = cursor.fetchall()
            
            if modulos_data:
                modulos = [mod for mod, _ in modulos_data]
                cantidades = [cant for _, cant in modulos_data]
                
                self.rrhh_chart.plot_bar_chart(
                    modulos, 
                    cantidades, 
                    'Distribución de Personal por Módulo',
                    'Módulo',
                    'Cantidad de Empleados',
                    '#3f51b5'  # Color azul para RRHH
                )
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos de RRHH: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
                
    def cargarDatosLogistica(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Cargar datos de logística
            cursor.execute("""
                SELECT log_id, log_usu_id, log_origen, log_destino, 
                       log_fecha_salida, log_fecha_llegada, log_estado 
                FROM logistica 
                ORDER BY log_fecha_salida DESC
            """)
            logistica_data = cursor.fetchall()
            self.logistica_model.refreshData(logistica_data)
            
            # Cargar datos de almacenes
            cursor.execute("""
                SELECT alm_id, alm_nombre, alm_ubicacion 
                FROM almacen 
                ORDER BY alm_id
            """)
            almacenes_data = cursor.fetchall()
            self.almacenes_model.refreshData(almacenes_data)
            
            # Cargar datos de inventario
            cursor.execute("""
                SELECT inv_id, inv_alm_id, inv_producto, inv_cantidad 
                FROM inventario 
                ORDER BY inv_id
            """)
            inventario_data = cursor.fetchall()
            self.inventario_model.refreshData(inventario_data)
            
            # Datos para gráfico
            cursor.execute("""
                SELECT log_estado, COUNT(*) 
                FROM logistica 
                GROUP BY log_estado
            """)
            estado_data = cursor.fetchall()
            
            if estado_data:
                estados = [estado for estado, _ in estado_data]
                cantidades = [cant for _, cant in estado_data]
                
                self.logistica_chart.plot_bar_chart(
                    estados, 
                    cantidades, 
                    'Estado de Envíos',
                    'Estado',
                    'Cantidad',
                    '#009688'  # Color verde-azulado para Logística
                )
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos de logística: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
                
    def cargarDatosCompras(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Cargar datos de solicitudes
            cursor.execute("""
                SELECT sol_id, sol_usu_id, sol_fecha, sol_descripcion, sol_estado 
                FROM solicitud_compra 
                ORDER BY sol_fecha DESC
            """)
            solicitudes_data = cursor.fetchall()
            self.solicitudes_model.refreshData(solicitudes_data)
            
            # Cargar datos de compras
            cursor.execute("""
                SELECT com_id, com_proveedor, com_usu_id, com_fecha_compra, 
                       com_sol_id, com_monto_total, com_estado 
                FROM compra 
                ORDER BY com_fecha_compra DESC
            """)
            compras_data = cursor.fetchall()
            self.compras_model.refreshData(compras_data)
            
            # Cargar datos de detalle de compra
            cursor.execute("""
                SELECT dc_id, com_id, inv_id, cantidad 
                FROM detalle_compra 
                ORDER BY dc_id
            """)
            detalle_compra_data = cursor.fetchall()
            self.detalle_compra_model.refreshData(detalle_compra_data)
            
            # Cargar datos de detalle de solicitud
            cursor.execute("""
                SELECT ds_id, sol_id, inv_id, cantidad 
                FROM detalle_solicitud 
                ORDER BY ds_id
            """)
            detalle_solicitud_data = cursor.fetchall()
            self.detalle_solicitud_model.refreshData(detalle_solicitud_data)
            
            # Datos para gráfico
            cursor.execute("""
                SELECT DATE_FORMAT(com_fecha_compra, '%Y-%m') as mes, SUM(com_monto_total) 
                FROM compra 
                GROUP BY mes 
                ORDER BY mes
            """)
            compras_por_mes = cursor.fetchall()
            
            if compras_por_mes:
                meses = [mes for mes, _ in compras_por_mes]
                montos = [monto for _, monto in compras_por_mes]
                
                self.compras_chart.plot_bar_chart(
                    meses, 
                    montos, 
                    'Compras por Mes',
                    'Mes',
                    'Monto Total ($)',
                    '#ff9800'  # Color naranja para Compras
                )
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos de compras: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
    

                
    def cargarDatosVentas(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Cargar datos de ventas
            cursor.execute("""
                SELECT ven_id, ven_cliente, ven_usu_id, ven_fecha_venta, 
                       ven_monto_total, ven_estado 
                FROM venta 
                ORDER BY ven_fecha_venta DESC
            """)
            ventas_data = cursor.fetchall()
            self.ventas_model.refreshData(ventas_data)
            
            # Cargar datos de detalle de venta
            cursor.execute("""
                SELECT dv_id, ven_id, inv_id, cantidad 
                FROM detalle_venta 
                ORDER BY dv_id
            """)
            detalle_venta_data = cursor.fetchall()
            self.detalle_venta_model.refreshData(detalle_venta_data)
            
            # Datos para gráfico
            cursor.execute("""
                SELECT DATE_FORMAT(ven_fecha_venta, '%Y-%m') as mes, SUM(ven_monto_total) 
                FROM venta 
                GROUP BY mes 
                ORDER BY mes
            """)
            ventas_por_mes = cursor.fetchall()
            
            if ventas_por_mes:
                meses = [mes for mes, _ in ventas_por_mes]
                montos = [monto for _, monto in ventas_por_mes]
                
                self.ventas_chart.plot_bar_chart(
                    meses, 
                    montos, 
                    'Ventas por Mes',
                    'Mes',
                    'Monto Total ($)',
                    '#4CAF50'  # Color verde para Ventas
                )
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos de ventas: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
                
    def cargarDatosMantenimiento(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Cargar datos de mantenimiento
            cursor.execute("""
                SELECT man_id, man_vehiculo_id, man_usu_id, man_fecha_programada, 
                       man_descripcion, man_costo, man_estado 
                FROM mantenimiento 
                ORDER BY man_fecha_programada DESC
            """)
            mantenimiento_data = cursor.fetchall()
            self.mantenimiento_model.refreshData(mantenimiento_data)
            
            # Cargar datos de incidencias
            cursor.execute("""
                SELECT inc_id, inc_usu_id, inc_fecha, inc_descripcion, inc_estado 
                FROM incidencia 
                ORDER BY inc_fecha DESC
            """)
            incidencias_data = cursor.fetchall()
            self.incidencias_model.refreshData(incidencias_data)
            
            # Datos para gráfico
            cursor.execute("""
                SELECT man_estado, COUNT(*) 
                FROM mantenimiento 
                GROUP BY man_estado
            """)
            estado_data = cursor.fetchall()
            
            if estado_data:
                estados = [estado for estado, _ in estado_data]
                cantidades = [cant for _, cant in estado_data]
                
                self.mantenimiento_chart.plot_bar_chart(
                    estados, 
                    cantidades, 
                    'Estado de Mantenimientos',
                    'Estado',
                    'Cantidad',
                    '#673ab7'  # Color púrpura para Mantenimiento
                )
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos de mantenimiento: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()
                
    def logout(self):
        self.close()
        self.loginWindow.show()