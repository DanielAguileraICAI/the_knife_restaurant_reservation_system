#!/usr/bin/env python3
"""
Build complete SQL file with all CSV data for The Knife Database
Usage: python3 build_sql.py
"""

import csv
import os

def escape_value(val):
    """Escape SQL value, handling NULL and quotes"""
    if val is None or val == '' or val.upper() == 'NULL':
        return 'NULL'
    return "'" + str(val).replace("'", "''") + "'"

def process_csv(filepath, table_name):
    """Read CSV and generate INSERT statements"""
    if not os.path.exists(filepath):
        print(f"⚠️  Warning: {filepath} not found!")
        return []
    
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

# Base SQL with table structures
base_sql = """-- phpMyAdmin SQL Dump
-- The Knife Restaurant Reservation System
-- Generado: 18-11-2025

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `the_knife`
--

CREATE DATABASE IF NOT EXISTS `the_knife` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE `the_knife`;

-- --------------------------------------------------------

CREATE TABLE `clientes` (
  `ID_CLIENTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `NOMBRE` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `NUM_TELEFONO` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  `EMAIL` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `ESTUDIOS` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `SEXO` char(1) COLLATE utf8_unicode_ci DEFAULT NULL,
  `EDAD` int(3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `restaurantes` (
  `ID_RESTAURANTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `NOMBRE` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `CIUDAD` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `CCAA` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `TIPO_COMIDA` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `PRESUPUESTO` int(1) DEFAULT NULL,
  `ESTRELLA_MICH` int(1) DEFAULT NULL,
  `CADENA` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `reservas` (
  `ID_RESERVA` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `ID_CLIENTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `NUM_PERSONAS` int(2) DEFAULT NULL,
  `FECHA_RESERVA` date DEFAULT NULL,
  `HORA_RESERVA` time DEFAULT NULL,
  `ID_RESTAURANTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `ESTADO_RESERVA` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `facturas` (
  `ID_FACTURA` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `ID_CLIENTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `ID_RESERVA` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `PRECIO` decimal(10,2) DEFAULT NULL,
  `FECHA_FACTURA` date DEFAULT NULL,
  `ID_RESTAURANTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `platos` (
  `ID_RESTAURANTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `N_PLATO` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `T_PLATO` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `PRECIO` decimal(10,2) DEFAULT NULL,
  `ALERGENOS` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `resenas` (
  `ID_RESTAURANTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `ID_CLIENTE` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `VALORACION` decimal(2,1) DEFAULT NULL,
  `FECHA_VISITA` date DEFAULT NULL,
  `TIPO_VISITA` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------
"""

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

print("🔧 Building SQL file for The Knife database...\n")

for csv_file, table_name in tables_data:
    print(f"📊 Processing {table_name}...", end=" ")
    inserts = process_csv(csv_file, table_name)
    
    sql_sections.append(f"\n--")
    sql_sections.append(f"-- Volcado de datos: `{table_name}` ({len(inserts)} registros)")
    sql_sections.append(f"--\n")
    sql_sections.extend(inserts)
    sql_sections.append("")
    print(f"✅ {len(inserts)} rows")

# Add indexes and constraints
sql_sections.append("""
-- --------------------------------------------------------
-- Índices y restricciones
-- --------------------------------------------------------

ALTER TABLE `clientes`
  ADD PRIMARY KEY (`ID_CLIENTE`);

ALTER TABLE `restaurantes`
  ADD PRIMARY KEY (`ID_RESTAURANTE`);

ALTER TABLE `reservas`
  ADD PRIMARY KEY (`ID_RESERVA`),
  ADD KEY `FK_CLIENTE_RESERVA` (`ID_CLIENTE`),
  ADD KEY `FK_RESTAURANTE_RESERVA` (`ID_RESTAURANTE`);

ALTER TABLE `facturas`
  ADD PRIMARY KEY (`ID_FACTURA`),
  ADD KEY `FK_CLIENTE_FACTURA` (`ID_CLIENTE`),
  ADD KEY `FK_RESERVA_FACTURA` (`ID_RESERVA`),
  ADD KEY `FK_RESTAURANTE_FACTURA` (`ID_RESTAURANTE`);

ALTER TABLE `platos`
  ADD KEY `FK_RESTAURANTE_PLATO` (`ID_RESTAURANTE`);

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

print("\n✅ SQL file generated successfully!")
print(f"📁 Output: api_flask_mysql.sql")
print(f"🗄️  Database: the_knife")
print(f"📊 Total tables: {len(tables_data)}")
print(f"\n💡 To import:")
print(f"   mysql -u root -p < api_flask_mysql.sql")
