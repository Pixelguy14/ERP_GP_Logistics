USE gp_logistics;

-- Insert para la tabla usuario (un insert por cada usu_mod)
INSERT INTO usuario (usu_nombre, usu_correo, usu_contra, usu_puesto, usu_fecha_contratacion, usu_salario, usu_mod) VALUES
('Ana Financiera', 'ana.financiera@ejemplo.com', 'passFinanzas123', 'Analista Financiero', '2024-01-15', 55000.00, 'Finanzas'),
('Carlos RRHH', 'carlos.rrhh@ejemplo.com', 'passRRHH456', 'Especialista de RRHH', '2023-05-20', 60000.00, 'Recursos Humanos'),
('Laura Logistica', 'laura.logistica@ejemplo.com', 'passLogistica789', 'Coordinador de Logística', '2022-11-01', 65000.00, 'Logistica'),
('Pedro Compras', 'pedro.compras@ejemplo.com', 'passCompras101', 'Comprador Senior', '2023-03-10', 58000.00, 'Compras'),
('Sofia Ventas', 'sofia.ventas@ejemplo.com', 'passVentas222', 'Ejecutivo de Ventas', '2024-02-28', 52000.00, 'Ventas'),
('Javier Mantenimiento', 'javier.mantenimiento@ejemplo.com', 'passMantenimiento333', 'Técnico de Mantenimiento', '2023-07-01', 48000.00, 'Mantenimiento'),
('Elena Gestion', 'elena.gestion@ejemplo.com', 'passGestion444', 'Gerente General', '2022-08-05', 80000.00, 'Gestion');

-- Inserts para la tabla finanza (10 inserts)
INSERT INTO finanza (fin_usu_id, fin_fecha, fin_desc, fin_monto, fin_tipo) VALUES
(1, '2025-05-01', 'Pago de factura #12345', 1250.50, 'gasto'),
(1, '2025-05-03', 'Ingreso por venta #V001', 2800.00, 'ingreso'),
(1, '2025-05-05', 'Reembolso de gastos de viaje', 85.75, 'ingreso'),
(1, '2025-05-08', 'Pago de nómina (quincena)', 15000.00, 'gasto'),
(1, '2025-05-10', 'Ingreso por servicio #S002', 3500.00, 'ingreso'),
(1, '2025-05-12', 'Compra de material de oficina', 210.99, 'gasto'),
(1, '2025-05-15', 'Pago de alquiler de oficina', 5000.00, 'gasto'),
(1, '2025-05-17', 'Ingreso por venta #V003', 1950.00, 'ingreso'),
(1, '2025-05-20', 'Pago de publicidad online', 380.25, 'gasto'),
(1, '2025-05-22', 'Ingreso por ajuste contable', 120.00, 'ingreso');

-- Inserts para la tabla recursoshumanos (10 inserts)
INSERT INTO recursoshumanos (reh_usu_id, reh_estado, reh_tipo_contrato, reh_beneficios, reh_observaciones) VALUES
(2, 'Activo', 'Tiempo completo', 'Seguro médico, vacaciones pagadas, bono anual', 'Empleado con buen desempeño.'),
(2, 'Activo', 'Medio tiempo', 'Seguro médico parcial, vacaciones proporcionales', 'Trabaja 20 horas a la semana.'),
(2, 'Baja', 'Tiempo completo', 'Seguro médico, vacaciones pagadas', 'Renunció el 2025-04-30.'),
(2, 'Activo', 'Temporal', 'Ninguno', 'Contratado por 3 meses para proyecto específico.'),
(2, 'Activo', 'Tiempo completo', 'Seguro dental, seguro de vida, vacaciones pagadas', 'Excelente actitud y proactividad.'),
(2, 'Inactivo', 'Medio tiempo', 'Seguro médico parcial', 'Actualmente de licencia por maternidad.'),
(2, 'Activo', 'Tiempo completo', 'Seguro médico, plan de jubilación, vacaciones pagadas', 'Líder de equipo.'),
(2, 'Activo', 'Temporal', 'Ninguno', 'Apoyo durante la temporada alta.'),
(2, 'Activo', 'Tiempo completo', 'Seguro médico, vales de despensa, vacaciones pagadas', 'Recién contratado, en periodo de prueba.'),
(2, 'Activo', 'Medio tiempo', 'Seguro médico parcial, bono por desempeño', 'Estudiante universitario.');

