# cd Documents/DICIS_8vo_2025/Topicos_Selectos_Sistemas_Informacion/Python/
# python3 -m venv ./
# source /home/pixel/Documents/DICIS_8vo_2025/Topicos_Selectos_Sistemas_Informacion/Python/bin/activate
# source /home/pixelguy14/Documentos/DICIS_8vo/Topicos_selectos_sistemas_de_informacion/ERP_GP_Logistics/bin/activate
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
import mysql.connector
from dotenv import load_dotenv
import os
from finanzas import *
from recursoshumanos import *
from logistica import *
from gestion import *

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('GP Logistics ERP')
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QLabel#title_label {
                font-size: 24px;
                font-weight: bold;
                font-family: Arial;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton#forgotBtn {
                background-color: transparent;
                color: #4a86e8;
                text-align: left;
                padding: 5px;
            }
            QPushButton#forgotBtn:hover {
                color: #3a76d8;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Logo/Header
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pixmap = QPixmap("Logo-Grupo-Porteo.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(header_layout)

        title_label = QLabel("Inicio de sesion")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Por favor rellene los campos con\nsu cuenta para iniciar sesión")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(20)

        correo_label = QLabel("Correo")
        correo_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(correo_label)

        self.correo_input = QLineEdit()
        self.correo_input.setPlaceholderText("Ingrese su Correo")
        self.correo_input.setMinimumHeight(40)
        main_layout.addWidget(self.correo_input)

        main_layout.addSpacing(10)

        contra_label = QLabel("Contraseña")
        contra_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(contra_label)

        self.contra_input = QLineEdit()
        self.contra_input.setPlaceholderText("Ingrese su Contraseña")
        self.contra_input.setEchoMode(QLineEdit.Password)
        self.contra_input.setMinimumHeight(40)
        main_layout.addWidget(self.contra_input)

        options_layout = QHBoxLayout()

        self.remember_checkbox = QCheckBox("Recordar Cuenta?")
        options_layout.addWidget(self.remember_checkbox)

        forgot_btn = QPushButton("Olvidé mi Contraseña")
        forgot_btn.setObjectName("forgotBtn")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.clicked.connect(self.OlvideContra)
        options_layout.addWidget(forgot_btn, alignment=Qt.AlignRight)

        main_layout.addLayout(options_layout)

        main_layout.addSpacing(20)

        login_btn = QPushButton("Entrar")
        login_btn.setMinimumHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        main_layout.addWidget(login_btn)
        """
        register_layout = QHBoxLayout()
        register_label = QLabel("Don't have an account?")
        register_layout.addWidget(register_label)

        register_btn = QPushButton("Register")
        register_btn.setObjectName("forgotBtn")
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(self.register)
        register_layout.addWidget(register_btn)
        main_layout.addLayout(register_layout)
        """
        # Add stretch to push everything to the top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def login(self):
        correo = self.correo_input.text()
        contra = self.contra_input.text()

        if not correo or not contra:
            QMessageBox.warning(self, "Inicio de sesión fallido", "Por favor ingresar correo y contraseña")
            return

        try:
            conn = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                database=os.environ.get("DB_DATABASE"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD")
            )
            cursor = conn.cursor(dictionary=True)
            
            query = f"SELECT usu_contra, usu_mod FROM usuario WHERE usu_correo = %s"
            cursor.execute(query, (correo,))
            resultado = cursor.fetchone()
            # Guardamos el id_usu en una variable para poder hacer requests con el usuario 
            query = f"SELECT usu_id from usuario WHERE usu_correo = %s and usu_contra = %s"
            cursor.execute(query, (correo, contra))
            usu_id = cursor.fetchone()
            
            if resultado and resultado["usu_contra"] == contra:
                #print(f"estado del recuerdo: {self.remember_checkbox.isChecked()}")
                if not self.remember_checkbox.isChecked(): # limpiamos el texto
                    self.correo_input.clear()
                    self.contra_input.clear()
                #QMessageBox.information(self, "Inicio de sesión exitoso", f"Bienvenido, {correo}!")
                if resultado["usu_mod"] == "Finanzas":
                    print("interfaz de Finanzas")
                    #print("Creando instancia de FinanzasWindow...")
                    self.finanzas_window = FinanzasWindow(self, usu_id)
                    #print("Aplicando atributos...")
                    self.finanzas_window.setAttribute(Qt.WA_DeleteOnClose, False)  # Evita que se elimine automáticamente
                    #print("Mostrando ventana...")
                    self.finanzas_window.show()
                elif resultado["usu_mod"] == "Recursos Humanos":
                    print("interfaz de Recursos Humanos")
                    self.RRHH_window = RRHHWindow(self, usu_id)
                    self.RRHH_window.show()
                elif resultado["usu_mod"] == "Logistica":
                    print("interfaz de Logistica")
                    self.Logistica_window = LogisticaWindow(self, usu_id)
                    self.Logistica_window.show()
                elif resultado["usu_mod"] == "Compras":
                    print("interfaz de Compras")
                elif resultado["usu_mod"] == "Ventas":
                    print("interfaz de Ventas")
                elif resultado["usu_mod"] == "Mantenimiento":
                    print("interfaz de Mantenimiento")
                elif resultado["usu_mod"] == "Gestion":
                    print("interfaz de Gestion")
                    self.gestion_window = GestionWindow(self)
                    self.gestion_window.show()
                self.hide()
                #self.show()
            else:
                QMessageBox.warning(self, "Inicio de sesión fallido", "Correo o contraseña incorrectos")

            cursor.close()
            conn.close()
            #self.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"No se pudo conectar: {err}")
    def OlvideContra(self):
        dialog = DialogOlvideContra()
        dialog.exec_()

class DialogOlvideContra(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recuperación de Contraseña")
        self.setMinimumSize(200, 150)
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Cambiar Contraseña')
        self.setFixedSize(self.sizeHint())
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QLabel#title_label {
                font-size: 24px;
                font-weight: bold;
                font-family: Arial;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton#forgotBtn {
                background-color: transparent;
                color: #4a86e8;
                text-align: left;
                padding: 5px;
            }
            QPushButton#forgotBtn:hover {
                color: #3a76d8;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        subtitle_label = QLabel("Por favor rellene los campos con su\ncuenta para cambiar su contraseña")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(20)

        correo_label = QLabel("Correo")
        correo_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(correo_label)

        self.correo_input = QLineEdit()
        self.correo_input.setPlaceholderText("Ingrese su Correo")
        self.correo_input.setMinimumHeight(40)
        main_layout.addWidget(self.correo_input)

        main_layout.addSpacing(10)

        contra_label = QLabel("Nueva Contraseña")
        contra_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(contra_label)

        self.nueva_contra_input = QLineEdit()
        self.nueva_contra_input.setPlaceholderText("Ingrese su Nueva Contraseña")
        self.nueva_contra_input.setEchoMode(QLineEdit.Password)
        self.nueva_contra_input.setMinimumHeight(40)
        main_layout.addWidget(self.nueva_contra_input)

        main_layout.addSpacing(10)

        contra_label = QLabel("Ingrese de Nuevo la Nueva Contraseña")
        contra_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(contra_label)

        self.nueva_contra_input2 = QLineEdit()
        self.nueva_contra_input2.setPlaceholderText("Ingrese su Nueva Contraseña")
        self.nueva_contra_input2.setEchoMode(QLineEdit.Password)
        self.nueva_contra_input2.setMinimumHeight(40)
        main_layout.addWidget(self.nueva_contra_input2)

        main_layout.addSpacing(20)

        new_contra_btn = QPushButton("Cambiar Contraseña")
        new_contra_btn.setMinimumHeight(50)
        new_contra_btn.setCursor(Qt.PointingHandCursor)
        new_contra_btn.clicked.connect(self.cambiar_contra)
        main_layout.addWidget(new_contra_btn)
        # Add stretch to push everything to the top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def cambiar_contra(self):
        correo = self.correo_input.text()
        nueva_contra = self.nueva_contra_input.text()
        nueva_contra2 = self.nueva_contra_input2.text()

        if not correo or not nueva_contra or not nueva_contra2:
            QMessageBox.warning(self, "Error", "Por favor ingresa tu correo y la nueva contraseña")
            return

        try:
            conn = mysql.connector.connect(
                host=os.environ.get("DB_HOST"),
                database=os.environ.get("DB_DATABASE"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD")
            )
            cursor = conn.cursor(dictionary=True)

            if (nueva_contra==nueva_contra2):
                query = "UPDATE usuario SET usu_contra = %s WHERE usu_correo = %s"
                #print(query,nueva_contra,correo)
                cursor.execute(query, (nueva_contra, correo))
                conn.commit()

                if cursor.rowcount > 0:
                    QMessageBox.information(self, "Cambio exitoso", "Tu contraseña ha sido actualizada correctamente.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "No se encontró una cuenta con ese correo.")
            else:
                QMessageBox.information(self, "Error", "Ambas contraseñas deben ser iguales.")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de base de datos", f"No se pudo actualizar la contraseña: {err}")