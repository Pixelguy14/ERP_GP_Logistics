CREATE DATABASE gp_logistics;

USE gp_logistics;

-- Tabla de Usuarios
CREATE TABLE usuario (
    usu_id INT PRIMARY KEY AUTO_INCREMENT,
    usu_nombre VARCHAR(100) NOT NULL,
    usu_correo VARCHAR(100) NOT NULL UNIQUE,
    usu_contra VARCHAR(255) NOT NULL,
    usu_puesto VARCHAR(50) NOT NULL,
    usu_fecha_contratacion DATE NOT NULL,
    usu_salario DECIMAL(10, 2) NOT NULL,
    usu_mod ENUM('Finanzas', 'Recursos Humanos', 'Logistica', 'Compras', 'Ventas', 'Mantenimiento', 'Gestion')
);
# Gestion = administrador, o dueño.

-- Tabla de Finanzas
CREATE TABLE finanza (
    fin_id INT PRIMARY KEY AUTO_INCREMENT,
    fin_usu_id INT,
    fin_fecha DATE NOT NULL,
    fin_desc VARCHAR(255),
    fin_monto DECIMAL(10, 2) NOT NULL,
    fin_tipo ENUM('ingreso', 'gasto') NOT NULL,
    FOREIGN KEY (fin_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Recursos Humanos
CREATE TABLE recursoshumanos (
    reh_id INT PRIMARY KEY AUTO_INCREMENT,
    reh_usu_id INT,
    reh_estado ENUM('Activo', 'Inactivo', 'Baja') NOT NULL,
    reh_tipo_contrato ENUM('Tiempo completo', 'Medio tiempo', 'Temporal') NOT NULL,
    reh_beneficios TEXT,
    reh_observaciones TEXT,
    FOREIGN KEY (reh_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Evaluación de Desempeño (Función de RH)
CREATE TABLE evaluacion_desempeno (
    eva_id INT PRIMARY KEY AUTO_INCREMENT,
    eva_usu_id INT,
    eva_fecha DATE NOT NULL,
    eva_puntaje INT NOT NULL CHECK (eva_puntaje BETWEEN 1 AND 10),
    eva_comentarios TEXT,
    FOREIGN KEY (eva_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Logística
CREATE TABLE logistica (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    log_usu_id INT,
    log_origen VARCHAR(100) NOT NULL,
    log_destino VARCHAR(100) NOT NULL,
    log_fecha_salida DATE NOT NULL,
    log_fecha_llegada DATE,
    log_estado ENUM('Planificado', 'En proceso', 'Completado') NOT NULL,
    FOREIGN KEY (log_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Almacenes (Función de Logística)
CREATE TABLE almacen (
    alm_id INT PRIMARY KEY AUTO_INCREMENT,
    alm_nombre VARCHAR(100) NOT NULL,
    alm_ubicacion VARCHAR(255) NOT NULL
);

-- Tabla de Inventario (Función de Logística)
CREATE TABLE inventario (
    inv_id INT PRIMARY KEY AUTO_INCREMENT,
    inv_alm_id INT,
    inv_producto VARCHAR(100) NOT NULL,
    inv_cantidad INT NOT NULL,
    FOREIGN KEY (inv_alm_id) REFERENCES almacen(alm_id)
);

-- Tabla de Solicitudes de Compra (Función de Compras)
CREATE TABLE solicitud_compra (
    sol_id INT PRIMARY KEY AUTO_INCREMENT,
    sol_usu_id INT,
    sol_fecha DATE NOT NULL,
    sol_descripcion TEXT,
    sol_estado ENUM('Pendiente', 'Aprobada', 'Rechazada') NOT NULL,
    FOREIGN KEY (sol_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Compras
CREATE TABLE compra (
    com_id INT PRIMARY KEY AUTO_INCREMENT,
    com_proveedor INT,
    com_usu_id INT,
    com_fecha_compra DATE NOT NULL,
    com_sol_id INT,
    com_monto_total DECIMAL(10, 2) NOT NULL,
    com_estado ENUM('Pendiente', 'Completada') NOT NULL,
    FOREIGN KEY (com_usu_id) REFERENCES usuario(usu_id),
    FOREIGN KEY (com_sol_id) REFERENCES solicitud_compra(sol_id)
);

-- Tabla de Ventas
CREATE TABLE venta (
    ven_id INT PRIMARY KEY AUTO_INCREMENT,
    ven_cliente INT,
    ven_usu_id INT,
    ven_fecha_venta DATE NOT NULL,
    ven_monto_total DECIMAL(10, 2) NOT NULL,
    ven_estado ENUM('Pendiente', 'Completada') NOT NULL,
    FOREIGN KEY (ven_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Mantenimiento
CREATE TABLE mantenimiento (
    man_id INT PRIMARY KEY AUTO_INCREMENT,
    man_vehiculo_id INT,
    man_usu_id INT,
    man_fecha_programada DATE NOT NULL,
    man_descripcion VARCHAR(255),
    man_costo DECIMAL(10, 2),
    man_estado ENUM('Pendiente', 'Completado') NOT NULL,
    FOREIGN KEY (man_usu_id) REFERENCES usuario(usu_id)
);

-- Tabla de Incidencias (Función de Mantenimiento)
CREATE TABLE incidencia (
    inc_id INT PRIMARY KEY AUTO_INCREMENT,
    inc_usu_id INT,
    inc_fecha DATE NOT NULL,
    inc_descripcion TEXT,
    inc_estado ENUM('Reportada', 'En revisión', 'Resuelta') NOT NULL,
    FOREIGN KEY (inc_usu_id) REFERENCES usuario(usu_id)
);

-- Vinculacion de las ventas con el inventario
CREATE TABLE detalle_venta (
    dv_id INT PRIMARY KEY AUTO_INCREMENT,
    ven_id INT,
    inv_id INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (ven_id) REFERENCES venta(ven_id),
    FOREIGN KEY (inv_id) REFERENCES inventario(inv_id)
);

-- Vinculacion de la compra con el inventario
CREATE TABLE detalle_compra (
    dc_id INT PRIMARY KEY AUTO_INCREMENT,
    com_id INT,
    inv_id INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (com_id) REFERENCES compra(com_id),
    FOREIGN KEY (inv_id) REFERENCES inventario(inv_id)
);

-- Vinculacion de solicitud de compra con inventario
CREATE TABLE detalle_solicitud (
    ds_id INT PRIMARY KEY AUTO_INCREMENT,
    sol_id INT,
    inv_id INT,
    cantidad INT NOT NULL,
    FOREIGN KEY (sol_id) REFERENCES solicitud_compra(sol_id),
    FOREIGN KEY (inv_id) REFERENCES inventario(inv_id)
);
