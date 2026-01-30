from flask import Flask, jsonify, request, send_file
from flask_mysqldb import MySQL
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import io
import base64

from config import config
from frontend import frontend_bp

app = Flask(__name__)

# Configure MySQL BEFORE creating connection
app.config.from_object(config['development'])
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
app.config['MYSQL_INIT_COMMAND'] = "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"

conexion = MySQL(app)

# Configurar encoding al iniciar - CRÍTICO para caracteres especiales
@app.before_request
def before_request():
    if conexion.connection:
        cursor = conexion.connection.cursor()
        # Estos 3 comandos fuerzan UTF-8 en toda la conexión
        cursor.execute("SET NAMES utf8mb4")
        cursor.execute("SET CHARACTER_SET_CLIENT = utf8mb4")
        cursor.execute("SET CHARACTER_SET_RESULTS = utf8mb4")
        cursor.execute("SET CHARACTER_SET_CONNECTION = utf8mb4")
        cursor.close()

# Register frontend blueprint to serve templates/static
app.register_blueprint(frontend_bp)

# ===== API ENDPOINTS FOR CLIENT WEB APP =====

@app.route('/api/restaurantes', methods=['GET'])
def listar_restaurantes():
    try:
        cursor = conexion.connection.cursor()
        alergia_filter = request.args.get('alergia', None)
        
        if alergia_filter:
            # Buscar restaurantes que tengan al menos un plato SIN ese alérgeno
            sql = """SELECT DISTINCT r.ID_RESTAURANTE, r.NOMBRE, r.CIUDAD, r.CCAA, r.T_COMIDA, 
                     r.PRESUPUESTO, r.ESTRELLA_MICH, r.CADENA 
                     FROM restaurantes r
                     WHERE EXISTS (
                         SELECT 1 FROM platos p
                         WHERE p.ID_RESTAURANTE = r.ID_RESTAURANTE
                         AND (p.ID_RESTAURANTE, p.N_PLATO) NOT IN (
                             SELECT al.ID_RESTAURANTE, al.N_PLATO
                             FROM alergias al
                             JOIN alergenos a ON al.NUM_ALERGENO = a.NUM_ALERGENO
                             WHERE a.ALERGENO = %s
                         )
                     )
                     ORDER BY r.ESTRELLA_MICH DESC, r.NOMBRE"""
            cursor.execute(sql, (alergia_filter,))
        else:
            sql = """SELECT ID_RESTAURANTE, NOMBRE, CIUDAD, CCAA, T_COMIDA, 
                     PRESUPUESTO, ESTRELLA_MICH, CADENA 
                     FROM restaurantes ORDER BY ESTRELLA_MICH DESC, NOMBRE"""
            cursor.execute(sql)
            
        datos = cursor.fetchall()
        restaurantes = []
        for fila in datos:
            restaurante = {
                'id': fila[0],
                'nombre': fila[1],
                'ciudad': fila[2],
                'ccaa': fila[3],
                'tipo_comida': fila[4],
                'presupuesto': fila[5],
                'estrellas': fila[6],
                'cadena': fila[7] if fila[7] and fila[7] != 'NULL' else None
            }
            restaurantes.append(restaurante)
        return jsonify({'restaurantes': restaurantes, 'mensaje': 'Restaurantes listados'})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_rest>', methods=['GET'])
