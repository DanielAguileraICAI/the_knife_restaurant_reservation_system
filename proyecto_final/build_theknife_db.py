#!/usr/bin/env python3
"""
Build complete theknife_db SQL file with all CSV data
"""

import csv
import os

def escape_value(val, is_numeric=False):
    """Escape SQL value, handling NULL and quotes"""
    if val is None or val == '' or val.upper() == 'NULL':
        return 'NULL'
    if is_numeric:
        return str(val)
    return "'" + str(val).replace("'", "''") + "'"

def read_clientes_csv():
    """Read clientes.csv and return formatted INSERT values"""
    values = []
    with open('proyecto_final_db/clientes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id_cliente = escape_value(row['ID_CLIENTE'])
            nombre = escape_value(row['N_CLIENTE'])
            telefono = escape_value(row['NUM_TELEFONO'], is_numeric=True)
            email = escape_value(row['EMAIL'])
            estudios = escape_value(row['ESTUDIOS'])
            sexo = escape_value(row['SEXO'])
            edad = escape_value(row['EDAD'], is_numeric=True)
            values.append(f"({id_cliente}, {nombre}, {telefono}, {email}, {estudios}, {sexo}, {edad})")
    return values

def read_platos_csv():
    """Read platos.csv and return formatted INSERT values"""
    values = []
    with open('proyecto_final_db/platos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id_rest = escape_value(row['ID_RESTAURANTE'])
            nombre = escape_value(row['N_PLATO'])
            tipo = escape_value(row['T_PLATO'])
            precio = escape_value(row['PRECIO'], is_numeric=True)
            values.append(f"({id_rest}, {nombre}, {tipo}, {precio})")
    return values

def read_reservas_csv():
    """Read reservas.csv and return formatted INSERT values"""
    values = []
    with open('proyecto_final_db/reservas.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id_reserva = escape_value(row['ID_RESERVA'])
            id_cliente = escape_value(row['ID_CLIENTE'])
            num_personas = escape_value(row['NUM_PERSONAS'], is_numeric=True)
            fecha = escape_value(row['FECHA_RESERVA'])
            hora = escape_value(row['HORA_RESERVA'])
            id_rest = escape_value(row['ID_RESTAURANTE'])
            estado = escape_value(row['ESTADO_RESERVA'])
            values.append(f"({id_reserva}, {id_cliente}, {num_personas}, {fecha}, {hora}, {id_rest}, {estado})")
    return values

def read_facturas_csv():
    """Read facturas2.csv and return formatted INSERT values"""
    values = []
    csv_path = 'src/PROYECTO FINAL/facturas2.csv'
    if not os.path.exists(csv_path):
        csv_path = 'proyecto_final_db/facturas.csv'
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Generate factura ID from reserva ID
            id_factura = escape_value('F' + row['ID_RESERVA'][1:])
            id_cliente = escape_value(row['ID_CLIENTE'])
            id_reserva = escape_value(row['ID_RESERVA'])
            precio = escape_value(row['PRECIO_TOTAL'], is_numeric=True)
            valoracion = escape_value(row.get('VALORACION', 'NULL'), is_numeric=True)
            tipo_visita = escape_value(row.get('TIPO_VISITA', 'NULL'))
            fecha = escape_value(row['FECHA_FACTURA'])
            id_rest = escape_value(row['ID_RESTAURANTE'])
            values.append(f"({id_factura}, {id_cliente}, {id_reserva}, {precio}, {valoracion}, {tipo_visita}, {fecha}, {id_rest})")
    return values

def read_resenas_csv():
    """Read reseñas.csv and return formatted INSERT values for facturas table"""
    # Note: resenas data goes into facturas table as valoracion
    return []

print("🔧 Building theknife_db SQL file with all CSV data...\n")

print("📊 Reading clientes.csv...", end=" ")
clientes_values = read_clientes_csv()
print(f"✅ {len(clientes_values)} rows")

print("📊 Reading platos.csv...", end=" ")
platos_values = read_platos_csv()
print(f"✅ {len(platos_values)} rows")

print("📊 Reading reservas.csv...", end=" ")
reservas_values = read_reservas_csv()
print(f"✅ {len(reservas_values)} rows")

print("📊 Reading facturas.csv...", end=" ")
facturas_values = read_facturas_csv()
print(f"✅ {len(facturas_values)} rows")

# Read the base SQL structure
with open('api_flask_mysql_prueba.sql', 'r', encoding='utf-8') as f:
    base_content = f.read()

# Find where to insert the data
# Replace the CLIENTES insert section
clientes_insert = "INSERT INTO CLIENTES (ID_CLIENTE, N_CLIENTE, NUM_TELEFONO, EMAIL, ESTUDIOS, SEXO, EDAD) VALUES\n"
clientes_insert += ',\n'.join(clientes_values) + ';\n'

print(f"\n📝 Generated CLIENTES INSERT with {len(clientes_values)} records")
print(f"📝 Generated PLATOS INSERT with {len(platos_values)} records")
print(f"📝 Generated RESERVAS INSERT with {len(reservas_values)} records")
print(f"📝 Generated FACTURAS INSERT with {len(facturas_values)} records")

# Write the inserts to a temporary file for review
with open('csv_data_inserts.sql', 'w', encoding='utf-8') as f:
    f.write("-- CLIENTES DATA FROM CSV\n")
    f.write(clientes_insert + "\n\n")
    
    f.write("-- PLATOS DATA FROM CSV\n")
    f.write("INSERT INTO PLATOS (ID_RESTAURANTE, N_PLATO, T_PLATO, PRECIO) VALUES\n")
    f.write(',\n'.join(platos_values) + ';\n\n\n')
    
    f.write("-- RESERVAS DATA FROM CSV\n")
    f.write("INSERT INTO RESERVAS (ID_RESERVA, ID_CLIENTE, NUM_PERSONAS, FECHA_RESERVA, HORA_RESERVA, ID_RESTAURANTE, ESTADO_RESERVA) VALUES\n")
    f.write(',\n'.join(reservas_values) + ';\n\n\n')
    
    f.write("-- FACTURAS DATA FROM CSV\n")
    f.write("INSERT INTO FACTURAS (ID_FACTURA, ID_CLIENTE, ID_RESERVA, PRECIO, VALORACION, TIPO_VISITA, FECHA_FACTURA, ID_RESTAURANTE) VALUES\n")
    f.write(',\n'.join(facturas_values) + ';\n\n\n')

print(f"\n✅ SQL inserts generated successfully!")
print(f"📁 Output: csv_data_inserts.sql")
print(f"\n💡 Review the file and integrate into api_flask_mysql_prueba.sql")
