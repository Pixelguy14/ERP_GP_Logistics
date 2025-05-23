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

class UsuariosTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        # Cabeceras de cada tabla.
        self._headers = ["ID", "Nombre", "Correo", "Puesto", "Fecha Contratacion", "Salario", "Módulo", "Acciones"]
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            # para no mostrar valores en la columna de las acciones (7 en este caso)
            if index.column() == 7:
                return None
                
            value = self._data[index.row()][index.column()]
            
            # Darle el formato correcto a las fechas
            if index.column() == 4 and isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
                
            # Formato correcto al salario
            if index.column() == 5:
                return f"${value:,.2f}"
                
            return str(value)
            
        elif role == Qt.TextAlignmentRole:
            # Alinear los valores de la columna de monto a la derecha
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

class EvaluacionTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        # Cabeceras de cada tabla.
        self._headers = ["ID", "ID del Usuario", "Fecha", "Puntaje", "Comentarios", "Acciones"]
        
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
                
            
        elif role == Qt.TextAlignmentRole:
            # Alinear los valores del puntaje a la derecha
            if index.column() == 3:
                return Qt.AlignRight | Qt.AlignVCenter
            
        return None
        
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

class RecursosHumanosTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        # Cabeceras de cada tabla.
        self._headers = ["ID", "Usuario ID", "Estado", "Tipo Contrato", "Beneficios", "Observaciones", "Acciones"]
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            # para no mostrar valores en la columna de las acciones (6 en este caso)
            if index.column() == 6:
                return None
                
            value = self._data[index.row()][index.column()]
            
            # Limitar la longitud de los textos largos para mejor visualización
            if index.column() in [4, 5] and isinstance(value, str):
                return value[:50] + "..." if len(value) > 50 else value
                
            return str(value)
            
        elif role == Qt.TextAlignmentRole:
            # Alinear los valores al centro
            return Qt.AlignCenter
            
        elif role == Qt.BackgroundRole:
            # Colorear según el estado
            estado = self._data[index.row()][2]
            if estado == 'Activo':
                return QColor(240, 255, 240)  # Verde claro
            elif estado == 'Inactivo':
                return QColor(255, 255, 240)  # Amarillo claro
            else:  # Baja
                return QColor(255, 240, 240)  # Rojo claro
                
        return None
        
    def rowCount(self, parent=None):
        return len(self._data)
        
    def columnCount(self, parent=None):
        return 7  # 6 columnas de datos + 1 columna de acciones
        
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

