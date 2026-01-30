import csv
import random
import string
from datetime import datetime, timedelta

# ===========================
#   FUNCIONES AUXILIARES
# ===========================

def generar_id_factura(fecha, existentes):
    """
    Genera un ID_FACTURA único con formato:
    Letra + Dígito + DDMMYY
    Ejemplo: G5121024
    """
    while True:
        letra = random.choice(string.ascii_uppercase)
        digito = str(random.randint(0, 9))
        fecha_str = fecha.strftime("%d%m%y")
        id_factura = f"{letra}{digito}{fecha_str}"
        if id_factura not in existentes:
            existentes.add(id_factura)
            return id_factura


def fecha_aleatoria(inicio, fin):
    """Genera una fecha aleatoria entre inicio y fin."""
    dias = (fin - inicio).days
    return inicio + timedelta(days=random.randint(0, dias))


# ===========================
#   CARGAR ARCHIVOS CSV
# ===========================

clientes = []
with open("clientes.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        clientes.append(row["ID_CLIENTE"])

reservas = []
with open("reservas.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        reservas.append({
            "ID_RESERVA": row["ID_RESERVA"],
            "ID_CLIENTE": row["ID_CLIENTE"],
            "FECHA_RESERVA": row["FECHA_RESERVA"],
            "ID_RESTAURANTE": row["ID_RESTAURANTE"]
        })

restaurantes = []
with open("restaurantes.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        restaurantes.append(row["ID_RESTAURANTE"])


# ===========================
#   GENERAR FACTURAS
# ===========================

facturas = []
id_facturas_existentes = set()

# --- Facturas que vienen de reservas (obligatorias) ---
for r in reservas:
    fecha = datetime.strptime(r["FECHA_RESERVA"], "%Y-%m-%d")
    id_factura = generar_id_factura(fecha, id_facturas_existentes)

    facturas.append({
        "ID_FACTURA": id_factura,
        "ID_CLIENTE": r["ID_CLIENTE"],
        "ID_RESERVA": r["ID_RESERVA"],
        "PRECIO": round(random.uniform(10, 300), 2),
        "FECHA_FACTURA": r["FECHA_RESERVA"],
        "ID_RESTAURANTE": r["ID_RESTAURANTE"]
    })

# --- Facturas sin reserva (opcional, aleatorias) ---

num_sin_reserva = max(20, len(clientes) // 5)   # Por ejemplo 20 o 20% de clientes
inicio_fecha = datetime(2015, 1, 1)
fin_fecha = datetime.now()

for _ in range(num_sin_reserva):
    cliente = random.choice(clientes)
    fecha = fecha_aleatoria(inicio_fecha, fin_fecha)
    id_factura = generar_id_factura(fecha, id_facturas_existentes)
    restaurante = random.choice(restaurantes)

    facturas.append({
        "ID_FACTURA": id_factura,
        "ID_CLIENTE": cliente,
        "ID_RESERVA": None,
        "PRECIO": round(random.uniform(10, 300), 2),
        "FECHA_FACTURA": fecha.strftime("%Y-%m-%d"),
        "ID_RESTAURANTE": restaurante
    })


# ===========================
#   ASEGURAR QUE TODOS LOS RESTAURANTES APARECEN AL MENOS UNA VEZ
# ===========================

restaurantes_facturados = {f["ID_RESTAURANTE"] for f in facturas}
faltan = [r for r in restaurantes if r not in restaurantes_facturados]

for r in faltan:
    cliente = random.choice(clientes)
    fecha = fecha_aleatoria(inicio_fecha, fin_fecha)
    id_factura = generar_id_factura(fecha, id_facturas_existentes)

    facturas.append({
        "ID_FACTURA": id_factura,
        "ID_CLIENTE": cliente,
        "ID_RESERVA": None,
        "PRECIO": round(random.uniform(10, 300), 2),
        "FECHA_FACTURA": fecha.strftime("%Y-%m-%d"),
        "ID_RESTAURANTE": r
    })


# ===========================
#   GUARDAR ARCHIVO CSV
# ===========================

with open("facturas.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["ID_FACTURA", "ID_CLIENTE", "ID_RESERVA", "PRECIO", "FECHA_FACTURA", "ID_RESTAURANTE"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(facturas)

print("Archivo facturas.csv generado correctamente.")
