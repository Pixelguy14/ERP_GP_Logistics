# cd Documents/DICIS_8vo_2025/Topicos_Selectos_Sistemas_Informacion/Python/
# python3 -m venv ./
# source /home/pixel/Documents/DICIS_8vo_2025/Topicos_Selectos_Sistemas_Informacion/Python/bin/activate
# source /home/pixelguy14/Documentos/DICIS_8vo/Topicos_selectos_sistemas_de_informacion/ERP_GP_Logistics/bin/activate

# pip install mysql-connector-python
# pip install python-dotenv
# pip install matplotlib
# pip install pyqt5
# en mysql terminal: 
# CREATE USER 'gp_log'@'localhost' IDENTIFIED BY '1234'; GRANT ALL PRIVILEGES ON gp_logistics.* TO 'gp_log'@'localhost'; FLUSH PRIVILEGES;
# mysql -u gp_log -p -h localhost
# mysql -u gp_log -p -h 127.0.0.1 -P 3306 -- para fedora
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
import mysql.connector
from dotenv import load_dotenv
from login import *
import os

load_dotenv()
"""
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_DATABASE: {os.environ.get('DB_DATABASE')}")
print(f"DB_USER: {os.environ.get('DB_USER')}")
print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")
"""
try:
    # Obtener las variables de entorno
    db_host = os.environ.get("DB_HOST")
    db_database = os.environ.get("DB_DATABASE")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")

    # Establecer la conexión utilizando las variables de entorno
    conn = mysql.connector.connect(
        host=db_host,
        database=db_database,
        user=db_user,
        password=db_password
    )

    if conn.is_connected():
        print(f"Conexión exitosa a la base de datos: {db_database} en {db_host}")
        cursor = conn.cursor(dictionary=True)

except mysql.connector.Error as err:
    print(f"Error al conectar a MySQL: {err}")

finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