-- Inserts para la tabla evaluacion_desempeno (10 inserts)
INSERT INTO evaluacion_desempeno (eva_usu_id, eva_fecha, eva_puntaje, eva_comentarios) VALUES
(2, '2024-07-15', 8, 'Buen desempeño general, áreas de mejora en comunicación.'),
(3, '2024-08-01', 9, 'Superó las expectativas en la gestión de envíos.'),
(4, '2024-07-20', 7, 'Cumplió con los objetivos, necesita mejorar la organización.'),
(5, '2024-08-10', 10, 'Excelente desempeño en ventas, superó cuotas.'),
(6, '2024-07-25', 8, 'Mantenimiento preventivo realizado eficientemente.'),
(1, '2024-09-01', 9, 'Análisis financiero preciso y oportuno.'),
(3, '2025-01-15', 8, 'Mejora continua en la planificación logística.'),
(4, '2025-02-01', 7, 'Negociación efectiva con proveedores.'),
(5, '2025-01-20', 9, 'Excelente atención al cliente y cierre de ventas.'),
(6, '2025-02-10', 10, 'Resolución rápida y efectiva de incidencias.');

-- Inserts para la tabla logistica (10 inserts)
INSERT INTO logistica (log_usu_id, log_origen, log_destino, log_fecha_salida, log_fecha_llegada, log_estado) VALUES
(3, 'Ciudad de México', 'Guadalajara', '2025-05-05', '2025-05-07', 'Completado'),
(3, 'Monterrey', 'Puebla', '2025-05-08', '2025-05-10', 'En proceso'),
(3, 'Tijuana', 'León', '2025-05-12', '2025-05-15', 'Planificado'),
(3, 'Querétaro', 'Oaxaca', '2025-05-18', '2025-05-20', 'Planificado'),
(3, 'Mérida', 'Villahermosa', '2025-05-02', '2025-05-04', 'Completado'),
(3, 'San Luis Potosí', 'Chihuahua', '2025-05-10', '2025-05-14', 'En proceso'),
(3, 'Aguascalientes', 'Morelia', '2025-05-15', '2025-05-17', 'Planificado'),
(3, 'Hermosillo', 'Culiacán', '2025-05-20', '2025-05-22', 'Planificado'),
(3, 'Toluca', 'Tuxtla Gutiérrez', '2025-05-07', '2025-05-11', 'Completado'),
(3, 'Zacatecas', 'Saltillo', '2025-05-13', '2025-05-16', 'En proceso');

-- Inserts para la tabla almacen (10 inserts)
INSERT INTO almacen (alm_nombre, alm_ubicacion) VALUES
('Almacén Central CDMX', 'Calle Principal #123, Ciudad de México'),
('Bodega Guadalajara', 'Avenida López Mateos Sur #456, Guadalajara'),
('Centro de Distribución Monterrey', 'Parque Industrial #789, Monterrey'),
('Almacén Puebla', 'Carretera Federal #101, Puebla'),
('Bodega Tijuana', 'Zona Industrial #202, Tijuana'),
('Almacén León', 'Bulevar Aeropuerto #303, León'),
('Centro de Almacenamiento Querétaro', 'Parque Tecnológico #404, Querétaro'),
('Bodega Oaxaca', 'Calle Independencia #505, Oaxaca'),
('Almacén Mérida', 'Anillo Periférico #606, Mérida'),
('Centro Logístico Villahermosa', 'Avenida Paseo Tabasco #707, Villahermosa');

-- Inserts para la tabla inventario (10 inserts)
INSERT INTO inventario (inv_alm_id, inv_producto, inv_cantidad) VALUES
(1, 'Laptop Dell XPS 15', 50),
(1, 'Monitor LG 27 pulgadas', 100),
(2, 'Teclado mecánico Logitech', 75),
(2, 'Mouse inalámbrico Razer', 120),
(3, 'Impresora HP LaserJet Pro', 30),
(3, 'Toner HP Negro', 200),
(4, 'Silla ergonómica Herman Miller', 40),
(4, 'Escritorio de oficina ajustable', 60),
(5, 'Cable HDMI 1.5m', 300),
(5, 'Adaptador USB-C', 150);

