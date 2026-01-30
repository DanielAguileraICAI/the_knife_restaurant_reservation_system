import csv
import random
from datetime import datetime, timedelta

# === CONFIGURACIÓN ===
ARCHIVO_CLIENTES = "clientes.csv"
ARCHIVO_RESTAURANTES = "restaurantes.csv"
ARCHIVO_SALIDA = "reservas.csv"

MIN_RESERVAS_POR_CLIENTE = 0
MAX_RESERVAS_POR_CLIENTE = 5

# === FUNCIONES ===
def cargar_columna_csv(archivo, columna):
    """Carga una columna específica de un CSV en una lista."""
    with open(archivo, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row[columna] for row in reader if row[columna] and row[columna] != "NULL"]

def generar_fecha_reserva():
    """Genera una fecha aleatoria entre 2015 y hoy."""
    inicio = datetime(2015, 1, 1)
    fin = datetime.now()
    dias = (fin - inicio).days
    fecha = inicio + timedelta(days=random.randint(0, dias))
    return fecha

def generar_hora_reserva():
    """Genera una hora realista de reserva (almuerzo o cena)."""
    hora = random.choice([12, 13, 14, 19, 20, 21])
    minutos = random.choice([0, 15, 30, 45])
    return f"{hora:02d}:{minutos:02d}"

def generar_id_reserva(fecha, usados):
    """Genera un ID_RESERVA único con formato YYMMDD + Letra + Dígito."""
    while True:
        codigo = f"{fecha.strftime('%y%m%d')}{random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')}{random.randint(0,9)}"
        if codigo not in usados:
            usados.add(codigo)
            return codigo

# === CARGA DE DATOS ===
clientes = cargar_columna_csv(ARCHIVO_CLIENTES, "ID_CLIENTE")
restaurantes = cargar_columna_csv(ARCHIVO_RESTAURANTES, "ID_RESTAURANTE")

print(f"Clientes cargados: {len(clientes)}")
print(f"Restaurantes cargados: {len(restaurantes)}")

# === GENERACIÓN DE RESERVAS ===
reservas = []
id_usados = set()

for cliente in clientes:
    # Cada cliente tendrá entre 1 y 5 reservas
    n_reservas = random.randint(MIN_RESERVAS_POR_CLIENTE, MAX_RESERVAS_POR_CLIENTE)
    
    for _ in range(n_reservas):
        fecha = generar_fecha_reserva()
        id_reserva = generar_id_reserva(fecha, id_usados)
        id_restaurante = random.choice(restaurantes)  # <-- garantiza relación con restaurantes.csv
        num_personas = random.randint(1, 8)
        hora = generar_hora_reserva()
        estado = "CONFIRMADA" if random.random() < 0.9 else "CANCELADA"
        
        reservas.append({
            "ID_RESERVA": id_reserva,
            "ID_CLIENTE": cliente,
            "NUM_PERSONAS": num_personas,
            "FECHA_RESERVA": fecha.strftime("%Y-%m-%d"),
            "HORA_RESERVA": hora,
            "ID_RESTAURANTE": id_restaurante,
            "ESTADO_RESERVA": estado
        })

# === GUARDAR RESULTADOS ===
with open(ARCHIVO_SALIDA, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "ID_RESERVA", "ID_CLIENTE", "NUM_PERSONAS",
        "FECHA_RESERVA", "HORA_RESERVA",
        "ID_RESTAURANTE", "ESTADO_RESERVA"
    ])
    writer.writeheader()
    writer.writerows(reservas)

print(f"✅ Archivo '{ARCHIVO_SALIDA}' generado con {len(reservas)} reservas únicas.")
