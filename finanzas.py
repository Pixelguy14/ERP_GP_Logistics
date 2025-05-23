import sys
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTableView, QHeaderView, QToolBar, QAction, QDialog, QFormLayout, 
                            QLineEdit, QDateEdit, QComboBox, QMessageBox, QLabel, QSplitter,
                            QDialogButtonBox, QApplication, QFrame, QGridLayout, QSizePolicy, 
                            QStackedWidget)
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

class FinanzasTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else []
        # Cabeceras de cada tabla.
        self._headers = ["ID", "Usuario ID", "Fecha", "Descripción", "Monto", "Tipo", "Acciones"]
        
    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
            
        if role == Qt.DisplayRole:
            # para no mostrar valores en la columna de las acciones (6 en este caso)
            if index.column() == 6:
                return None
                
            value = self._data[index.row()][index.column()]
            
            # Darle el formato correcto a las fechas
            if index.column() == 2 and isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")
                
            # Formato correcto a los ingresos
            if index.column() == 4:
                return f"${value:,.2f}"
                
            return str(value)
            
        elif role == Qt.TextAlignmentRole:
            # Alinear los valores de la columna de monto a la derecha
            if index.column() == 4:
                return Qt.AlignRight | Qt.AlignVCenter
        """
        elif role == Qt.BackgroundRole:
            # Colorear las filas en base a el tipo de transaccion
            if self._data[index.row()][5] == 'ingreso':
                return QColor(240, 255, 240)  # Light green for income
            else:
                return QColor(255, 240, 240)  # Light red for expenses
        """     
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

