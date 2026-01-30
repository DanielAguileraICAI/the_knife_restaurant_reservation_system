import sqlite3
import csv

# Create SQLite database
conn = sqlite3.connect('restaurantes.db')
cursor = conn.cursor()

# Create restaurantes table
cursor.execute('''
CREATE TABLE IF NOT EXISTS restaurantes (
    ID_RESTAURANTE TEXT PRIMARY KEY,
    NOMBRE TEXT NOT NULL,
    CIUDAD TEXT NOT NULL,
    CCAA TEXT NOT NULL,
    TIPO_COMIDA TEXT NOT NULL,
    PRESUPUESTO INTEGER NOT NULL,
    ESTRELLA_MICH INTEGER NOT NULL,
    CADENA TEXT
)
''')

# Read and insert data from CSV
with open('proyecto_final_db/restaurantes.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        # Convert NULL string to None
        cadena = None if row['CADENA'] == 'NULL' else row['CADENA']
        
        cursor.execute('''
            INSERT OR REPLACE INTO restaurantes 
            (ID_RESTAURANTE, NOMBRE, CIUDAD, CCAA, TIPO_COMIDA, PRESUPUESTO, ESTRELLA_MICH, CADENA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['ID_RESTAURANTE'],
            row['NOMBRE'],
            row['CIUDAD'],
            row['CCAA'],
            row['TIPO_COMIDA'],
            int(row['PRESUPUESTO']),
            int(row['ESTRELLA_MICH']),
            cadena
        ))

# Commit and close
conn.commit()
print(f"✓ Database created with {cursor.execute('SELECT COUNT(*) FROM restaurantes').fetchone()[0]} restaurants")
conn.close()
print("✓ restaurantes.db created successfully!")
