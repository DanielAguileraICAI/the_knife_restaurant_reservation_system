"""
Test Flask app to verify database connection
"""
from flask import Flask, jsonify
from flask_mysqldb import MySQL
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

try:
    conexion = MySQL(app)
    print("✓ MySQL extension initialized")
except Exception as e:
    print(f"✗ Error initializing MySQL: {e}")
    sys.exit(1)

@app.route('/test')
def test_connection():
    try:
        cursor = conexion.connection.cursor()
        
        # Test restaurantes
        cursor.execute("SELECT COUNT(*) FROM restaurantes")
        count_rest = cursor.fetchone()[0]
        
        # Test platos
        cursor.execute("SELECT COUNT(*) FROM platos")
        count_platos = cursor.fetchone()[0]
        
        # Get sample restaurants
        cursor.execute("SELECT NOMBRE, CIUDAD, ESTRELLA_MICH FROM restaurantes LIMIT 5")
        restaurants = cursor.fetchall()
        
        cursor.close()
        
        return jsonify({
            'status': 'success',
            'restaurantes_count': count_rest,
            'platos_count': count_platos,
            'sample_restaurants': [
                {'nombre': r[0], 'ciudad': r[1], 'estrellas': r[2]} 
                for r in restaurants
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Testing Database Connection")
    print("="*50)
    print(f"Host: {app.config['MYSQL_HOST']}")
    print(f"User: {app.config['MYSQL_USER']}")
    print(f"DB: {app.config['MYSQL_DB']}")
    print("="*50)
    print("\nStarting test server on http://localhost:5001/test")
    print("Press Ctrl+C to stop\n")
    
    app.run(port=5001, debug=True)
