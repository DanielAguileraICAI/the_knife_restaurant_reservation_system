#!/usr/bin/env python3
"""Generate SQL INSERT statements from CSV files"""

import csv
import sys

def escape_sql_value(value):
    """Escape single quotes and handle NULL values"""
    if value is None or value == '' or value.upper() == 'NULL':
        return 'NULL'
    # Escape single quotes
    value = str(value).replace("'", "''")
    return f"'{value}'"

def generate_inserts_from_csv(csv_file, table_name):
    """Generate INSERT statements from CSV file"""
    inserts = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        for row in reader:
            values = [escape_sql_value(row[col]) for col in headers]
            values_str = ', '.join(values)
            columns_str = ', '.join([f'`{col}`' for col in headers])
            insert = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values_str});"
            inserts.append(insert)
    
    return inserts

# Process each CSV file
tables = [
    ('proyecto_final_db/clientes.csv', 'clientes'),
    ('proyecto_final_db/restaurantes.csv', 'restaurantes'),
    ('proyecto_final_db/reservas.csv', 'reservas'),
    ('proyecto_final_db/facturas.csv', 'facturas'),
    ('proyecto_final_db/platos.csv', 'platos'),
    ('proyecto_final_db/resenas.csv', 'resenas')
]

all_sql = []

for csv_file, table_name in tables:
    print(f"Processing {csv_file}...", file=sys.stderr)
    inserts = generate_inserts_from_csv(csv_file, table_name)
    all_sql.append(f"\n--\n-- Volcado de datos para la tabla `{table_name}` ({len(inserts)} registros)\n--\n")
    all_sql.extend(inserts)
    all_sql.append("\n")

# Print to stdout
print('\n'.join(all_sql))
