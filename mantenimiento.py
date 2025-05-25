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

class MantenimientoTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        # Cabeceras de cada tabla.
        self._headers = ["ID", "ID del Vehiculo", "ID del Usuario", "Fecha Programada", "Descripcion", "Costo", "Estado", "Acciones"]
        #                 0          1              2                3                 4          5         6          7
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            # para no mostrar valores en la columna de las acciones (7 en este caso)
            if index.column() == 7:
                return None
                
            value = self._data[index.row()][index.column()]
            
            # Darle el formato correcto a las fechas
            if index.column() == 3 and isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
                
            # Formato correcto al costo
            if index.column() == 5:
                return f"${value:,.2f}"
                
            return str(value)
            
        elif role == Qt.TextAlignmentRole:
            # Alinear los valores de la columna de costo a la derecha
            if index.column() == 5:
                return Qt.AlignRight | Qt.AlignVCenter
        return None
        
    def rowCount(self, parent=None):
        return len(self._data)
        
    def columnCount(self, parent=None):
        return 8  # 7 columnas de datos + 1 columna de acciones (Quitando contraseña)
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
        
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False
        
    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class IncidenciaTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        # Cabeceras de cada tabla.
        self._headers = ["ID", "ID del Usuario", "Fecha", "Descripcion", "Estado", "Acciones"]
        #                 0           1             2           3            4         5
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            # para no mostrar valores en la columna de las acciones (7 en este caso)
            if index.column() == 5:
                return None
                
            value = self._data[index.row()][index.column()]
            
            # Darle el formato correcto a las fechas
            if index.column() == 2 and isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")

            return str(value)
        
    def rowCount(self, parent=None):
        return len(self._data)
        
    def columnCount(self, parent=None):
        return 6  # 5 columnas de datos + 1 columna de acciones
        
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None
        
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False
        
    def refreshData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

