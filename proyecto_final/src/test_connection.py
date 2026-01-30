"""
Script to test MySQL database connection
"""
try:
    import MySQLdb
except ImportError:
    print("Instalando mysqlclient...")
    import subprocess
    subprocess.run(["pip", "install", "mysqlclient"])
    import MySQLdb

try:
    print("Intentando conectar a la base de datos...")
    connection = MySQLdb.connect(
        host='localhost',
        user='root',
        password='root',
        database='theknife_db'
    )
    print("✓ Conexión exitosa a theknife_db!")
    
    cursor = connection.cursor()
    
    # Test 1: Count restaurantes
    cursor.execute("SELECT COUNT(*) FROM restaurantes")
    count = cursor.fetchone()[0]
    print(f"✓ Número de restaurantes en la BD: {count}")
    
    # Test 2: Get first 5 restaurants
    cursor.execute("SELECT NOMBRE, CIUDAD, ESTRELLA_MICH FROM restaurantes LIMIT 5")
    print("\n✓ Primeros 5 restaurantes:")
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}) - {row[2]} estrellas")
    
    # Test 3: Count platos
    cursor.execute("SELECT COUNT(*) FROM platos")
    count_platos = cursor.fetchone()[0]
    print(f"\n✓ Número de platos en la BD: {count_platos}")
    
    cursor.close()
    connection.close()
    print("\n✓ Todo funciona correctamente!")
    
except MySQLdb.Error as e:
    print(f"✗ Error de conexión: {e}")
    print("\nVerifica:")
    print("1. MySQL está ejecutándose")
    print("2. La contraseña de root es 'root'")
    print("3. La base de datos 'theknife_db' existe")
    print("\nPara crear la BD ejecuta:")
    print("   mysql -u root -p < api_flask_mysql_prueba.sql")