-- Inserts para la tabla solicitud_compra (10 inserts)
INSERT INTO solicitud_compra (sol_usu_id, sol_fecha, sol_descripcion, sol_estado) VALUES
(4, '2025-05-01', 'Solicitud de 50 laptops Dell XPS 15 para nuevos empleados.', 'Pendiente'),
(4, '2025-05-03', 'Requisición de material de oficina: resmas de papel, bolígrafos, etc.', 'Aprobada'),
(4, '2025-05-05', 'Pedido urgente de 10 sillas ergonómicas para el departamento de ventas.', 'Pendiente'),
(4, '2025-05-08', 'Solicitud de compra de software de gestión de proyectos.', 'Aprobada'),
(4, '2025-05-10', 'Requisición de 20 monitores LG de 27 pulgadas.', 'Pendiente'),
(4, '2025-05-12', 'Solicitud de compra de licencias de antivirus para todas las estaciones de trabajo.', 'Aprobada'),
(4, '2025-05-15', 'Pedido de 3 impresoras HP LaserJet Pro para diferentes áreas.', 'Pendiente'),
(4, '2025-05-17', 'Requisición de 10 teclados mecánicos Logitech.', 'Aprobada'),
(4, '2025-05-20', 'Solicitud de compra de un nuevo servidor para el departamento de TI.', 'Pendiente'),
(4, '2025-05-22', 'Requisición de 150 mouse inalámbricos Razer.', 'Aprobada');

-- Inserts para la tabla compra (10 inserts)
INSERT INTO compra (com_proveedor, com_usu_id, com_fecha_compra, com_sol_id, com_monto_total, com_estado) VALUES
(101, 4, '2025-05-08', 2, 5500.75, 'Completada'),
(102, 4, '2025-05-15', 4, 12000.50, 'Completada'),
(103, 4, '2025-05-22', 6, 3800.99, 'Completada'),
(104, 4, '2025-05-29', 8, 1875.20, 'Pendiente'),
(101, 4, '2025-06-05', 10, 4200.00, 'Pendiente'),
(105, 4, '2025-05-10', 1, 22500.00, 'Completada'),
(102, 4, '2025-05-18', 3, 6000.00, 'Completada'),
(103, 4, '2025-05-25', 5, 7500.00, 'Pendiente'),
(104, 4, '2025-06-01', 7, 1500.50, 'Pendiente'),
(105, 4, '2025-06-08', 9, 9800.00, 'Pendiente');

-- Inserts para la tabla venta (10 inserts)
INSERT INTO venta (ven_cliente, ven_usu_id, ven_fecha_venta, ven_monto_total, ven_estado) VALUES
(201, 5, '2025-05-03', 2500.00, 'Completada'),
(202, 5, '2025-05-07', 1800.50, 'Completada'),
(203, 5, '2025-05-10', 3200.75, 'Pendiente'),
(204, 5, '2025-05-14', 950.99, 'Completada'),
(205, 5, '2025-05-17', 4100.20, 'Pendiente'),
(201, 5, '2025-05-21', 1200.00, 'Completada'),
(202, 5, '2025-05-24', 2850.60, 'Pendiente'),
(203, 5, '2025-05-28', 675.40, 'Completada'),
(204, 5, '2025-06-01', 5300.80, 'Pendiente'),
(205, 5, '2025-06-05', 1900.15, 'Completada');

-- Inserts para la tabla mantenimiento (10 inserts)
INSERT INTO mantenimiento (man_vehiculo_id, man_usu_id, man_fecha_programada, man_descripcion, man_costo, man_estado) VALUES
(301, 6, '2025-05-10', 'Revisión de motor y cambio de aceite.', 150.00, 'Pendiente'),
(302, 6, '2025-05-15', 'Rotación de neumáticos y alineación.', 85.50, 'Pendiente'),
(303, 6, '2025-05-20', 'Inspección de frenos y cambio de pastillas delanteras.', 220.75, 'Pendiente'),
(304, 6, '2025-05-25', 'Revisión del sistema de suspensión.', 110.20, 'Pendiente'),
(305, 6, '2025-05-30', 'Cambio de filtro de aire y filtro de combustible.', 75.99, 'Pendiente'),
(301, 6, '2025-06-05', 'Mantenimiento preventivo general.', 300.00, 'Pendiente');