def obtener_restaurante(id_rest):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_RESTAURANTE, NOMBRE, CIUDAD, CCAA, T_COMIDA, 
                 PRESUPUESTO, ESTRELLA_MICH, CADENA 
                 FROM restaurantes WHERE ID_RESTAURANTE = %s"""
        cursor.execute(sql, (id_rest,))
        datos = cursor.fetchone()
        if datos:
            restaurante = {
                'id': datos[0],
                'nombre': datos[1],
                'ciudad': datos[2],
                'ccaa': datos[3],
                'tipo_comida': datos[4],
                'presupuesto': datos[5],
                'estrellas': datos[6],
                'cadena': datos[7]
            }
            return jsonify({'restaurante': restaurante})
        else:
            return jsonify({'mensaje': 'Restaurante no encontrado'}), 404
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_rest>/platos', methods=['GET'])
def listar_platos_restaurante(id_rest):
    try:
        cursor = conexion.connection.cursor()
        alergia_filter = request.args.get('alergia', None)
        
        sql = """SELECT N_PLATO, T_PLATO, PRECIO 
                 FROM platos WHERE ID_RESTAURANTE = %s 
                 ORDER BY FIELD(T_PLATO, 'ENTRANTE', 'PRINCIPAL', 'POSTRE', 'BEBIDA'), PRECIO DESC"""
        cursor.execute(sql, (id_rest,))
        datos = cursor.fetchall()
        platos = []
        
        for fila in datos:
            nombre_plato = fila[0]
            tiene_alergeno = False
            
            if alergia_filter:
                # Verificar si el plato contiene el alérgeno
                sql_alergia = """SELECT COUNT(*) FROM alergias al
                                 JOIN alergenos a ON al.NUM_ALERGENO = a.NUM_ALERGENO
                                 WHERE al.ID_RESTAURANTE = %s 
                                 AND al.N_PLATO = %s 
                                 AND a.ALERGENO = %s"""
                cursor.execute(sql_alergia, (id_rest, nombre_plato, alergia_filter))
                tiene_alergeno = cursor.fetchone()[0] > 0
            
            plato = {
                'nombre': nombre_plato,
                'tipo': fila[1],
                'precio': float(fila[2]),
                'sin_alergeno': not tiene_alergeno if alergia_filter else None
            }
            platos.append(plato)
        return jsonify({'platos': platos})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    try:
        data = request.json
        cursor = conexion.connection.cursor()
        
        # Generate unique ID_RESERVA (8 chars)
        import random
        import string
        id_reserva = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        sql = """INSERT INTO reservas (ID_RESERVA, ID_CLIENTE, NUM_PERSONAS, 
                 FECHA_RESERVA, HORA_RESERVA, ID_RESTAURANTE, ESTADO_RESERVA)
                 VALUES (%s, %s, %s, %s, %s, %s, 'Confirmada')"""
        cursor.execute(sql, (id_reserva, data['id_cliente'], data['num_personas'],
                            data['fecha'], data['hora'], data['id_restaurante']))
        conexion.connection.commit()
        return jsonify({'mensaje': 'Reserva creada exitosamente', 'id_reserva': id_reserva})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/reservas/<id_cliente>', methods=['GET'])
def listar_reservas_cliente(id_cliente):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT r.ID_RESERVA, r.NUM_PERSONAS, r.FECHA_RESERVA, r.HORA_RESERVA,
                 r.ESTADO_RESERVA, rest.NOMBRE, rest.CIUDAD, rest.ID_RESTAURANTE
                 FROM reservas r
                 JOIN restaurantes rest ON r.ID_RESTAURANTE = rest.ID_RESTAURANTE
                 WHERE r.ID_CLIENTE = %s
                 ORDER BY r.FECHA_RESERVA DESC, r.HORA_RESERVA DESC"""
        cursor.execute(sql, (id_cliente,))
        datos = cursor.fetchall()
        reservas = []
        for fila in datos:
            # Convertir fecha a string en formato YYYY-MM-DD
            fecha_str = str(fila[2]) if fila[2] else ''
            hora_str = str(fila[3]) if fila[3] else ''
            reserva = {
                'id_reserva': fila[0],
                'num_personas': fila[1],
                'fecha': fecha_str,
                'hora': hora_str,
                'estado': fila[4],
                'restaurante_nombre': fila[5],
                'restaurante_ciudad': fila[6],
                'id_restaurante': fila[7]
            }
            reservas.append(reserva)
        return jsonify({'reservas': reservas})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/reservas', methods=['GET'])
