# app.py
# Servicio API usando Flask para exponer el Crawler.

from flask import Flask, request, jsonify
import sys
import os
from typing import Dict, Any

# --- Configuración de Importación ---
# Agrega el directorio padre al sys.path si el archivo app.py no está al mismo nivel que main.py
# Si main.py está en el mismo directorio que app.py, esta línea solo asegura el path.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importamos la clase principal Crawler del módulo main.
try:
    # Importamos main y luego la clase Crawler
    import main
    crawler_instance = main.Crawler()
except ImportError as e:
    # Esto ocurre si falta main.py o sus dependencias (processor, fetcher, etc.)
    print(f"Error fatal: No se pudo importar la clase Crawler o sus dependencias. Asegúrate de que todos los módulos (processor, fetcher, main, etc.) estén accesibles y las librerías instaladas. Detalle: {e}")
    sys.exit(1)


app = Flask(__name__)

@app.route('/api/crawler', methods=['POST'])
def handle_crawler_request():
    """
    Endpoint: POST /api/crawler
    Procesa la consulta del usuario usando el Crawler.
    """
    # 1. Validar y obtener el prompt
    try:
        data: Dict[str, Any] = request.get_json()
    except Exception:
        return jsonify({"error": "Formato JSON inválido"}), 400

    prompt = data.get('prompt', '').strip()

    if not prompt:
        return jsonify({"error": "El campo 'prompt' es obligatorio en el cuerpo de la solicitud."}), 400

    # 2. Ejecutar el Crawler
    print(f"[POST] Recibida solicitud para prompt: '{prompt[:50]}...'")
    
    try:
        # La clase Crawler ya maneja todo el flujo de RAG (KB -> Web -> Consolidar)
        result: Dict[str, Any] = crawler_instance.run(prompt)
        
        # 3. Devolver la respuesta en formato JSON
        return jsonify(result), 200

    except Exception as e:
        # Manejo de errores durante el ciclo del crawler
        print(f"ERROR: Fallo durante la ejecución del crawler: {e}")
        return jsonify({
            "error": "Error interno del servidor al ejecutar el crawler",
            "details": str(e)
        }), 500


@app.route('/', methods=['GET'])
def home():
    """Endpoint de prueba simple."""
    return "Servicio Crawler API (RAG) corriendo. Usa POST en /api/crawler con un prompt."


if __name__ == '__main__':
    print("Iniciando Flask Server (http://127.0.0.1:5000)...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)