import csv
import random
import string
from faker import Faker

def generar_id_cliente(ids_existentes):
    """Genera un ID_CLIENTE único de 8 cifras + una letra."""
    while True:
        numero = random.randint(10000000, 99999999)
        letra = random.choice(string.ascii_uppercase)
        id_cliente = f"{numero}{letra}"
        if id_cliente not in ids_existentes:
            ids_existentes.add(id_cliente)
            return id_cliente

def generar_email(nombre, apellido):
    """Genera un email con una probabilidad del 80%, el resto será NULL."""
    if random.random() < 0.8:  # 80% de probabilidad de tener email
        nombre_limpio = nombre.lower().replace(" ", "")
        apellido_limpio = apellido.lower().replace(" ", "")
        dominio = random.choice(["gmail.com", "hotmail.com", "yahoo.es", "outlook.com"])
        return f"{nombre_limpio}.{apellido_limpio}@{dominio}"
    else:
        return None

def generar_clientes(num_clientes, archivo_salida):
    fake = Faker("es_ES")
    ids_existentes = set()
    estudios_posibles = ["ESTUDIANTE", "TRABAJADOR", "JUBILADO", "NC"]

    with open(archivo_salida, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID_CLIENTE", "NOMBRE", "NUM_TELEFONO", "EMAIL", "ESTUDIOS", "SEXO", "EDAD"])

        for _ in range(num_clientes):
            id_cliente = generar_id_cliente(ids_existentes)
            nombre = fake.first_name().upper()
            apellido = fake.last_name().upper()
            nombre_completo = f"{apellido}, {nombre}"
            telefono = f"6{random.randint(10000000, 99999999)}"
            email = generar_email(nombre, apellido)
            estudios = random.choice(estudios_posibles)
            sexo = random.choices(population=["M", "F", "O"],weights=[47, 47, 6],k=1)[0]
            edad = random.randint(16, 95)

            writer.writerow([id_cliente, nombre_completo, telefono, email if email else "NULL", estudios, sexo, edad])

    print(f"✅ Archivo '{archivo_salida}' generado con {num_clientes} clientes.")

if __name__ == "__main__":
    generar_clientes(num_clientes=100, archivo_salida="clientes.csv")