# Dialog de editar/insertar datos a la  base de datos para el mantenimiento
class MantenimientoDialog(QDialog):
    def __init__(self, parent=None, mantenimiento_data=None):
        super().__init__(parent)
        self.mantenimiento_data = mantenimiento_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Mantenimiento" if not self.mantenimiento_data else "Editar Registro")
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

        self.vehiculo_spin = QSpinBox()
        self.vehiculo_spin.setRange(1, 9999)
        layout.addRow("ID del Vehiculo:", self.vehiculo_spin)
        
        # Campo de la fecha
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.mantenimiento_data:
            self.date_edit.setDate(QDate.fromString(self.mantenimiento_data[3].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha Programada:", self.date_edit)
        
        # Campo para la descripcion
        self.desc_edit = QLineEdit()
        self.desc_edit.setFixedHeight(80)
        layout.addRow("Descripción:", self.desc_edit)
        
        # Campo para el costo
        self.costo_edit = QLineEdit()
        self.costo_edit.setPlaceholderText("0.00")
        layout.addRow("Costo del Mantenimiento:", self.costo_edit)
        
        # Campo para estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Pendiente', 'Completado'])
        layout.addRow("Estado:", self.estado_combo)
        
        # botones de accion
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Llenamos el formulario con datos si se esta editando
        if self.mantenimiento_data:
            self.vehiculo_spin.setValue(int(self.mantenimiento_data[1]))
            self.date_edit.setDate(QDate.fromString(self.mantenimiento_data[3].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.desc_edit.setText(str(self.mantenimiento_data[4]))
            self.costo_edit.setText(str(self.mantenimiento_data[5]))
            self.estado_combo.setCurrentText(self.mantenimiento_data[6])
            
    def getMantenimientoData(self):
        return {
            "vehiculo_id": self.vehiculo_spin.value(),
            "fecha": self.date_edit.date().toString("yyyy-MM-dd"),
            "descripcion": self.desc_edit.text(),
            "costo": float(self.costo_edit.text() or 0),
            "estado": self.estado_combo.currentText()
        }

class IncidenciaDialog(QDialog):
    def __init__(self, parent=None, incidencia_data=None):
        super().__init__(parent)
        self.incidencia_data = incidencia_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Evaluacion de Desempeño" if not self.incidencia_data else "Editar Evaluacion de Desempeño")
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

        self.date_label = QLabel("Fecha de la Incidencia:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.incidencia_data:
            self.date_edit.setDate(QDate.fromString(self.incidencia_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addRow(self.date_label, self.date_edit)

        self.desc_label = QLabel("Descripcion:")
        self.desc_text_edit = QLineEdit()
        self.desc_text_edit.setFixedHeight(80)
        layout.addRow(self.desc_label, self.desc_text_edit)

        # Campo para estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Reportada', 'En revisión', 'Resuelta'])
        layout.addRow("Estado:", self.estado_combo)
        
        # Botones de accion
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Llenamos el formulario con datos si se esta editando
        if self.incidencia_data:
            self.date_edit.setDate(QDate.fromString(self.incidencia_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.desc_text_edit.setText(self.incidencia_data[3] or "")
            self.estado_combo.setCurrentText(self.incidencia_data[4])
            
    def getEvalData(self):
        return {
                "fecha": self.date_edit.date().toString("yyyy-MM-dd"),
                "descripcion": self.desc_text_edit.text(),
                "estado": self.estado_combo.currentText()
            }

class MantenimientoWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.db_connection = None
        self.mantenimiento_data = []
        self.rrhh_data = []
        self.incidencia_data = []
        self.latestUsuRow=0
        self.initUI(usu_id)
        self.loadDataMain(usu_id)
        
    def initUI(self, usu_id):
        self.setWindowTitle("Módulo de Mantenimiento - Grupo Porteo")
        self.showMaximized()  # Lo volvemos pantalla completa
        
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
        
        # Toolbar superior
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # Agregamos el logo a la toolbar
        logo_label = QLabel()
        logo_pixmap = QPixmap("Logo-Grupo-Porteo.png")
        if logo_pixmap.isNull():
            print("Error: No se pudo cargar Logo-Grupo-Porteo.png")
        else:
            logo_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        self.toolbar.addWidget(logo_label)
        
        # Titulo de la toolbar
        title_label = QLabel("Sistema de Gestión de RRHH")
        title_label.setObjectName("titleLabel")
        self.toolbar.addWidget(title_label)

        self.toolbar.addSeparator()

        self.btn_usuarios = QPushButton("Gestión de Mantenimiento")
        self.btn_usuarios.setCursor(Qt.PointingHandCursor)
        self.btn_usuarios.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0), self.loadDataMain(usu_id)))
        self.toolbar.addWidget(self.btn_usuarios)
        
        self.btn_incidencia = QPushButton("Gestion de Incidencias")
        self.btn_incidencia.setCursor(Qt.PointingHandCursor)
        self.btn_incidencia.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1), self.loadDataIncidencia(usu_id['usu_id'])))
        self.toolbar.addWidget(self.btn_incidencia)
        
        self.toolbar.addSeparator()

        # Spacer para el boton de cerrar sesion
        spacer = QWidget()

        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setStyleSheet("background-color: transparent;")
        self.toolbar.addWidget(spacer)
        
        # Añadimos el boton de cerrar sesion
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        self.toolbar.addWidget(self.logout_btn)
        
        self.stacked_widget = QStackedWidget()
        # --- Primera vista: Panel de Tabla Mantemimiento ---

        mantenimiento_view_widget = QWidget()
        mantenimiento_layout = QVBoxLayout(mantenimiento_view_widget)

        # Splitter para la tabla y graficos
        splitter = QSplitter(Qt.Vertical)
        
        # Tabla con los datos del mantenimiento
        self.table_view_mantenimiento = QTableView()
        self.table_view_mantenimiento.setAlternatingRowColors(True)
        self.table_view_mantenimiento.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_mantenimiento.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_mantenimiento.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_mantenimiento.verticalHeader().setVisible(False)
        self.table_view_mantenimiento.verticalHeader().setDefaultSectionSize(50) # Se aumenta la altura de la tabla para mostrar correctamente los botones
        self.table_view_mantenimiento.setSortingEnabled(True)
        
        # Modelo de insercion para la tabla de mantenimiento
        self.table_model = MantenimientoTableModel()
        self.table_view_mantenimiento.setModel(self.table_model)

        # Configurar el ancho de las columnas
        header = self.table_view_mantenimiento.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Fijamos el ancho de la columna 7
        header.resizeSection(7, 300)
        
        splitter.addWidget(self.table_view_mantenimiento)

        # añadir tablas (una izq y otra derecha) de:
        """
        Programación de mantenimientos por realizar:
        SELECT * FROM mantenimiento WHERE man_estado = 'Pendiente';

        ### Registro de incidencias reportadas:
        SELECT * FROM incidencia WHERE inc_estado = 'Reportada';
        """

        #splitter.addWidget(self.table_view_incidencia)
        #self.table_view_incidencia.hide()
        
        # Le configuramos el tamaño inicial a los componetes dentro del splitter
        splitter.setSizes([450, 550])
        splitter.setStretchFactor(0, 0) # Desactiva el estiramiento para el primer widget (table_view_mantenimiento)
        splitter.setStretchFactor(1, 0) # Desactiva el estiramiento para el segundo widget (charts_frame)

        mantenimiento_layout.addWidget(splitter)
        
        button_panel = QHBoxLayout()
        new_action = QPushButton(QIcon.fromTheme("document-new"), "Nuevo Mantenimiento", self)
        new_action.clicked.connect(lambda: self.addMantenimientoRecord(usu_id))
        button_panel.addWidget(new_action)
        
        refresh_action = QPushButton(QIcon.fromTheme("view-refresh"), "Actualizar", self)
        refresh_action.clicked.connect(lambda: self.loadDataMain(usu_id))
        button_panel.addWidget(refresh_action)
        button_panel.addStretch()
        
        mantenimiento_layout.addLayout(button_panel)

        self.stacked_widget.addWidget(mantenimiento_view_widget)

        incidencia_view_widget = QWidget()
        incidencia_layout = QVBoxLayout(incidencia_view_widget)

        self.table_view_incidencia = QTableView()
        self.table_view_incidencia.setAlternatingRowColors(True)
        self.table_view_incidencia.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_incidencia.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_incidencia.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_incidencia.verticalHeader().setVisible(False)
        self.table_view_incidencia.verticalHeader().setDefaultSectionSize(50)
        self.table_view_incidencia.setSortingEnabled(True)

        self.evaluacions_table_model = IncidenciaTableModel()
        self.table_view_incidencia.setModel(self.evaluacions_table_model)

        # Configurar el ancho de las columnas
        header = self.table_view_incidencia.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Fijamos el ancho de la columna 4
        header.resizeSection(4, 300)

        incidencia_layout.addWidget(self.table_view_incidencia)

        button_panel = QHBoxLayout()

        self.new_incidencia = QPushButton(QIcon.fromTheme("document-new"), "Nueva Incidencia", self)
        self.new_incidencia.clicked.connect(lambda: self.addIncidenciaRecord(usu_id))
        button_panel.addWidget(self.new_incidencia)

        refresh_action = QPushButton(QIcon.fromTheme("view-refresh"), "Actualizar", self)
        refresh_action.clicked.connect(lambda: self.loadDataIncidencia(usu_id['usu_id']))
        button_panel.addWidget(refresh_action)
        button_panel.addStretch()

        incidencia_layout.addLayout(button_panel)

        self.stacked_widget.addWidget(incidencia_view_widget)

        # Añadimos el QStackedWidget al layout principal de la ventana
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
            cursor.execute("SELECT * FROM mantenimiento ORDER BY man_costo DESC")
            self.mantenimiento_data = cursor.fetchall()
            
            # Actualizamos los datos de la tabla
            self.table_model.refreshData(self.mantenimiento_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.mantenimiento_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editMantenimientoRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de eliminar
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteMantenimientoRecord(r, usu_id))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla, en la columna 7 (excluyendo contraseña)
                self.table_view_mantenimiento.setIndexWidget(self.table_model.index(row, 7), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadDataIncidencia(self, usu_id):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            query = """SELECT * FROM incidencia WHERE inc_usu_id=%s ORDER BY inc_fecha DESC"""
            
            cursor.execute(query, (usu_id, ))
            self.incidencia_data = cursor.fetchall()
            # Actualizamos los datos de la tabla
            self.evaluacions_table_model.refreshData(self.incidencia_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.incidencia_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editEvalRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de eliminar
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteEvalRecord(r, usu_id))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla, en la columna 5
                self.table_view_incidencia.setIndexWidget(self.evaluacions_table_model.index(row, 5), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def addMantenimientoRecord(self, usu_id):
        dialog = MantenimientoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            mantenimiento_data = dialog.getMantenimientoData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                INSERT INTO mantenimiento (man_vehiculo_id, man_usu_id, man_fecha_programada, man_descripcion, man_costo, man_estado)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    mantenimiento_data["vehiculo_id"],
                    usu_id,
                    mantenimiento_data["fecha"],
                    mantenimiento_data["descripcion"],
                    mantenimiento_data["costo"],
                    mantenimiento_data["estado"]
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

    def addIncidenciaRecord(self, usu_id):
        dialog = IncidenciaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            incidencia_data = dialog.getEvalData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                INSERT INTO incidencia (inc_usu_id, inc_fecha, inc_descripcion, inc_estado)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    usu_id,
                    incidencia_data["fecha"],
                    incidencia_data["descripcion"],
                    incidencia_data["estado"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro agregado correctamente")

                self.loadDataIncidencia(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close() 

    def editMantenimientoRecord(self, row, usu_id):
        record = self.mantenimiento_data[row]
        
        dialog = MantenimientoDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            mantenimiento_data = dialog.getMantenimientoData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE mantenimiento 
                SET man_vehiculo_id = %s, man_usu_id = %s, man_fecha_programada = %s, man_descripcion = %s, man_costo = %s, 
                man_estado = %s
                WHERE man_id = %s
                """
                cursor.execute(query, (
                    mantenimiento_data["vehiculo_id"],
                    usu_id,
                    mantenimiento_data["fecha"],
                    mantenimiento_data["descripcion"],
                    mantenimiento_data["costo"],
                    mantenimiento_data["estado"],
                    record[0] # id del mantenimiento a editar
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

    def editEvalRecord(self, row, usu_id):
        record = self.incidencia_data[row]
        
        dialog = IncidenciaDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            incidencia_data = dialog.getEvalData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE incidencia 
                SET inc_usu_id = %s, inc_fecha = %s, inc_descripcion = %s, inc_estado = %s
                WHERE inc_id = %s
                """
                cursor.execute(query, (
                    usu_id,
                    incidencia_data["fecha"],
                    incidencia_data["descripcion"],
                    incidencia_data["estado"],
                    record[0] # id de la evaluacion a editar (inc_id)
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro actualizado correctamente")
                self.loadDataIncidencia(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteMantenimientoRecord(self, row, usu_id):
        record = self.mantenimiento_data[row]
        #print(f"record: {record}, row: {row}")
        
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
                
                query = "DELETE FROM mantenimiento WHERE inc_id = %s"
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

    def deleteEvalRecord(self, row, usu_id):
        record = self.incidencia_data[row]
        #print(f"record: {record}, row: {row}")
        
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
                
                query = "DELETE FROM incidencia WHERE inc_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                self.loadDataIncidencia(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def logout(self):
        self.close()
        self.loginWindow.show()
