USE gp_logistics;

##### Finanzas

### Gestión de facturas
# Facturas de ingresos:
SELECT * FROM finanza WHERE fin_tipo = 'ingreso';
# Facturas de gastos:
SELECT * FROM finanza WHERE fin_tipo = 'gasto';

### Control de gastos: (total de gastos)
SELECT SUM(fin_monto) FROM finanza WHERE fin_tipo = 'gasto';

SELECT SUM(fin_monto) FROM finanza WHERE fin_tipo = 'ingreso';

### Generación de reportes financieros: (reporte anual)
SELECT fin_fecha, fin_desc, fin_monto FROM finanza WHERE fin_fecha BETWEEN '2024-01-01' AND '2024-12-31';
# Transacciones de un dia en especifico
SELECT * FROM finanza WHERE fin_fecha = '2023-10-01';

##### Recursos Humanos

### CRUD tabla recursoshumanos
### Gestion de empleados (ver empleados de X departamento).
SELECT * FROM usuario WHERE usu_mod = 'Recursos Humanos';
# falta CRUD para el empleado, que solo pueden controlar los de recursos humanos, y poder editar el estado, contrato etc. del usuario.

### Gestion de nominas: (ver salarios).
SELECT usu_nombre, usu_salario FROM usuario;

### Evaluación de desempeño: (de empleado X) en una fecha especifica o en general
SELECT * FROM evaluacion_desempeno WHERE eva_usu_id = 1 AND eva_fecha = '2023-10-01';
### CRUD evaluacion de desempeño segun el usuario
SELECT * FROM evaluacion_desempeno WHERE eva_usu_id = 1;

### CRUD Usuarios:
INSERT INTO usuario (usu_id, usu_nombre, usu_correo, usu_contra, usu_puesto, usu_fecha_contratacion, usu_salario, usu_mod) VALUES ();

##### Logistica

### CRUD tabla logistica

### Gestion de gastos internos:
SELECT SUM(fin_monto) FROM finanza WHERE fin_tipo = 'gasto' AND fin_desc LIKE '%interno%';

### Gestión de viajes: (viajes planificados).
SELECT * FROM logistica WHERE log_estado = 'Planificado';

### Manejo de almacenes:
# ver todos los almacenes
SELECT * FROM almacen;

### Manejo de almacenes:
# inventario de un almacén
SELECT * FROM inventario WHERE inv_alm_id = 1;

### Seguimiento de pedidos: (pedidos en proceso)
SELECT * FROM logistica WHERE log_estado = 'En proceso';

### Generación de reportes de logística: (ejemplo de reporte mensual).
SELECT log_origen, log_destino, log_fecha_salida FROM logistica WHERE log_fecha_salida BETWEEN '2025-03-01' AND '2023-03-31';

##### Compra

### Crud tabla compra

### Gestion de proovedores:
SELECT DISTINCT com_proveedor FROM compra;

### CRUD solicitud_compra dependiendo de la compra seleccionada

### CRUD de detalle compra

### Solicitudes de compra pendientes:
SELECT * FROM solicitud_compra WHERE sol_estado = 'Pendiente';

### Control de órdenes de compra por usuario (usuario del ERP con posicion del modulo de compras):
SELECT * FROM compra WHERE com_usu_id = 1;

### Recepción de mercancías: (compras completadas).
SELECT * FROM compra WHERE com_estado = 'Completada';

#### ventas

### Gestión de clientes:

### CRUD de venta 

SELECT DISTINCT ven_cliente FROM venta;

### Creación de cotizaciones: (ventas pendientes).
SELECT * FROM venta WHERE ven_estado = 'Pendiente';

### Seguimiento de ventas: (ventas completadas).
SELECT * FROM venta WHERE ven_estado = 'Completada';

### Generación de reportes de ventas: (reporte mensual).
SELECT ven_fecha_venta, ven_monto_total FROM venta WHERE ven_fecha_venta BETWEEN '2023-10-01' AND '2023-10-31';

### CRUD de detalle_venta

#### mantenimiento

### CRUD de mantenimiento

### Programación de mantenimientos por realizar:
SELECT * FROM mantenimiento WHERE man_estado = 'Pendiente';

### CRUD de incidencia

### Registro de incidencias reportadas:
SELECT * FROM incidencia WHERE inc_estado = 'Reportada';