def listar_reservas_restaurante(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT r.ID_RESERVA, r.NUM_PERSONAS, r.FECHA_RESERVA, r.HORA_RESERVA,
                 r.ESTADO_RESERVA, r.ID_CLIENTE, c.N_CLIENTE
                 FROM reservas r
                 JOIN clientes c ON r.ID_CLIENTE = c.ID_CLIENTE
                 WHERE r.ID_RESTAURANTE = %s
                 ORDER BY r.FECHA_RESERVA DESC, r.HORA_RESERVA DESC"""
        cursor.execute(sql, (id_restaurante,))
        datos = cursor.fetchall()
        reservas = []
        for fila in datos:
            reserva = {
                'id_reserva': fila[0],
                'num_personas': fila[1],
                'fecha': str(fila[2]),
                'hora': str(fila[3]),
                'estado': fila[4],
                'id_cliente': fila[5],
                'nombre_cliente': fila[6]
            }
            reservas.append(reserva)
        return jsonify({'reservas': reservas})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/facturas', methods=['GET'])
def listar_facturas_restaurante(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_FACTURA, PRECIO, ID_RESERVA, FECHA_FACTURA
                 FROM facturas
                 WHERE ID_RESTAURANTE = %s
                 ORDER BY FECHA_FACTURA DESC"""
        cursor.execute(sql, (id_restaurante,))
        datos = cursor.fetchall()
        facturas = []
        for fila in datos:
            factura = {
                'id_factura': fila[0],
                'precio': float(fila[1]),
                'id_reserva': fila[2],
                'fecha': str(fila[3])
            }
            facturas.append(factura)
        return jsonify({'facturas': facturas})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/factura/crear', methods=['POST'])
def crear_factura_restaurante():
    try:
        print("=== CREAR FACTURA DESDE RESTAURANTE ===")
        data = request.json
        print(f"Datos recibidos: {data}")
        
        cursor = conexion.connection.cursor()
        
        # Generar ID de factura
        import random
        import string
        from datetime import datetime
        
        id_factura = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        fecha_factura = datetime.now().strftime('%Y-%m-%d')
        
        # Insertar factura con TIPO_VISITA NULL inicialmente
        sql_factura = """INSERT INTO facturas (ID_FACTURA, ID_CLIENTE, ID_RESERVA, 
                        PRECIO, FECHA_FACTURA, ID_RESTAURANTE, TIPO_VISITA)
                        VALUES (%s, %s, %s, %s, %s, %s, NULL)"""
        cursor.execute(sql_factura, (
            id_factura,
            data['id_cliente'],
            data['id_reserva'],
            data['precio'],
            fecha_factura,
            data['id_restaurante']
        ))
        
        # Insertar comandas (cada plato es una comanda)
        for plato in data['platos']:
            sql_comanda = """INSERT INTO comandas (ID_FACTURA, N_PLATO, ID_RESTAURANTE, NUM_PEDIDOS)
                            VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql_comanda, (
                id_factura,
                plato['nombre'],
                data['id_restaurante'],
                plato['cantidad']
            ))
        
        conexion.connection.commit()
        print(f"Factura {id_factura} creada con {len(data['platos'])} platos")
        
        return jsonify({
            'mensaje': 'Factura creada exitosamente',
            'id_factura': id_factura,
            'exito': True
        }), 200
        
    except Exception as ex:
        print(f"Error al crear factura: {ex}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'mensaje': str(ex), 'exito': False}), 500

@app.route('/api/reservas/update/<id_reserva>', methods=['PUT'])
def actualizar_reserva(id_reserva):
    try:
        data = request.json
        cursor = conexion.connection.cursor()
        sql = """UPDATE reservas 
                 SET FECHA_RESERVA = %s, HORA_RESERVA = %s, NUM_PERSONAS = %s
                 WHERE ID_RESERVA = %s"""
        cursor.execute(sql, (data['fecha'], data['hora'], data['num_personas'], id_reserva))
        conexion.connection.commit()
        return jsonify({'mensaje': 'Reserva actualizada exitosamente', 'exito': True}), 200
    except Exception as ex:
        print(f"Error al actualizar reserva: {str(ex)}")
        return jsonify({'mensaje': 'Error al actualizar la reserva', 'exito': False}), 400

@app.route('/api/reservas/cancel/<id_reserva>', methods=['DELETE'])
def cancelar_reserva(id_reserva):
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM reservas WHERE ID_RESERVA = %s"
        cursor.execute(sql, (id_reserva,))
        conexion.connection.commit()
        return jsonify({'mensaje': 'Reserva cancelada exitosamente', 'exito': True}), 200
    except Exception as ex:
        print(f"Error al cancelar reserva: {str(ex)}")
        return jsonify({'mensaje': 'Error al cancelar la reserva', 'exito': False}), 400

@app.route('/api/resenas/<id_cliente>', methods=['GET'])
def listar_resenas_cliente(id_cliente):
    print(f"=== OBTENER RESEÑAS DEL CLIENTE {id_cliente} ===")
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_FACTURA, VALORACION, TIPO_VISITA, ID_RESTAURANTE
                 FROM facturas
                 WHERE ID_CLIENTE = %s AND VALORACION IS NOT NULL"""
        cursor.execute(sql, (id_cliente,))
        datos = cursor.fetchall()
        print(f"Datos obtenidos: {datos}")
        resenas = []
        for fila in datos:
            resena = {
                'id_factura': fila[0],
                'valoracion': float(fila[1]),
                'tipo_visita': fila[2],
                'id_restaurante': fila[3]
            }
            resenas.append(resena)
        print(f"Reseñas procesadas: {resenas}")
        return jsonify({'resenas': resenas})
    except Exception as ex:
        print(f"Error al obtener reseñas: {str(ex)}")
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/resenas', methods=['POST'])
def crear_resena():
    print("=== CREAR RESEÑA ===")
    print("Datos recibidos:", request.json)
    try:
        data = request.json
        cursor = conexion.connection.cursor()
        
        # Buscar si existe una factura asociada a esta reserva/cliente/restaurante
        sql_check = """SELECT ID_FACTURA, VALORACION FROM facturas 
                       WHERE ID_CLIENTE = %s AND ID_RESTAURANTE = %s 
                       ORDER BY FECHA_FACTURA DESC LIMIT 1"""
        cursor.execute(sql_check, (data['id_cliente'], data['id_restaurante']))
        factura = cursor.fetchone()
        
        if not factura:
            # Si no hay factura, no se puede valorar
            return jsonify({'mensaje': 'Debes tener una factura para valorar este restaurante', 'exito': False}), 400
        
        id_factura = factura[0]
        valoracion_existente = factura[1]
        
        # Verificar si ya existe una valoración para esta factura
        if valoracion_existente is not None:
            print("Ya existe una reseña para esta factura")
            return jsonify({'mensaje': 'Ya has valorado este restaurante anteriormente', 'exito': False}), 400
        
        # Actualizar la factura con la valoración y tipo de visita
        tipo_visita = data.get('tipo_visita', 'PAREJA')  # Valor por defecto si no se especifica
        print(f"Actualizando factura: ID_FACTURA={id_factura}, VALORACION={data['valoracion']}, TIPO_VISITA={tipo_visita}")
        
        sql_update_factura = """UPDATE facturas 
                               SET VALORACION = %s, TIPO_VISITA = %s 
                               WHERE ID_FACTURA = %s"""
        cursor.execute(sql_update_factura, (data['valoracion'], tipo_visita, id_factura))
        
        conexion.connection.commit()
        print("Reseña guardada en factura exitosamente")
        return jsonify({'mensaje': 'Reseña guardada exitosamente', 'id_factura': id_factura, 'exito': True}), 200
    except Exception as ex:
        import traceback
        print(f"ERROR COMPLETO al guardar reseña:")
        print(traceback.format_exc())
        return jsonify({'mensaje': 'Error al guardar la reseña', 'exito': False, 'error': str(ex)}), 400

@app.route('/api/facturas/<id_cliente>', methods=['GET'])
def listar_facturas_cliente(id_cliente):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT f.ID_FACTURA, f.PRECIO, f.VALORACION, f.TIPO_VISITA,
                 f.FECHA_FACTURA, rest.NOMBRE, rest.CIUDAD, f.ID_RESERVA, f.ID_RESTAURANTE
                 FROM facturas f
                 JOIN restaurantes rest ON f.ID_RESTAURANTE = rest.ID_RESTAURANTE
                 WHERE f.ID_CLIENTE = %s
                 ORDER BY f.FECHA_FACTURA DESC"""
        cursor.execute(sql, (id_cliente,))
        datos = cursor.fetchall()
        facturas = []
        for fila in datos:
            factura = {
                'id_factura': fila[0],
                'precio': float(fila[1]),
                'valoracion': float(fila[2]) if fila[2] else None,
                'tipo_visita': fila[3],
                'fecha': str(fila[4]),
                'restaurante_nombre': fila[5],
                'restaurante_ciudad': fila[6],
                'id_reserva': fila[7],
                'id_restaurante': fila[8]
            }
            facturas.append(factura)
        print(f"DEBUG: Facturas encontradas para cliente {id_cliente}: {len(facturas)}")
        return jsonify({'facturas': facturas, 'total': len(facturas)})
    except Exception as ex:
        print(f"ERROR en facturas: {str(ex)}")
        return jsonify({'mensaje': f'Error: {str(ex)}', 'facturas': []}), 500

@app.route('/api/reservas/<id_reserva>/factura', methods=['POST'])
def generar_factura_reserva(id_reserva):
    try:
        print(f"=== GENERAR FACTURA PARA RESERVA {id_reserva} ===")
        cursor = conexion.connection.cursor()
        
        # Obtener información de la reserva
        sql_reserva = """SELECT ID_CLIENTE, ID_RESTAURANTE, FECHA_RESERVA 
                        FROM reservas WHERE ID_RESERVA = %s"""
        cursor.execute(sql_reserva, (id_reserva,))
        reserva = cursor.fetchone()
        
        if not reserva:
            return jsonify({'mensaje': 'Reserva no encontrada'}), 404
        
        id_cliente = reserva[0]
        id_restaurante = reserva[1]
        fecha_reserva = reserva[2]
        
        # Verificar si ya existe una factura para esta reserva
        sql_check = "SELECT ID_FACTURA FROM facturas WHERE ID_RESERVA = %s"
        cursor.execute(sql_check, (id_reserva,))
        factura_existente = cursor.fetchone()
        
        if factura_existente:
            return jsonify({
                'mensaje': 'Ya existe una factura para esta reserva',
                'id_factura': factura_existente[0],
                'exito': True
            }), 200
        
        # Generar nueva factura
        import random
        import string
        from datetime import datetime
        
        id_factura = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        precio = round(random.uniform(30, 150), 2)  # Precio aleatorio entre 30 y 150€
        fecha_factura = datetime.now().strftime('%Y-%m-%d')
        
        sql_insert = """INSERT INTO facturas (ID_FACTURA, ID_CLIENTE, ID_RESERVA, 
                        PRECIO, FECHA_FACTURA, ID_RESTAURANTE, TIPO_VISITA)
                        VALUES (%s, %s, %s, %s, %s, %s, NULL)"""
        cursor.execute(sql_insert, (id_factura, id_cliente, id_reserva, 
                                     precio, fecha_factura, id_restaurante))
        conexion.connection.commit()
        
        print(f"Factura {id_factura} generada correctamente para reserva {id_reserva}")
        return jsonify({
            'mensaje': 'Factura generada correctamente',
            'id_factura': id_factura,
            'precio': precio,
            'exito': True
        }), 200
        
    except Exception as ex:
        print(f"Error al generar factura: {ex}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'mensaje': str(ex), 'exito': False}), 500

@app.route('/api/clientes/buscar', methods=['GET'])
def buscar_clientes():
    try:
        nombre = request.args.get('nombre', '')
        id_cliente = request.args.get('id', '')
        cursor = conexion.connection.cursor()
        
        if id_cliente:
            sql = "SELECT ID_CLIENTE, N_CLIENTE, NUM_TELEFONO, EMAIL, ESTUDIOS, SEXO, EDAD FROM clientes WHERE ID_CLIENTE = %s"
            cursor.execute(sql, (id_cliente,))
        elif nombre:
            sql = "SELECT ID_CLIENTE, N_CLIENTE, NUM_TELEFONO, EMAIL, ESTUDIOS, SEXO, EDAD FROM clientes WHERE N_CLIENTE LIKE %s"
            cursor.execute(sql, (f'%{nombre}%',))
        else:
            return jsonify({'clientes': [], 'mensaje': 'Debe proporcionar nombre o ID'})
        
        datos = cursor.fetchall()
        clientes = []
        for fila in datos:
            cliente = {
                'id': fila[0],
                'nombre': fila[1],
                'telefono': fila[2],
                'email': fila[3],
                'estudios': fila[4],
                'sexo': fila[5],
                'edad': fila[6]
            }
            clientes.append(cliente)
        return jsonify({'clientes': clientes, 'mensaje': f'{len(clientes)} cliente(s) encontrado(s)'})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    try:
        cursor = conexion.connection.cursor()
        sql= "SELECT ID_CLIENTE, N_CLIENTE, NUM_TELEFONO, EMAIL, ESTUDIOS, SEXO, EDAD FROM clientes"
        cursor.execute(sql)
        datos = cursor.fetchall()
        clientes = []
        for fila in datos:
            cliente = {'ID_CLIENTE':fila[0], 'N_CLIENTE':fila[1], 'NUM_TELEFONO':fila[2], 'EMAIL':fila[3], 'ESTUDIOS':fila[4], 'SEXO':fila[5], 'EDAD':fila[6]}
            clientes.append(cliente)
        return jsonify({'clientes':clientes, 'mensaje': "Clientes listados."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})
    
@app.route('/clientes/<codigo>', methods=['GET'])
def leer_cliente(codigo):
    try: 
        cursor= conexion.connection.cursor()
        sql= "SELECT ID_CLIENTE, N_CLIENTE, NUM_TELEFONO, EMAIL, ESTUDIOS, SEXO, EDAD FROM clientes WHERE ID_CLIENTE = {0}".format(codigo)
        cursor.execute(sql)
        datos = cursor.fetchone()
        if datos != None:
            cliente = {'ID_CLIENTE':datos[0], 'N_CLIENTE':datos[1], 'NUM_TELEFONO':datos[2], 'EMAIL':datos[3], 'ESTUDIOS':datos[4], 'SEXO':datos[5], 'EDAD':datos[6]}
            return jsonify({'cliente':cliente, 'mensaje': "Cliente encontrado."})
        else:
            return jsonify({'mensaje': "Cliente no encontrado."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})    

@app.route('/clientes', methods=['POST'])
def registrar_cliente():
    print("=== REGISTRO DE CLIENTE ===")
    print("Datos recibidos:", request.json)
    try:
        cursor= conexion.connection.cursor()
        sql="""INSERT INTO clientes (ID_CLIENTE, N_CLIENTE, NUM_TELEFONO, EMAIL, ESTUDIOS, SEXO, EDAD) 
        VALUES ('{0}','{1}',{2},'{3}','{4}','{5}',{6})""".format(request.json['ID_CLIENTE'], 
        request.json['N_CLIENTE'], request.json['NUM_TELEFONO'], request.json['EMAIL'], request.json['ESTUDIOS'], request.json['SEXO'], request.json['EDAD'])
        print("SQL:", sql)
        cursor.execute(sql)
        conexion.connection.commit()
        print("Cliente registrado exitosamente")
        return jsonify({'mensaje': "Cliente registrado exitosamente.", 'exito': True}), 200
    except Exception as ex:
        print(f"ERROR al registrar cliente: {str(ex)}")
        error_msg = "El cliente ya existe" if "Duplicate entry" in str(ex) else "Error al registrar el cliente"
        return jsonify({'mensaje': error_msg, 'exito': False, 'error': str(ex)}), 400 

@app.route('/clientes/<codigo>', methods=['PUT'])
def actualizar_cliente_legacy(codigo):
    try:
        cursor= conexion.connection.cursor()
        sql="""UPDATE clientes 
        SET N_CLIENTE = '{0}', NUM_TELEFONO = {1}, EMAIL = '{2}', ESTUDIOS = '{3}', SEXO = '{4}', EDAD = {5} 
        WHERE ID_CLIENTE = '{6}'""".format(request.json['N_CLIENTE'], 
        request.json['NUM_TELEFONO'], request.json['EMAIL'], request.json['ESTUDIOS'], request.json['SEXO'], request.json['EDAD'], codigo)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': "Cliente actualizado."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"})
    

@app.route('/clientes/<codigo>', methods=['DELETE'])
def eliminar_cliente_legacy(codigo):
    try:
        cursor= conexion.connection.cursor()
        sql="DELETE FROM clientes WHERE ID_CLIENTE = '{0}'".format(codigo)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': "Cliente eliminado."})
    except Exception as ex:
        return jsonify({'mensaje': "Error"}) 

@app.route('/api/clientes/<string:id_cliente>', methods=['PUT'])
def actualizar_cliente(id_cliente):
    try:
        print(f"=== ACTUALIZAR CLIENTE {id_cliente} ===")
        data = request.json
        print(f"Datos recibidos: {data}")
        
        cursor = conexion.connection.cursor()
        
        # Verificar que el cliente existe
        cursor.execute("SELECT ID_CLIENTE FROM clientes WHERE ID_CLIENTE = %s", (id_cliente,))
        if not cursor.fetchone():
            return jsonify({'mensaje': 'Cliente no encontrado'}), 404
        
        # Actualizar cliente (sin modificar ID_CLIENTE)
        sql = """UPDATE clientes 
                 SET N_CLIENTE = %s, EMAIL = %s, NUM_TELEFONO = %s, EDAD = %s, ESTUDIOS = %s 
                 WHERE ID_CLIENTE = %s"""
        cursor.execute(sql, (
            data['nombre'],
            data['email'],
            data['telefono'],
            data['edad'],
            data['estudios'],
            id_cliente
        ))
        conexion.connection.commit()
        
        print(f"Cliente {id_cliente} actualizado correctamente")
        return jsonify({'mensaje': 'Cliente actualizado correctamente'})
        
    except Exception as ex:
        print(f"Error al actualizar cliente: {ex}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'mensaje': str(ex)}), 500

@app.route('/api/clientes/<string:id_cliente>', methods=['DELETE'])
def eliminar_cliente(id_cliente):
    try:
        print(f"=== ELIMINAR CLIENTE {id_cliente} ===")
        
        cursor = conexion.connection.cursor()
        
        # Verificar que el cliente existe
        cursor.execute("SELECT ID_CLIENTE FROM clientes WHERE ID_CLIENTE = %s", (id_cliente,))
        if not cursor.fetchone():
            return jsonify({'mensaje': 'Cliente no encontrado'}), 404
        
        # Eliminar en cascada:
        # 1. Eliminar comandas asociadas a facturas del cliente
        cursor.execute("""DELETE FROM comandas 
                         WHERE ID_FACTURA IN (
                             SELECT ID_FACTURA FROM facturas WHERE ID_CLIENTE = %s
                         )""", (id_cliente,))
        
        # 2. Eliminar facturas del cliente
        cursor.execute("DELETE FROM facturas WHERE ID_CLIENTE = %s", (id_cliente,))
        
        # 3. Eliminar reservas del cliente
        cursor.execute("DELETE FROM reservas WHERE ID_CLIENTE = %s", (id_cliente,))
        
        # 4. Eliminar alergias del cliente
        cursor.execute("DELETE FROM alergias WHERE ID_CLIENTE = %s", (id_cliente,))
        
        # 5. Finalmente, eliminar el cliente
        cursor.execute("DELETE FROM clientes WHERE ID_CLIENTE = %s", (id_cliente,))
        
        conexion.connection.commit()
        
        print(f"Cliente {id_cliente} eliminado correctamente (con todas sus dependencias)")
        return jsonify({'mensaje': 'Cliente eliminado correctamente'})
        
    except Exception as ex:
        print(f"Error al eliminar cliente: {ex}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'mensaje': str(ex)}), 500

@app.route('/api/alergenos', methods=['GET'])
def listar_alergenos():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ALERGENO, NUM_ALERGENO FROM alergenos ORDER BY ALERGENO"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alergenos = []
        for fila in datos:
            alergeno = {
                'nombre': fila[0],
                'num': fila[1]
            }
            alergenos.append(alergeno)
        return jsonify({'alergenos': alergenos})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

# ===== ANALYTICS ENDPOINTS =====

@app.route('/api/restaurantes/<id_restaurante>/analytics/sin-valorar', methods=['GET'])
def clientes_sin_valorar(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        # Clientes con factura pero sin valoración para este restaurante
        sql = """SELECT DISTINCT c.ID_CLIENTE, c.N_CLIENTE, c.EMAIL, c.NUM_TELEFONO,
                 f.ID_FACTURA, f.FECHA_FACTURA
                 FROM facturas f
                 JOIN clientes c ON f.ID_CLIENTE = c.ID_CLIENTE
                 WHERE f.ID_RESTAURANTE = %s 
                 AND (f.VALORACION IS NULL)
                 ORDER BY f.FECHA_FACTURA DESC"""
        cursor.execute(sql, (id_restaurante,))
        datos = cursor.fetchall()
        
        print(f"Clientes sin valorar encontrados: {len(datos)} para restaurante {id_restaurante}")
        
        clientes = []
        for fila in datos:
            cliente = {
                'id_cliente': fila[0],
                'nombre': fila[1],
                'email': fila[2] or 'No disponible',
                'telefono': fila[3] or 'No disponible',
                'id_factura': fila[4],
                'fecha_visita': str(fila[5]) if fila[5] else ''
            }
            clientes.append(cliente)
        
        return jsonify({'clientes': clientes})
    except Exception as ex:
        print(f"Error en clientes_sin_valorar: {ex}")
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/analytics/gasto-medio', methods=['GET'])
def gasto_medio_persona(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        # Calcular gasto medio por persona usando facturas y reservas
        sql = """SELECT AVG(f.PRECIO / r.NUM_PERSONAS) as gasto_medio
                 FROM facturas f
                 JOIN reservas r ON f.ID_RESERVA = r.ID_RESERVA
                 WHERE f.ID_RESTAURANTE = %s"""
        cursor.execute(sql, (id_restaurante,))
        resultado = cursor.fetchone()
        
        gasto_medio = round(resultado[0], 2) if resultado[0] else 0
        
        return jsonify({'gasto_medio': gasto_medio})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/analytics/dia-mas-concurrido', methods=['GET'])
def dia_mas_concurrido(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        # Obtener el día de la semana con más reservas
        sql = """SELECT DAYNAME(FECHA_RESERVA) as dia, COUNT(*) as total
                 FROM reservas
                 WHERE ID_RESTAURANTE = %s
                 GROUP BY DAYNAME(FECHA_RESERVA), DAYOFWEEK(FECHA_RESERVA)
                 ORDER BY total DESC
                 LIMIT 1"""
        cursor.execute(sql, (id_restaurante,))
        resultado = cursor.fetchone()
        
        if resultado:
            # Traducir días al español
            dias_es = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            dia = dias_es.get(resultado[0], resultado[0])
            total = resultado[1]
        else:
            dia = 'N/A'
            total = 0
        
        return jsonify({'dia': dia, 'total': total})
    except Exception as ex:
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/analytics/top-platos', methods=['GET'])
def top_platos(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        # Top 3 platos más pedidos - unir facturas → comandas (N_PLATO es el nombre del plato)
        sql = """SELECT c.N_PLATO, SUM(c.NUM_PEDIDOS) as total_pedidos
                 FROM facturas f
                 JOIN comandas c ON f.ID_FACTURA = c.ID_FACTURA
                 WHERE f.ID_RESTAURANTE = %s
                 GROUP BY c.N_PLATO
                 ORDER BY total_pedidos DESC
                 LIMIT 3"""
        cursor.execute(sql, (id_restaurante,))
        datos = cursor.fetchall()
        
        print(f"Top platos encontrados: {len(datos)} para restaurante {id_restaurante}")
        if datos:
            print(f"Datos: {datos}")
        
        platos = []
        if not datos or len(datos) == 0:
            # Si no hay comandas, mostrar mensaje
            print("No se encontraron platos pedidos en comandas")
            return jsonify({'platos': [], 'mensaje': 'No hay datos de platos pedidos'})
        
        for fila in datos:
            # Buscar el tipo de plato en la tabla platos
            sql_tipo = """SELECT T_PLATO FROM platos 
                         WHERE ID_RESTAURANTE = %s AND N_PLATO = %s
                         LIMIT 1"""
            cursor.execute(sql_tipo, (id_restaurante, fila[0]))
            tipo_result = cursor.fetchone()
            tipo = tipo_result[0] if tipo_result else 'N/A'
            
            plato = {
                'nombre': fila[0],
                'tipo': tipo,
                'total_pedidos': int(fila[1]) if fila[1] else 0
            }
            platos.append(plato)
        
        return jsonify({'platos': platos})
    except Exception as ex:
        print(f"Error en top_platos: {ex}")
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/analytics/grafico-dias', methods=['GET'])
def grafico_dias_semana(id_restaurante):
    try:
        cursor = conexion.connection.cursor()
        
        # Obtener reservas por día de la semana
        sql = """SELECT 
                 DAYOFWEEK(FECHA_RESERVA) as dia_num,
                 DAYNAME(FECHA_RESERVA) as dia_nombre,
                 COUNT(*) as total
                 FROM reservas
                 WHERE ID_RESTAURANTE = %s
                 GROUP BY DAYOFWEEK(FECHA_RESERVA), DAYNAME(FECHA_RESERVA)
                 ORDER BY DAYOFWEEK(FECHA_RESERVA)"""
        cursor.execute(sql, (id_restaurante,))
        datos = cursor.fetchall()
        
        # Mapeo de días (MySQL DAYOFWEEK: 1=Domingo, 2=Lunes, ..., 7=Sábado)
        dias_map = {
            1: 'Domingo', 2: 'Lunes', 3: 'Martes', 4: 'Miércoles',
            5: 'Jueves', 6: 'Viernes', 7: 'Sábado'
        }
        
        # Inicializar todos los días en 0
        dias_data = {dia: 0 for dia in dias_map.values()}
        
        # Rellenar con los datos reales
        for fila in datos:
            dia_num = fila[0]
            total = fila[2]
            dia_nombre = dias_map.get(dia_num, 'Desconocido')
            dias_data[dia_nombre] = total
        
        # Ordenar los días correctamente (Lunes a Domingo)
        dias_ordenados = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dias_labels = dias_ordenados
        dias_valores = [dias_data[dia] for dia in dias_ordenados]
        
        # Crear gráfico con matplotlib
        plt.figure(figsize=(10, 6))
        colores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
        bars = plt.bar(dias_labels, dias_valores, color=colores, edgecolor='black', linewidth=1.5)
        
        # Añadir valores encima de las barras
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.xlabel('Día de la Semana', fontsize=12, fontweight='bold')
        plt.ylabel('Número de Reservas', fontsize=12, fontweight='bold')
        plt.title('Reservas por Día de la Semana', fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        # Convertir a base64 para enviar al frontend
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'imagen': image_base64,
            'dias': dias_labels,
            'valores': dias_valores
        })
    except Exception as ex:
        print(f"Error en grafico_dias_semana: {ex}")
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

@app.route('/api/restaurantes/<id_restaurante>/analytics/grafico-precio-comparativo', methods=['GET'])
def grafico_precio_comparativo(id_restaurante):
    try:
        import numpy as np
        from scipy import stats
        
        cursor = conexion.connection.cursor()
        
        # Obtener el gasto medio por persona del restaurante actual
        sql_restaurante = """SELECT AVG(f.PRECIO / r.NUM_PERSONAS) as gasto_medio
                            FROM facturas f
                            JOIN reservas r ON f.ID_RESERVA = r.ID_RESERVA
                            WHERE f.ID_RESTAURANTE = %s"""
        cursor.execute(sql_restaurante, (id_restaurante,))
        resultado = cursor.fetchone()
        gasto_restaurante = float(resultado[0]) if resultado[0] else None
        
        # Obtener todos los gastos medios por persona de todos los restaurantes
        sql_todos = """SELECT r.ID_RESTAURANTE, AVG(f.PRECIO / res.NUM_PERSONAS) as gasto_medio
                      FROM facturas f
                      JOIN reservas res ON f.ID_RESERVA = res.ID_RESERVA
                      JOIN restaurantes r ON f.ID_RESTAURANTE = r.ID_RESTAURANTE
                      GROUP BY r.ID_RESTAURANTE
                      HAVING gasto_medio IS NOT NULL"""
        cursor.execute(sql_todos)
        datos_todos = cursor.fetchall()
        
        if len(datos_todos) < 2:
            return jsonify({'mensaje': 'No hay suficientes datos para generar el gráfico'}), 400
        
        # Extraer los valores de gasto medio
        gastos = [float(fila[1]) for fila in datos_todos]
        
        # Calcular media y desviación estándar
        media = np.mean(gastos)
        desviacion = np.std(gastos)
        
        # Crear rango de valores para la curva gaussiana
        x_min = max(0, media - 4*desviacion)
        x_max = media + 4*desviacion
        x = np.linspace(x_min, x_max, 1000)
        
        # Calcular la distribución normal
        y = stats.norm.pdf(x, media, desviacion)
        
        # Crear el gráfico
        plt.figure(figsize=(12, 7))
        
        # Dibujar la curva gaussiana
        plt.plot(x, y, 'b-', linewidth=2.5, label='Distribución de todos los restaurantes')
        plt.fill_between(x, y, alpha=0.3, color='lightblue')
        
        # Añadir línea vertical para el restaurante actual
        if gasto_restaurante:
            plt.axvline(x=gasto_restaurante, color='red', linestyle='--', linewidth=3, 
                       label=f'Este restaurante: {gasto_restaurante:.2f}€/persona')
            
            # Añadir texto con la posición del restaurante
            y_max = max(y)
            plt.text(gasto_restaurante, y_max * 0.9, f'{gasto_restaurante:.2f}€', 
                    ha='center', va='bottom', fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
        
        # Añadir línea para la media
        plt.axvline(x=media, color='green', linestyle=':', linewidth=2, 
                   label=f'Media del mercado: {media:.2f}€/persona')
        
        # Configurar el gráfico
        plt.xlabel('Precio por Persona (€)', fontsize=13, fontweight='bold')
        plt.ylabel('Densidad de Probabilidad', fontsize=13, fontweight='bold')
        plt.title('Comparativa de Precio por Persona con el Mercado', 
                 fontsize=15, fontweight='bold', pad=20)
        plt.legend(fontsize=11, loc='upper right')
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Añadir información estadística
        info_text = f'μ = {media:.2f}€\nσ = {desviacion:.2f}€\nN = {len(gastos)} restaurantes'
        plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Convertir a base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        # Calcular percentil del restaurante
        percentil = None
        if gasto_restaurante:
            percentil = stats.percentileofscore(gastos, gasto_restaurante)
        
        return jsonify({
            'imagen': image_base64,
            'gasto_restaurante': round(gasto_restaurante, 2) if gasto_restaurante else None,
            'media_mercado': round(media, 2),
            'desviacion': round(desviacion, 2),
            'percentil': round(percentil, 1) if percentil else None,
            'total_restaurantes': len(gastos)
        })
        
    except Exception as ex:
        print(f"Error en grafico_precio_comparativo: {ex}")
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error: {str(ex)}'}), 500

def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe...</h1>", 404

if __name__=="__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()