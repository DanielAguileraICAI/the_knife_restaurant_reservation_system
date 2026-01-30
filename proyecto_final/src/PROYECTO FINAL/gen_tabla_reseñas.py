import csv
import random
from datetime import datetime

# ===========================
#   CONFIGURACIÓN
# ===========================

PROB_RESEÑA = 0.65   # 65% de probabilidad de que una factura genere reseña

VALORACIONES = [i * 0.5 for i in range(0, 11)]   # 0, 0.5, ..., 5

TIPOS_VISITA = ["SOLO", "PAREJA", "GRUPO", "FAMILIA", "EMPRESA"]


# ===========================
#   CARGAR FACTURAS
# ===========================

facturas = []
with open("facturas.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Solo consideramos facturas asociadas a un restaurante
        facturas.append({
            "ID_FACTURA": row["ID_FACTURA"],
            "ID_CLIENTE": row["ID_CLIENTE"],
            "ID_RESTAURANTE": row["ID_RESTAURANTE"],
            "ID_RESERVA": row["ID_RESERVA"],
            "FECHA_FACTURA": row["FECHA_FACTURA"]
        })


# ===========================
#   GENERAR RESEÑAS
# ===========================

reseñas = []

for fac in facturas:
    # Se decide si hay reseña para esta factura:
    if random.random() <= PROB_RESEÑA:

        reseñas.append({
            "ID_RESTAURANTE": fac["ID_RESTAURANTE"],
            "ID_CLIENTE": fac["ID_CLIENTE"],
            "VALORACION": random.choice(VALORACIONES),
            "FECHA_VISITA": fac["FECHA_FACTURA"],
            "TIPO_VISITA": random.choice(TIPOS_VISITA)
        })


# ===========================
#   GUARDAR RESEÑAS EN CSV
# ===========================

with open("reseñas.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["ID_RESTAURANTE", "ID_CLIENTE", "VALORACION", "FECHA_VISITA", "TIPO_VISITA"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(reseñas)

print(f"Reseñas generadas correctamente. Total reseñas: {len(reseñas)}")
