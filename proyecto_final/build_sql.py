#!/usr/bin/env python3
"""Build complete SQL file with all table data from CSVs"""

import csv

def escape_value(val):
    """Escape SQL value, handling NULL and quotes"""
    if val is None or val == '' or val.upper() == 'NULL':
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def process_csv(filepath, table_name):
    """Read CSV and generate INSERT statements"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        if not rows:
            return []
        
        cols = list(rows[0].keys())
        inserts = []
        
        for row in rows:
            values = [escape_value(row[col]) for col in cols]
            inserts.append(f"INSERT INTO `{table_name}` VALUES ({', '.join(values)});")
        
        return inserts

# Read existing SQL file
with open('api_flask_mysql.sql', 'r', encoding='utf-8') as f:
    base_sql = f.read()

# Generate inserts for all tables
tables_data = [
    ('proyecto_final_db/clientes.csv', 'clientes'),
    ('proyecto_final_db/restaurantes.csv', 'restaurantes'),
    ('proyecto_final_db/reservas.csv', 'reservas'),
    ('proyecto_final_db/facturas.csv', 'facturas'),
    ('proyecto_final_db/platos.csv', 'platos'),
    ('proyecto_final_db/resenas.csv', 'resenas')
]

sql_sections = [base_sql]

for csv_file, table_name in tables_data:
    print(f"Processing {table_name}...")
    inserts = process_csv(csv_file, table_name)
    
    sql_sections.append(f"\n--")
    sql_sections.append(f"-- Volcado de datos para la tabla `{table_name}` ({len(inserts)} registros)")
    sql_sections.append(f"--\n")
    sql_sections.extend(inserts)
    sql_sections.append("")

# Add indexes and constraints at the end
sql_sections.append("""
-- --------------------------------------------------------

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`ID_CLIENTE`);

--
-- Indices de la tabla `restaurantes`
--
ALTER TABLE `restaurantes`
  ADD PRIMARY KEY (`ID_RESTAURANTE`);

--
-- Indices de la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD PRIMARY KEY (`ID_RESERVA`),
  ADD KEY `FK_CLIENTE_RESERVA` (`ID_CLIENTE`),
  ADD KEY `FK_RESTAURANTE_RESERVA` (`ID_RESTAURANTE`);

--
-- Indices de la tabla `facturas`
--
ALTER TABLE `facturas`
  ADD PRIMARY KEY (`ID_FACTURA`),
  ADD KEY `FK_CLIENTE_FACTURA` (`ID_CLIENTE`),
  ADD KEY `FK_RESERVA_FACTURA` (`ID_RESERVA`),
  ADD KEY `FK_RESTAURANTE_FACTURA` (`ID_RESTAURANTE`);

--
-- Indices de la tabla `platos`
--
ALTER TABLE `platos`
  ADD KEY `FK_RESTAURANTE_PLATO` (`ID_RESTAURANTE`);

--
-- Indices de la tabla `resenas`
--
ALTER TABLE `resenas`
  ADD KEY `FK_RESTAURANTE_RESENA` (`ID_RESTAURANTE`),
  ADD KEY `FK_CLIENTE_RESENA` (`ID_CLIENTE`);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
""")

# Write complete SQL file
with open('api_flask_mysql.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_sections))

print("✓ SQL file generated successfully!")
print(f"Total tables: {len(tables_data)}")
