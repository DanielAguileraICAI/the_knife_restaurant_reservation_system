#!/usr/bin/env python3
"""
Script to generate complete SQL file for proyecto_final_db database
Reads all CSV files and generates CREATE TABLE and INSERT statements
"""

import csv
import os

def escape_sql_string(value):
    """Escape single quotes and handle NULL values"""
    if value is None or value == '' or value.upper() == 'NULL':
        return 'NULL'
    # Replace single quotes with two single quotes for SQL
    return f"'{str(value).replace(chr(39), chr(39)+chr(39))}'"

def read_csv_data(filepath):
    """Read CSV file and return headers and rows"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows

def generate_sql():
    """Generate complete SQL file"""
    
    sql_output = []
    
    # Database creation
    sql_output.append("-- Create database")
    sql_output.append("CREATE DATABASE IF NOT EXISTS proyecto_final_db;")
    sql_output.append("USE proyecto_final_db;")
    sql_output.append("")
    sql_output.append("-- Drop existing tables")
    sql_output.append("DROP TABLE IF EXISTS facturas;")
    sql_output.append("DROP TABLE IF EXISTS resenas;")
    sql_output.append("DROP TABLE IF EXISTS reservas;")
    sql_output.append("DROP TABLE IF EXISTS platos;")
    sql_output.append("DROP TABLE IF EXISTS clientes;")
    sql_output.append("DROP TABLE IF EXISTS restaurantes;")
    sql_output.append("")
    
    # Create tables
    sql_output.append("-- Create tables")
    sql_output.append("""
CREATE TABLE restaurantes (
    ID_RESTAURANTE CHAR(7) NOT NULL,
    NOMBRE VARCHAR(50) NOT NULL,
    CIUDAD VARCHAR(30) NOT NULL,
    CCAA VARCHAR(30) NOT NULL,
    TIPO_COMIDA VARCHAR(30) NOT NULL,
    PRESUPUESTO INTEGER NOT NULL,
    ESTRELLA_MICH INTEGER NOT NULL,
    CADENA VARCHAR(30) NULL,
    CONSTRAINT PKRT PRIMARY KEY (ID_RESTAURANTE)
);
""")
    
    sql_output.append("""
CREATE TABLE clientes (
    ID_CLIENTE CHAR(9) NOT NULL,
    NOMBRE VARCHAR(50) NOT NULL,
    NUM_TELEFONO BIGINT NOT NULL,
    EMAIL VARCHAR(50) NULL,
    ESTUDIOS VARCHAR(30) NOT NULL,
    SEXO CHAR(1) NOT NULL,
    EDAD INTEGER NOT NULL,
    CONSTRAINT PKC PRIMARY KEY (ID_CLIENTE)
);
""")
    
    sql_output.append("""
CREATE TABLE platos (
    ID_RESTAURANTE CHAR(7) NOT NULL,
    NOMBRE_PLATO VARCHAR(50) NOT NULL,
    TIPO_PLATO VARCHAR(30) NOT NULL,
    PRECIO DECIMAL(6,2) NOT NULL,
    CONSTRAINT PKP PRIMARY KEY (ID_RESTAURANTE, NOMBRE_PLATO),
    CONSTRAINT FKP FOREIGN KEY (ID_RESTAURANTE) REFERENCES restaurantes(ID_RESTAURANTE) ON DELETE RESTRICT
);
""")
    
    sql_output.append("""
CREATE TABLE reservas (
    ID_RESERVA CHAR(8) NOT NULL,
    ID_CLIENTE CHAR(9) NOT NULL,
    NUM_PERSONAS INTEGER NOT NULL,
    FECHA_RESERVA DATE NOT NULL,
    HORA_RESERVA TIME NOT NULL,
    ID_RESTAURANTE CHAR(7) NOT NULL,
    ESTADO_RESERVA VARCHAR(20) NOT NULL,
    CONSTRAINT PKRV PRIMARY KEY (ID_RESTAURANTE, ID_RESERVA),
    CONSTRAINT UNIQUE_RESERVA UNIQUE (ID_RESERVA),
    CONSTRAINT FKRV1 FOREIGN KEY (ID_RESTAURANTE) REFERENCES restaurantes(ID_RESTAURANTE) ON DELETE RESTRICT,
    CONSTRAINT FKRV2 FOREIGN KEY (ID_CLIENTE) REFERENCES clientes(ID_CLIENTE) ON DELETE RESTRICT
);
""")
    
    sql_output.append("""