# Dialog de editar/insertar datos a la  base de datos para finanzas
class FinanzasDialog(QDialog):
    def __init__(self, parent=None, finance_data=None):
        super().__init__(parent)
        self.finance_data = finance_data
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Registro de Finanzas" if not self.finance_data else "Editar Registro")
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
        
        # Campo de la fecha
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        #self.date_edit.setDate(QDate.currentDate())
        #self.date_edit.setDate(QDate.fromString(self.finance_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        if self.finance_data:
            self.date_edit.setDate(QDate.fromString(self.finance_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        else:
            #print("Advertencia: finance_data es None. Se usará la fecha actual.")
            self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Fecha:", self.date_edit)
        
        # Campo para la descripcion
        self.desc_edit = QLineEdit()
        layout.addRow("Descripción:", self.desc_edit)
        
        # Campo para el monto
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("0.00")
        layout.addRow("Monto:", self.amount_edit)
        
        # Campo para el tipo de ingreso
        self.type_combo = QComboBox()
        self.type_combo.addItems(["ingreso", "gasto"])
        layout.addRow("Tipo:", self.type_combo)
        
        # botones de accion
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        # Llenamos el formulario con datos si se esta editando
        if self.finance_data:
            #self.date_edit.setDate(QDate.fromString(self.finance_data[2], "yyyy-MM-dd"))
            self.date_edit.setDate(QDate.fromString(self.finance_data[2].strftime("%Y-%m-%d"), "yyyy-MM-dd"))
            self.desc_edit.setText(self.finance_data[3] or "")
            self.amount_edit.setText(str(self.finance_data[4]))
            self.type_combo.setCurrentText(self.finance_data[5])
            
    def getFinanceData(self):
        return {
            "fecha": self.date_edit.date().toString("yyyy-MM-dd"),
            "desc": self.desc_edit.text(),
            "monto": float(self.amount_edit.text() or 0),
            "tipo": self.type_combo.currentText()
        }

class FinanceChart(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
    def plot_income_expense(self, income_data, expense_data):
        self.axes.clear()
        
        # Extract dates and amounts
        #income_dates = [datetime.strptime(date, "%Y-%m-%d").date() for date, _ in income_data]
        income_dates = [date for date, _ in income_data]
        income_amounts = [amount for _, amount in income_data]
        
        #expense_dates = [datetime.strptime(date, "%Y-%m-%d").date() for date, _ in expense_data]
        expense_dates = [date for date, _ in expense_data]
        expense_amounts = [amount for _, amount in expense_data]
        
        # Plot data
        self.axes.plot(income_dates, income_amounts, 'go-', label='Ingresos')
        self.axes.plot(expense_dates, expense_amounts, 'ro-', label='Gastos')
        
        # Format plot
        self.axes.set_title('Ingresos vs Gastos')
        self.axes.set_xlabel('Fecha')
        self.axes.set_ylabel('Monto ($)')
        self.axes.legend()
        self.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Format y-axis as currency
        self.axes.yaxis.set_major_formatter('${x:,.2f}')
        
        # Rotate date labels for better readability
        plt.setp(self.axes.get_xticklabels(), rotation=45, ha='right')
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_summary_pie(self, income_total, expense_total):
        self.axes.clear()
        
        # Data
        labels = ['Ingresos', 'Gastos']
        sizes = [income_total, expense_total]
        colors = ['#4CAF50', '#F44336']
        explode = (0.1, 0)  # explode the 1st slice (Ingresos)
        
        # Plot
        self.axes.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        self.axes.set_title('Distribución de Finanzas')
        
        self.fig.tight_layout()
        self.draw()


class FinanzasWindow(QMainWindow):
    def __init__(self, loginWindow, usu_id):
        super().__init__()
        if loginWindow is None:
            print("Error: loginWindow no es válido")
            return
        self.loginWindow = loginWindow
        self.db_connection = None
        self.finance_data = []
        self.initUI(usu_id)
        self.loadDataMain()
        
    def initUI(self,usu_id):
        self.setWindowTitle("Módulo de Finanzas - Grupo Porteo")
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
        title_label = QLabel("Sistema de Gestión Financiera")
        title_label.setObjectName("titleLabel")
        self.toolbar.addWidget(title_label)

        self.toolbar.addSeparator()

        self.btn_finanzas = QPushButton("Gestión de Finanzas")
        self.btn_finanzas.setCursor(Qt.PointingHandCursor)
        #self.btn_finanzas.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0),self.loadDataMain))
        self.btn_finanzas.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0), self.loadDataMain()))
        self.toolbar.addWidget(self.btn_finanzas)

        self.btn_consultas = QPushButton("Reportes Financieros")
        self.btn_consultas.setCursor(Qt.PointingHandCursor)
        self.btn_consultas.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.toolbar.addWidget(self.btn_consultas)
        
        self.toolbar.addSeparator()
        """
        # Acciones sobre la toolbar
        new_action = QAction(QIcon.fromTheme("document-new"), "Nuevo Registro", self)
        new_action.triggered.connect(self.addFinanceRecord)
        self.toolbar.addAction(new_action)
        
        refresh_action = QAction(QIcon.fromTheme("view-refresh"), "Actualizar", self)
        refresh_action.triggered.connect(self.loadDataMain)
        self.toolbar.addAction(refresh_action)
        
        self.toolbar.addSeparator()
        """

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
        """
        # Añadimos el widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        """
        # --- Primera vista: Panel de Tablas SQL ---

        finances_view_widget = QWidget()
        finances_layout = QVBoxLayout(finances_view_widget)

        # Splitter para la tabla y graficos
        splitter = QSplitter(Qt.Vertical)
        
        # Tabla con los datos de las finanzas
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.verticalHeader().setDefaultSectionSize(50) # Se aumenta la altura de la tabla para mostrar correctamente los botones
        self.table_view.setSortingEnabled(True)
        
        # Create model for table
        self.table_model = FinanzasTableModel()
        self.table_view.setModel(self.table_model)
        
        splitter.addWidget(self.table_view)

        # Create charts frame
        charts_frame = QFrame()
        charts_frame.setObjectName("chartFrame")
        charts_layout = QGridLayout(charts_frame)
        
        # Create charts
        self.time_chart = FinanceChart(width=8, height=4)
        charts_layout.addWidget(self.time_chart, 0, 0)
        
        self.summary_chart = FinanceChart(width=4, height=4)
        charts_layout.addWidget(self.summary_chart, 0, 1)
        
        splitter.addWidget(charts_frame)
        
        # Le configuramos el tamaño inicial a los componetes dentro del splitter
        splitter.setSizes([450, 550])
        splitter.setStretchFactor(0, 0) # Desactiva el estiramiento para el primer widget (table_view)
        splitter.setStretchFactor(1, 0) # Desactiva el estiramiento para el segundo widget (charts_frame)
        
        #main_layout.addWidget(splitter)
        finances_layout.addWidget(splitter)
        """
        # Añadir un panel de boton hasta el fondo de la interfaz
        button_panel = QHBoxLayout()
        add_btn = QPushButton("Agregar Registro")
        add_btn.clicked.connect(self.addFinanceRecord)
        button_panel.addWidget(add_btn)
        
        button_panel.addStretch()
        
        main_layout.addLayout(button_panel)
        """
        button_panel = QHBoxLayout()
        new_action = QPushButton(QIcon.fromTheme("document-new"), "Nuevo Registro", self)
        #new_action.clicked.connect(self.addFinanceRecord)
        new_action.clicked.connect(lambda: self.addFinanceRecord(usu_id))
        #new_action = QAction(QIcon.fromTheme("document-new"), "Nuevo Registro", self)
        #new_action.triggered.connect(self.addFinanceRecord)
        #self.toolbar.addAction(new_action)
        button_panel.addWidget(new_action)
        
        refresh_action = QPushButton(QIcon.fromTheme("view-refresh"), "Actualizar", self)
        refresh_action.clicked.connect(self.loadDataMain)
        #refresh_action = QAction(QIcon.fromTheme("view-refresh"), "Actualizar", self)
        #refresh_action.triggered.connect(self.loadDataMain)
        #self.toolbar.addAction(refresh_action)
        button_panel.addWidget(refresh_action)

        button_panel.addStretch()
        
        finances_layout.addLayout(button_panel)

        #self.setCentralWidget(central_widget)
        self.stacked_widget.addWidget(finances_view_widget)

        # --- Segunda vista: Panel de Consultas SQL ---
        queries_view_widget = QWidget()
        queries_layout = QVBoxLayout(queries_view_widget)
        
        # Frame para filtros
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_layout = QFormLayout(filter_frame)

        # Fecha inicial
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addYears(-1))
        filter_layout.addRow("Fecha inicial:", self.start_date_edit)

        # Fecha final
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_layout.addRow("Fecha final:", self.end_date_edit)

        queries_layout.addWidget(filter_frame)

        # Botón de búsqueda y controles de totales
        button_row = QHBoxLayout()

        # Botón de búsqueda
        search_btn = QPushButton("Buscar")
        search_btn.clicked.connect(self.loadQueryData)
        button_row.addWidget(search_btn)

        # Botón de control de ingresos
        income_btn = QPushButton("Control de Ingresos")
        income_btn.clicked.connect(lambda: self.showTotal('ingreso'))
        income_btn.setStyleSheet("background-color: #4CAF50; color: white;")  # Verde
        button_row.addWidget(income_btn)

        # Botón de control de gastos
        expense_btn = QPushButton("Control de Gastos")
        expense_btn.clicked.connect(lambda: self.showTotal('gasto'))
        expense_btn.setStyleSheet("background-color: #F44336; color: white;")  # Rojo
        button_row.addWidget(expense_btn)

        # Añadir la fila de botones al layout del filtro
        filter_layout.addRow(button_row)

        queries_layout.addWidget(filter_frame)

        # Tabla para resultados
        self.query_table_view = QTableView()
        self.query_table_view.setAlternatingRowColors(True)
        self.query_table_view.setSelectionBehavior(QTableView.SelectRows)
        self.query_table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.query_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.query_table_view.verticalHeader().setVisible(False)
        self.query_table_view.verticalHeader().setDefaultSectionSize(50)

        # Modelo para la tabla de consultas
        self.query_model = FinanzasTableModel()
        self.query_table_view.setModel(self.query_model)

        queries_layout.addWidget(self.query_table_view)

        self.stacked_widget.addWidget(queries_view_widget)

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
            
    def loadDataMain(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Get all finance records
            cursor.execute("SELECT * FROM finanza ORDER BY fin_fecha DESC")
            self.finance_data = cursor.fetchall()
            
            # Update table model
            self.table_model.refreshData(self.finance_data)
            
            # Configure the action buttons in the last column
            for row in range(len(self.finance_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Edit button
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editFinanceRecord(r))
                layout.addWidget(edit_btn)
                
                # Delete button
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteFinanceRecord(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Set the widget as the cell's widget
                self.table_view.setIndexWidget(self.table_model.index(row, 6), widget)
                
            # Load data for charts
            cursor.execute("SELECT fin_fecha, SUM(fin_monto) FROM finanza WHERE fin_tipo = 'ingreso' GROUP BY fin_fecha ORDER BY fin_fecha")
            income_data = cursor.fetchall()
            
            cursor.execute("SELECT fin_fecha, SUM(fin_monto) FROM finanza WHERE fin_tipo = 'gasto' GROUP BY fin_fecha ORDER BY fin_fecha")
            expense_data = cursor.fetchall()
            
            cursor.execute("SELECT SUM(fin_monto) FROM finanza WHERE fin_tipo = 'ingreso'")
            income_total = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(fin_monto) FROM finanza WHERE fin_tipo = 'gasto'")
            expense_total = cursor.fetchone()[0] or 0
            
            # Update charts
            self.time_chart.plot_income_expense(income_data, expense_data)
            self.summary_chart.plot_summary_pie(income_total, expense_total)
            
            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def loadQueryData(self):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            if start_date > end_date:
                QMessageBox.critical(
                    self,
                    "Error en Fechas",
                    "La <b>fecha de inicio<\b> no puede ser posterior a la <b>fecha de fin<\b>.\n"
                    f"Por favor, ajusta las fechas:\n"
                    f"Inicio: {start_date}\n"
                    f"Fin: {end_date}"
                )
            cursor.execute("""
                SELECT fin_id, fin_usu_id, fin_fecha, fin_desc, fin_monto, fin_tipo 
                FROM finanza 
                WHERE fin_fecha BETWEEN %s AND %s
                ORDER BY fin_fecha DESC
            """, (start_date, end_date))
            
            query_data = cursor.fetchall()
            self.query_model.refreshData(query_data)
            
            # Configuramos los botones de accion en la ultima columna
            for row in range(len(query_data)):
                # Create a widget to hold the buttons
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(4, 4, 4, 4)
                
                # Edit button
                edit_btn = QPushButton("Editar")
                edit_btn.setFixedWidth(90)
                edit_btn.setFixedHeight(30)
                edit_btn.clicked.connect(lambda _, r=row: self.editFinanceRecord(r))
                layout.addWidget(edit_btn)
                
                # Delete button
                delete_btn = QPushButton("Eliminar")
                delete_btn.setObjectName("deleteBtn")
                delete_btn.setFixedWidth(90)
                delete_btn.setFixedHeight(30)
                delete_btn.clicked.connect(lambda _, r=row: self.deleteFinanceRecord(r))
                layout.addWidget(delete_btn)
                
                layout.setAlignment(Qt.AlignCenter)
                widget.setLayout(layout)
                
                # Set the widget as the cell's widget
                #self.table_view.setIndexWidget(self.table_model.index(row, 6), widget)
                #self.query_model.setIndexWidget(self.query_model.index(row, 6), widget)
                self.query_table_view.setIndexWidget(self.query_model.index(row, 6), widget)

            cursor.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al cargar datos: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def showTotal(self, tipo):
        if not self.connectToDatabase():
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Consulta para el total
            cursor.execute("""
                SELECT SUM(fin_monto) FROM finanza WHERE fin_tipo = %s
            """, (tipo,))
            
            total = cursor.fetchone()[0] or 0
            
            # Consulta para el total en el rango de fechas seleccionado
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            cursor.execute("""
                SELECT SUM(fin_monto) FROM finanza 
                WHERE fin_tipo = %s AND fin_fecha BETWEEN %s AND %s
            """, (tipo, start_date, end_date))
            
            total_periodo = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            # Mostrar los resultados en un QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Control de {'Ingresos' if tipo == 'ingreso' else 'Gastos'}")
            msg.setIcon(QMessageBox.Information)
            
            message = f"""
            <b>Total general:</b> ${total:,.2f}<br><br>
            <b>Total en el período seleccionado ({start_date} a {end_date}):</b> ${total_periodo:,.2f}
            """
            
            msg.setText(message)
            msg.exec_()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"Error al calcular totales: {err}")
        finally:
            if self.db_connection:
                self.db_connection.close()

    def addFinanceRecord(self, usu_id):
        dialog = FinanzasDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            finance_data = dialog.getFinanceData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                # Get current user ID (assuming it's stored somewhere)
                # For now, we'll use a placeholder value of 1
                user_id = usu_id
                
                query = """
                INSERT INTO finanza (fin_usu_id, fin_fecha, fin_desc, fin_monto, fin_tipo)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user_id,
                    finance_data["fecha"],
                    finance_data["desc"],
                    finance_data["monto"],
                    finance_data["tipo"]
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro agregado correctamente")
                self.loadDataMain()
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al agregar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()
                    
    def editFinanceRecord(self, row):
        record = self.finance_data[row]
        
        dialog = FinanzasDialog(self, record)
        if dialog.exec_() == QDialog.Accepted:
            finance_data = dialog.getFinanceData()
            
            if not self.connectToDatabase():
                return
                
            try:
                cursor = self.db_connection.cursor()
                
                query = """
                UPDATE finanza
                SET fin_fecha = %s, fin_desc = %s, fin_monto = %s, fin_tipo = %s
                WHERE fin_id = %s
                """
                cursor.execute(query, (
                    finance_data["fecha"],
                    finance_data["desc"],
                    finance_data["monto"],
                    finance_data["tipo"],
                    record[0]  # fin_id
                ))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro actualizado correctamente")
                self.loadDataMain()
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al actualizar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()
                    
    def deleteFinanceRecord(self, row):
        record = self.finance_data[row]
        
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
                
                query = "DELETE FROM finanza WHERE fin_id = %s"
                cursor.execute(query, (record[0],))
                
                self.db_connection.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Registro eliminado correctamente")
                self.loadDataMain()
                
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de base de datos", f"Error al eliminar registro: {err}")
            finally:
                if self.db_connection:
                    self.db_connection.close()
                    
    def logout(self):
        self.close()
        self.loginWindow.show()