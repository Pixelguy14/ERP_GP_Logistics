# Método de Instalación:
Para compilar y ejecutar el proyecto, siga los siguientes pasos:
## Instalación de MySQL: 
Asegúrese de tener MySQL Server instalado en su sistema. Puede utilizar MySQL
Workbench para una gestión más sencilla de la base de datos.
## Carga de la Base de Datos:
Ejecute los scripts SQL proporcionados en MySQL o MySQL Workbench para crear la base de datos y cargar
los datos iniciales:
ERP_GP_logistics.sql (para la creación de la estructura de la base de datos)
ERP_inserts.sql (para la inserción de datos de ejemplo)
## Cree un usuario para la aplicación y otorgue los permisos necesarios:
CREATE USER 'gp_log'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON gp_logistics.* TO 'gp_log'@'localhost';
FLUSH PRIVILEGES;
## Configuración del Entorno Python:
Es altamente recomendable crear un entorno virtual para gestionar las dependencias del proyecto:
python3 -m venv .env # Crea un entorno virtual llamado .env
source .env/bin/activate # Activa el entorno virtual (Linux/macOS)
#Para Windows: .env\Scripts\activate
## Instale las librerías de Python requeridas:
pip install mysql-connector-python
pip install python-dotenv
pip install matplotlib
pip install pyqt5

## Ejecute el codigo con:
python3 ERP_logistics.py