CREATE TABLE resenas (
    ID_RESTAURANTE CHAR(7) NOT NULL,
    ID_CLIENTE CHAR(9) NOT NULL,
    VALORACION DECIMAL(2,1) NOT NULL,
    FECHA_VISITA DATE NOT NULL,
    TIPO_VISITA VARCHAR(30) NOT NULL,
    CONSTRAINT PKRN PRIMARY KEY (ID_RESTAURANTE, ID_CLIENTE),
    CONSTRAINT FKRN1 FOREIGN KEY (ID_RESTAURANTE) REFERENCES restaurantes(ID_RESTAURANTE) ON DELETE RESTRICT,
    CONSTRAINT FKRN2 FOREIGN KEY (ID_CLIENTE) REFERENCES clientes(ID_CLIENTE) ON DELETE RESTRICT
);
""")
    
    sql_output.append("""
CREATE TABLE facturas (
    ID_FACTURA CHAR(8) NOT NULL,
    ID_CLIENTE CHAR(9) NOT NULL,
    ID_RESERVA CHAR(8) NULL,
    PRECIO DECIMAL(6,2) NOT NULL,
    FECHA_FACTURA DATE NOT NULL,
    ID_RESTAURANTE CHAR(7) NOT NULL,
    CONSTRAINT PKF PRIMARY KEY (ID_RESTAURANTE, ID_FACTURA),
    CONSTRAINT UNIQUE_FACTURA UNIQUE (ID_FACTURA),
    CONSTRAINT FKF1 FOREIGN KEY (ID_CLIENTE) REFERENCES clientes(ID_CLIENTE) ON DELETE RESTRICT,
    CONSTRAINT FKF2 FOREIGN KEY (ID_RESERVA) REFERENCES reservas(ID_RESERVA) ON DELETE RESTRICT,
    CONSTRAINT FKF3 FOREIGN KEY (ID_RESTAURANTE) REFERENCES restaurantes(ID_RESTAURANTE) ON DELETE RESTRICT
);
""")
    
    # Insert data from CSVs
    csv_files = {
        'restaurantes': 'proyecto_final_db/restaurantes.csv',
        'clientes': 'proyecto_final_db/clientes.csv',
        'platos': 'proyecto_final_db/platos.csv',
        'reservas': 'proyecto_final_db/reservas.csv',
        'resenas': 'proyecto_final_db/resenas.csv',
        'facturas': 'proyecto_final_db/facturas.csv'
    }
    
    for table_name, csv_file in csv_files.items():
        if not os.path.exists(csv_file):
            print(f"Warning: {csv_file} not found, skipping...")
            continue
            
        headers, rows = read_csv_data(csv_file)
        
        sql_output.append(f"\n-- Insert data into {table_name}")
        sql_output.append(f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES")
        
        insert_values = []
        for row in rows:
            values = [escape_sql_string(val) for val in row]
            insert_values.append(f"({', '.join(values)})")
        
        # Split into chunks of 100 rows to avoid too long statements
        chunk_size = 100
        for i in range(0, len(insert_values), chunk_size):
            chunk = insert_values[i:i+chunk_size]
            if i > 0:
                sql_output.append(f"\nINSERT INTO {table_name} ({', '.join(headers)}) VALUES")
            sql_output.append(',\n'.join(chunk) + ';')
        
        sql_output.append("")
    
    return '\n'.join(sql_output)

if __name__ == '__main__':
    print("Generating SQL file...")
    sql_content = generate_sql()
    
    output_file = 'api_flask_mysql_prueba.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"✓ SQL file generated: {output_file}")
    print(f"✓ File size: {len(sql_content)} bytes")