# Dialog de editar/insertar datos a la  base de datos para usuario
class UsuariosDialog(QDialog):
    def __init__(self, parent=None, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Usuario" if not self.usuario_data else "Editar Registro")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f8f8;
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
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QFormLayout()

        self.name_label = QLabel("Nombre Completo:")
        self.name_input = QLineEdit()
        layout.addRow(self.name_label, self.name_input)

        self.mail_label = QLabel("Correo:")
        self.mail_input = QLineEdit()
        layout.addRow(self.mail_label, self.mail_input)

        self.pass_label = QLabel("Contraseña:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addRow(self.pass_label, self.pass_input)

        self.poss_label = QLabel("Puesto:")
        self.poss_input = QLineEdit()
        layout.addRow(self.poss_label, self.poss_input)
        
        # Campo de la fecha
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.usuario_data:
            self.date_edit.setDate(QDate.fromString(self.usuario_data[4].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha de contratación:", self.date_edit)
        """
        # Campo para la descripcion
        self.desc_edit = QLineEdit()
        layout.addRow("Descripción:", self.desc_edit)
        """
        # Campo para el salario
        self.salary_edit = QLineEdit()
        self.salary_edit.setPlaceholderText("0.00")
        layout.addRow("Salario de entrada:", self.salary_edit)
        
        # Campo para el tipo de modulo
        self.mod_combo = QComboBox()
        self.mod_combo.addItems(['Finanzas', 'Recursos Humanos', 'Logistica', 'Compras', 'Ventas', 'Mantenimiento', 'Gestion'])
        layout.addRow("Módulo:", self.mod_combo)
        
        # botones de accion
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Llenamos el formulario con datos si se esta editando
        if self.usuario_data:
            #print(f"1:{self.usuario_data[0]} 2:{self.usuario_data[1]} 3:{self.usuario_data[2]} 4:{self.usuario_data[3]} 5:{self.usuario_data[4]} 6:{self.usuario_data[5]} 7:{self.usuario_data[6]}")
            self.name_input.setText(self.usuario_data[1] or "")
            self.mail_input.setText(self.usuario_data[2] or "")
            self.pass_input.setText("")
            self.poss_input.setText(self.usuario_data[3] or "")
            self.date_edit.setDate(QDate.fromString(self.usuario_data[4].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.salary_edit.setText(str(self.usuario_data[5]))
            self.mod_combo.setCurrentText(self.usuario_data[6])
            
    def getUserData(self):
        return {
            "nombre": self.name_input.text(),
            "correo": self.mail_input.text(),
            "contra": self.pass_input.text(),
            "puesto": self.poss_input.text(),
            "fecha_contratacion": self.date_edit.date().toString("yyyy-MM-dd"),
            "salario": float(self.salary_edit.text() or 0),
            "mod": self.mod_combo.currentText()
        }

class EvaluacionDialog(QDialog):
    def __init__(self, parent=None, evaluacion_data=None):
        super().__init__(parent)
        self.evaluacion_data = evaluacion_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Evaluacion de Desempeño" if not self.evaluacion_data else "Editar Evaluacion de Desempeño")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f8f8;
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
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QFormLayout()

        self.id_label = QLabel("ID del Usuario:")
        self.eval_id_input = QLineEdit()
        layout.addRow(self.id_label, self.eval_id_input)

        self.date_label = QLabel("Fecha de Evaluación:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.evaluacion_data:
            self.date_edit.setDate(QDate.fromString(self.evaluacion_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addRow(self.date_label, self.date_edit)

        self.score_label = QLabel("Puntaje (1-10):")
        self.score_spinbox = QSpinBox()
        self.score_spinbox.setRange(1, 10) # Set range for the score
        self.score_spinbox.setValue(5) # Default value
        layout.addRow(self.score_label, self.score_spinbox)

        self.comments_label = QLabel("Comentarios:")
        self.comments_text_edit = QLineEdit()
        self.comments_text_edit.setFixedHeight(80) # Make it a bit taller for comments
        layout.addRow(self.comments_label, self.comments_text_edit)
        
        # Botones de accion
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Llenamos el formulario con datos si se esta editando
        if self.evaluacion_data:
            self.eval_id_input.setText(str(self.evaluacion_data[1]))
            self.date_edit.setDate(QDate.fromString(self.evaluacion_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.score_spinbox.setValue(self.evaluacion_data[3] or "")
            self.comments_text_edit.setText(self.evaluacion_data[4] or "")
            
    def getEvalData(self):
        return {
                "eva_usu_id": self.eval_id_input.text(),
                "eva_fecha": self.date_edit.date().toString("yyyy-MM-dd"),
                "eva_puntaje": self.score_spinbox.value(),
                "eva_comentarios": self.comments_text_edit.text()
            }

class RecursosHumanosDialog(QDialog):
    def __init__(self, parent=None, rrhh_data=None):
        super().__init__(parent)
        self.rrhh_data = rrhh_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de RH" if not self.rrhh_data else "Editar Registro")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f8f8;
                font-family: Arial;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QLineEdit, QDateEdit, QComboBox, QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
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
            QPushButton[text="Cancelar"] {
                background-color: #6c757d;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QFormLayout()

        # Campo para el id del usuario
        self.rh_usuID_edit = QLineEdit()
        self.rh_usuID_edit.setPlaceholderText("ID del usuario...")
        layout.addRow("ID del Usuario:", self.rh_usuID_edit)

        # Campo para el estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(['Activo', 'Inactivo', 'Baja'])
        layout.addRow("Estado:", self.estado_combo)

        # Campo para el tipo de contrato
        self.contrato_combo = QComboBox()
        self.contrato_combo.addItems(['Tiempo completo', 'Medio tiempo', 'Temporal'])
        layout.addRow("Tipo de contrato:", self.contrato_combo)

        # Campo para beneficios
        self.beneficios_edit = QLineEdit()
        self.beneficios_edit.setPlaceholderText("Describa los beneficios del empleado...")
        layout.addRow("Beneficios:", self.beneficios_edit)

        # Campo para observaciones
        self.observaciones_edit = QLineEdit()
        self.observaciones_edit.setPlaceholderText("Observaciones adicionales...")
        layout.addRow("Observaciones:", self.observaciones_edit)
        
        # botones de accion
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Llenamos el formulario con datos si se esta editando
        if self.rrhh_data:
            self.rh_usuID_edit.setText(str(self.rrhh_data[1]))
            self.estado_combo.setCurrentText(self.rrhh_data[2])
            self.contrato_combo.setCurrentText(self.rrhh_data[3])
            self.beneficios_edit.setText(self.rrhh_data[4] or "")
            self.observaciones_edit.setText(self.rrhh_data[5] or "")
            
    def getRHData(self):
        return {
            "reh_id": self.rh_usuID_edit.text(),
            "estado": self.estado_combo.currentText(),
            "tipo_contrato": self.contrato_combo.currentText(),
            "beneficios": self.beneficios_edit.text(),
            "observaciones": self.observaciones_edit.text()
        }

class RRHHWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.db_connection = None
        self.user_data = []
        self.rrhh_data = []
        self.evaluacion_data = []
        self.latestUsuRow=0
        self.initUI(usu_id)
        self.loadDataMain(usu_id)
        
    def initUI(self, usu_id):
        self.setWindowTitle("Módulo de RRHH - Grupo Porteo")
        self.showMaximized()  # Lo volvemos pantalla completa
        
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
            QPushButton#deleteBtn {
                background-color: #dc3545;
            }
            QPushButton#deleteBtn:hover {
                background-color: #c82333;
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

        self.btn_usuarios = QPushButton("Gestión de Usuarios")
        self.btn_usuarios.setCursor(Qt.PointingHandCursor)
        self.btn_usuarios.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0), self.loadDataMain(usu_id)))
        self.toolbar.addWidget(self.btn_usuarios)
        
        self.btn_rrhh = QPushButton("Gestion de RRHH")
        self.btn_rrhh.setCursor(Qt.PointingHandCursor)
        self.btn_rrhh.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1), self.loadRHData(usu_id)))
        self.toolbar.addWidget(self.btn_rrhh)
        
        self.toolbar.addSeparator()

        # Spacer para el boton de cerrar sesion
        spacer = QWidget()

        #spacer.setSizePolicy(QApplication.instance().style().sizeHint(QApplication.instance().style().CT_ToolButton).expandedTo(QSize(0, 0)))
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setStyleSheet("background-color: transparent;")
        self.toolbar.addWidget(spacer)
        
        # Añadimos el boton de cerrar sesion
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        self.toolbar.addWidget(self.logout_btn)
        
        self.stacked_widget = QStackedWidget()
        # --- Primera vista: Panel de Tabla Usuario ---

        usuarios_view_widget = QWidget()
        usuarios_layout = QVBoxLayout(usuarios_view_widget)

        # Splitter para la tabla y graficos
        splitter = QSplitter(Qt.Vertical)
        
        # Tabla con los datos de los usuarios
        self.table_view_usu = QTableView()
        self.table_view_usu.setAlternatingRowColors(True)
        self.table_view_usu.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_usu.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_usu.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_usu.verticalHeader().setVisible(False)
        self.table_view_usu.verticalHeader().setDefaultSectionSize(50) # Se aumenta la altura de la tabla para mostrar correctamente los botones
        self.table_view_usu.setSortingEnabled(True)
        
        # Modelo de insercion para la tabla de usuarios
        self.table_model = UsuariosTableModel()
        self.table_view_usu.setModel(self.table_model)

        # Configurar el ancho de las columnas
        header = self.table_view_usu.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # Fijamos el ancho de la columna 7
        header.resizeSection(7, 300)
        
        splitter.addWidget(self.table_view_usu)

        self.table_view_evaluacions = QTableView()
        self.table_view_evaluacions.setAlternatingRowColors(True)
        self.table_view_evaluacions.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_evaluacions.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view_evaluacions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view_evaluacions.verticalHeader().setVisible(False)
        self.table_view_evaluacions.verticalHeader().setDefaultSectionSize(50)
        self.table_view_evaluacions.setSortingEnabled(True)

        self.evaluacions_table_model = EvaluacionTableModel()
        self.table_view_evaluacions.setModel(self.evaluacions_table_model)

        # Configurar el ancho de las columnas
        header2 = self.table_view_evaluacions.horizontalHeader()
        header2.setSectionResizeMode(QHeaderView.Stretch)
        header2.setSectionResizeMode(4, QHeaderView.Fixed)  # Fijamos el ancho de la columna 4
        header2.resizeSection(4, 300)

        splitter.addWidget(self.table_view_evaluacions)
        self.table_view_evaluacions.hide()
        
        # Le configuramos el tamaño inicial a los componetes dentro del splitter
        splitter.setSizes([450, 550])
        splitter.setStretchFactor(0, 0) # Desactiva el estiramiento para el primer widget (table_view_usu)
        splitter.setStretchFactor(1, 0) # Desactiva el estiramiento para el segundo widget (charts_frame)

        usuarios_layout.addWidget(splitter)
        
        button_panel = QHBoxLayout()
        new_action = QPushButton(QIcon.fromTheme("document-new"), "Nuevo Usuario", self)
        #new_action.clicked.connect(self.addUserRecord)
        new_action.clicked.connect(lambda: self.addUserRecord(usu_id))
        button_panel.addWidget(new_action)
        
        refresh_action = QPushButton(QIcon.fromTheme("view-refresh"), "Actualizar Usuario", self)
        refresh_action.clicked.connect(lambda: self.loadDataMain(usu_id))
        button_panel.addWidget(refresh_action)

        self.new_eval = QPushButton(QIcon.fromTheme("document-new"), "Nueva Evaluacion", self)
        self.new_eval.clicked.connect(lambda: self.addEvalRecord(usu_id))
        button_panel.addWidget(self.new_eval)
        #self.new_eval.hide()
        """
        self.refresh_eval = QPushButton(QIcon.fromTheme("view-refresh"), "Actualizar Evaluacion", self)
        #self.refresh_eval.clicked.connect(lambda: self.loadDataEvaluation(usu_id))
        button_panel.addWidget(self.refresh_eval)
        self.refresh_eval.hide()
        """
        button_panel.addStretch()
        
        usuarios_layout.addLayout(button_panel)

        self.stacked_widget.addWidget(usuarios_view_widget)
        # En el método initUI, después de configurar la vista de usuarios:
        rh_view_widget = QWidget()
        rh_layout = QVBoxLayout(rh_view_widget)

        # Tabla de recursos humanos
        self.rh_table_view = QTableView()
        self.rh_table_view.setAlternatingRowColors(True)
        self.rh_table_view.setSelectionBehavior(QTableView.SelectRows)
        self.rh_table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.rh_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rh_table_view.verticalHeader().setDefaultSectionSize(50)
        self.rh_table_view.verticalHeader().setVisible(False)
        self.rh_table_view.setSortingEnabled(True)

        # Modelo para la tabla de RH
        self.rh_table_model = RecursosHumanosTableModel()
        self.rh_table_view.setModel(self.rh_table_model)

        # Configurar el ancho de las columnas
        header = self.rh_table_view.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Beneficios
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Observaciones
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Acciones
        #header.setSectionResizeMode(QHeaderView.Stretch)
        #header.setSectionResizeMode(6, QHeaderView.Fixed)
        #header.resizeSection(6, 600)

        rh_layout.addWidget(self.rh_table_view)

        # Panel de botones
        button_panel = QHBoxLayout()
        add_btn = QPushButton("Agregar Registro RH")
        add_btn.clicked.connect(lambda: self.addRHRecord(usu_id))
        button_panel.addWidget(add_btn)

        refresh_btn = QPushButton("Actualizar")
        refresh_btn.clicked.connect(lambda: self.loadRHData(usu_id))
        button_panel.addWidget(refresh_btn)

        button_panel.addStretch()
        rh_layout.addLayout(button_panel)

        self.stacked_widget.addWidget(rh_view_widget)
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
            cursor.execute("SELECT usu_id, usu_nombre, usu_correo, usu_puesto, usu_fecha_contratacion, usu_salario, usu_mod FROM usuario ORDER BY usu_nombre DESC")
            self.user_data = cursor.fetchall()
            
            # Actualizamos los datos de la tabla
            self.table_model.refreshData(self.user_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.user_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editUserRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de eliminar
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteUserRecord(r, usu_id))
                layout.addWidget(delete_btn)
                
                # Evaluacion button
                evaluation_btn = QPushButton("Evals")
                evaluation_btn.setObjectName("evaluacionBtn")
                evaluation_btn.setFixedWidth(90)
                evaluation_btn.setFixedHeight(30)
                #evaluation_btn.clicked.connect(self.toggleEvaluacionsTable)
                evaluation_btn.clicked.connect(lambda _, r=row: self.toggleEvaluacionsTable(r, usu_id))
                layout.addWidget(evaluation_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla, en la columna 7 (excluyendo contraseña)
                self.table_view_usu.setIndexWidget(self.table_model.index(row, 7), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadDataEvaluation(self, row_usu, usu_id):
        record = self.user_data[row_usu] # usamos user_data por que queremos recuperar
        # el id de la tabla usuario
        #print(f"record: {record}, row: {row}")
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            query = """SELECT * FROM evaluacion_desempeno WHERE eva_usu_id=%s ORDER BY eva_fecha DESC"""
            cursor.execute(query, (record[0], ))
            self.evaluacion_data = cursor.fetchall()
            # Actualizamos los datos de la tabla
            self.evaluacions_table_model.refreshData(self.evaluacion_data)
            # Configurar las funciones en la ultima columna
            for row in range(len(self.evaluacion_data)):
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
                self.table_view_evaluacions.setIndexWidget(self.evaluacions_table_model.index(row, 5), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadRHData(self, usu_id):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Get all RH records
            cursor.execute("""
                SELECT reh_id, reh_usu_id, reh_estado, reh_tipo_contrato, 
                    reh_beneficios, reh_observaciones 
                FROM recursoshumanos 
                ORDER BY reh_estado, reh_usu_id
            """)
            self.rrhh_data = cursor.fetchall()
            
            # Actualizamos los datos de la tabla
            self.rh_table_model.refreshData(self.rrhh_data)
            
            # Configurar las funciones en la ultima columna
            for row in range(len(self.rrhh_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Boton de editar
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editRHRecord(r, usu_id))
                layout.addWidget(edit_btn)
                
                # Boton de cambiar estado
                status_btn = QPushButton("Cambiar Estado")
                status_btn.setFixedWidth(130)
                status_btn.setFixedHeight(30)
                status_btn.clicked.connect(lambda _, r=row: self.toggleRHStatus(r, usu_id))
                layout.addWidget(status_btn)

                # Boton de Eliminar
                status_btn = QPushButton("Eliminar")
                status_btn.setFixedWidth(90)
                status_btn.setFixedHeight(30)
                status_btn.clicked.connect(lambda _, r=row: self.deleteRRHHRecord(r, usu_id))
                layout.addWidget(status_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Configurar el widget en la tabla
                self.rh_table_view.setIndexWidget(self.rh_table_model.index(row, 6), widget)
                
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def addUserRecord(self, usu_id):
        dialog = UsuariosDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.getUserData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                user_id = usu_id
                #print("user id :",user_id)
                query = """
                INSERT INTO usuario (usu_nombre, usu_correo, usu_contra, usu_puesto, usu_fecha_contratacion, usu_salario, usu_mod)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user_data["nombre"],
                    user_data["correo"],
                    user_data["contra"],
                    user_data["puesto"],
                    user_data["fecha_contratacion"],
                    user_data["salario"],
                    user_data["mod"]
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

    def addEvalRecord(self, usu_id):
        dialog = EvaluacionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            evaluacion_data = dialog.getEvalData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                user_id = usu_id
                query = """
                INSERT INTO evaluacion_desempeno (eva_usu_id, eva_fecha, eva_puntaje, eva_comentarios)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    evaluacion_data["eva_usu_id"],
                    evaluacion_data["eva_fecha"],
                    evaluacion_data["eva_puntaje"],
                    evaluacion_data["eva_comentarios"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro agregado correctamente")
                if self.table_view_evaluacions.isVisible():
                    self.loadDataEvaluation(self.latestUsuRow,usu_id)
                else:
                    self.table_view_evaluacions.show()
                    self.loadDataEvaluation(self.latestUsuRow,usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close() 

    def addRHRecord(self, usu_id):
        dialog = RecursosHumanosDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            rrhh_data = dialog.getRHData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                INSERT INTO recursoshumanos 
                (reh_usu_id, reh_estado, reh_tipo_contrato, reh_beneficios, reh_observaciones)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    rrhh_data["reh_id"],
                    rrhh_data["estado"],
                    rrhh_data["tipo_contrato"],
                    rrhh_data["beneficios"],
                    rrhh_data["observaciones"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro de RH agregado correctamente")
                self.loadRHData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def editUserRecord(self, row, usu_id):
        record = self.user_data[row]
        
        dialog = UsuariosDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            user_data = dialog.getUserData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE usuario 
                SET usu_nombre = %s, usu_correo = %s, usu_contra = %s, usu_puesto = %s, usu_fecha_contratacion = %s, 
                usu_salario = %s, usu_mod = %s
                WHERE usu_id = %s
                """
                cursor.execute(query, (
                    user_data["nombre"],
                    user_data["correo"],
                    user_data["contra"],
                    user_data["puesto"],
                    user_data["fecha_contratacion"],
                    user_data["salario"],
                    user_data["mod"],
                    record[0] # id del usuario a editar
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
        record = self.evaluacion_data[row]
        
        dialog = EvaluacionDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            evaluacion_data = dialog.getEvalData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE evaluacion_desempeno 
                SET eva_usu_id = %s, eva_fecha = %s, eva_puntaje = %s, eva_comentarios = %s
                WHERE eva_id = %s
                """
                cursor.execute(query, (
                    evaluacion_data["eva_usu_id"],
                    evaluacion_data["eva_fecha"],
                    evaluacion_data["eva_puntaje"],
                    evaluacion_data["eva_comentarios"],
                    record[0] # id de la evaluacion a editar (eva_id)
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro actualizado correctamente")
                self.loadDataEvaluation(self.latestUsuRow, usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()
                    
    def editRHRecord(self, row, usu_id):
        record = self.rrhh_data[row]
        
        dialog = RecursosHumanosDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            rrhh_data = dialog.getRHData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE recursoshumanos 
                SET reh_usu_id = %s, reh_estado = %s, reh_tipo_contrato = %s, 
                    reh_beneficios = %s, reh_observaciones = %s
                WHERE reh_id = %s
                """
                cursor.execute(query, (
                    rrhh_data["reh_id"],
                    rrhh_data["estado"],
                    rrhh_data["tipo_contrato"],
                    rrhh_data["beneficios"],
                    rrhh_data["observaciones"],
                    record[0]  # reh_id
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro de RH actualizado correctamente")
                self.loadRHData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteUserRecord(self, row, usu_id):
        record = self.user_data[row]
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
                
                query = "DELETE FROM usuario WHERE usu_id = %s"
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
        record = self.evaluacion_data[row]
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
                
                query = "DELETE FROM evaluacion_desempeno WHERE eva_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                self.loadDataEvaluation(self.latestUsuRow, usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def deleteRRHHRecord(self, row, usu_id):
        record = self.rrhh_data[row]
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
                
                query = "DELETE FROM recursoshumanos WHERE reh_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                self.loadRHData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()
 
    def toggleEvaluacionsTable(self, row, usu_id):
        if self.table_view_evaluacions.isVisible() and row == self.latestUsuRow:
            self.table_view_evaluacions.hide()
            #self.new_eval.hide()
        else:
            self.table_view_evaluacions.show()
            #self.new_eval.show()
            self.loadDataEvaluation(row, usu_id)
            self.latestUsuRow=row

    def toggleRHStatus(self, row, usu_id):
        record = self.rrhh_data[row]
        current_status = record[2]
        
        #new_status = 'Baja' if current_status == 'Activo' else 'Activo'
        if current_status == 'Activo':
            new_status = 'Inactivo'
        elif current_status == 'Inactivo':
            new_status = 'Baja'
        else: 
            new_status = 'Activo'
        
        reply = QMessageBox.question(
            self, 
            "Confirmar cambio de estado",
            f"¿Cambiar estado de {current_status} a {new_status} para el registro ID {record[0]}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = "UPDATE recursoshumanos SET reh_estado = %s WHERE reh_id = %s"
                cursor.execute(query, (new_status, record[0]))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Estado actualizado correctamente")
                self.loadRHData(usu_id)
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar estado: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()

    def logout(self):
        self.close()
        self.loginWindow.show()
