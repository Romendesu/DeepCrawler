"""API Flask mejorada con IA generativa y aprendizaje."""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from typing import Dict, Any
import traceback
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar Crawler mejorado
try:
    from core_enhanced import EnhancedCrawler
    
    use_cache = os.getenv('USE_CACHE', 'true').lower() == 'true'
    use_ai = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
    
    crawler_instance = EnhancedCrawler(use_cache=use_cache, use_ai=bool(use_ai))
    print("✓ Crawler mejorado inicializado")
    print(f"  - Caché: {'Activado' if use_cache else 'Desactivado'}")
    print(f"  - IA: {crawler_instance.ai_provider.provider if use_ai else 'Desactivada'}")
    initialization_error = None
    
except ImportError as e:
    print(f"✗ Error al importar: {e}", file=sys.stderr)
    crawler_instance = None
    initialization_error = f"ERROR DE IMPORTACIÓN: {e}"
except Exception as e:
    print(f"✗ Error durante inicialización: {e}", file=sys.stderr)
    crawler_instance = None
    initialization_error = f"ERROR DE INICIALIZACIÓN: {e}"

# Crear app Flask
app = Flask(__name__)
CORS(app)


@app.route('/api/crawler', methods=['POST'])
def handle_crawler_request():
    """
    Endpoint principal: POST /api/crawler
    
    Body: {
        "prompt": "tu consulta aquí"
    }
    
    Response: {
        "prompt": "...",
        "response": {
            "query": "...",
            "intent": "...",
            "response_text": "...",
            "confidence": 0.85,
            "sources": [...],
            "keywords": [...],
            "ai_provider": "claude|openai|fallback",
            "learning_stats": {...}
        }
    }
    """
    
    if initialization_error:
        return jsonify({
            "error": "El servicio no se inicializó correctamente",
            "details": initialization_error
        }), 500
    
    if not crawler_instance:
        return jsonify({
            "error": "El servicio Crawler no está disponible"
        }), 500
    
    # Validar request
    try:
        data: Dict[str, Any] = request.get_json()
    except Exception:
        return jsonify({
            "error": "Formato JSON inválido"
        }), 400
    
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({
            "error": "El campo 'prompt' es obligatorio"
        }), 400
    
    # Ejecutar Crawler
    print(f"[→] Procesando: '{prompt[:60]}...'")
    
    try:
        result: Dict[str, Any] = crawler_instance.run(prompt)
        print(f"[✓] Respuesta generada exitosamente")
        print(f"    - IA: {result['response'].get('ai_provider', 'N/A')}")
        print(f"    - Confidence: {result['response'].get('confidence', 0):.2%}")
        return jsonify(result), 200
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[✗] Error durante ejecución:\n{error_trace}", file=sys.stderr)
        
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e),
            "type": type(e).__name__
        }), 500


@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    """
    Endpoint de feedback: POST /api/feedback
    
    Body: {
        "prompt": "consulta original",
        "response": {...},  # respuesta completa
        "useful": true/false
    }
    
    Response: {
        "status": "success",
        "message": "Feedback registrado",
        "learning_stats": {...}
    }
    """
    
    if not crawler_instance:
        return jsonify({
            "error": "El servicio Crawler no está disponible"
        }), 500
    
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "error": "Formato JSON inválido"
        }), 400
    
    prompt = data.get('prompt', '').strip()
    response = data.get('response', {})
    useful = data.get('useful', False)
    
    if not prompt or not response:
        return jsonify({
            "error": "Los campos 'prompt' y 'response' son obligatorios"
        }), 400
    
    try:
        # Registrar feedback
        crawler_instance.add_feedback(prompt, response, useful)
        
        # Obtener estadísticas actualizadas
        stats = crawler_instance.learning.get_learning_stats()
        
        print(f"[✓] Feedback registrado: {'Positivo' if useful else 'Negativo'}")
        print(f"    - Total feedback: {stats['total_feedback']}")
        print(f"    - Feedback positivo: {stats['positive_feedback']}")
        print(f"    - Temas aprendidos: {stats['learned_topics']}")
        
        return jsonify({
            "status": "success",
            "message": "Feedback registrado correctamente",
            "learning_stats": stats
        }), 200
    
    except Exception as e:
        print(f"[✗] Error al registrar feedback: {e}", file=sys.stderr)
        return jsonify({
            "error": "Error al registrar feedback",
            "details": str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Endpoint de estadísticas: GET /api/stats
    
    Response: {
        "learning_stats": {
            "total_feedback": 100,
            "positive_feedback": 75,
            "learned_topics": 25,
            "learned_facts": 120
        },
        "system_info": {
            "ai_provider": "claude",
            "cache_enabled": true,
            "version": "3.0.0"
        }
    }
    """
    
    if not crawler_instance:
        return jsonify({
            "error": "El servicio Crawler no está disponible"
        }), 500
    
    try:
        stats = crawler_instance.learning.get_learning_stats()
        
        system_info = {
            "ai_provider": crawler_instance.ai_provider.provider if crawler_instance.ai_provider else None,
            "cache_enabled": crawler_instance.fetcher.cache is not None,
            "version": "3.0.0"
        }
        
        return jsonify({
            "learning_stats": stats,
            "system_info": system_info
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Error al obtener estadísticas",
            "details": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check."""
    status = "healthy" if crawler_instance else "unhealthy"
    
    response = {
        "status": status,
        "service": "Enhanced Crawler API",
        "version": "3.0.0"
    }
    
    if crawler_instance:
        response["features"] = {
            "ai_enabled": crawler_instance.ai_provider is not None,
            "ai_provider": crawler_instance.ai_provider.provider if crawler_instance.ai_provider else None,
            "cache_enabled": crawler_instance.fetcher.cache is not None,
            "learning_enabled": True
        }
    
    if initialization_error:
        response["error"] = initialization_error
    
    status_code = 200 if crawler_instance else 503
    return jsonify(response), status_code


@app.route('/', methods=['GET'])
def home():
    """Endpoint raíz con información del servicio."""
    return jsonify({
        "service": "Enhanced Crawler API with AI",
        "version": "3.0.0",
        "status": "running" if crawler_instance else "error",
        "features": [
            "Web crawling avanzado",
            "IA generativa (Claude/GPT)",
            "Sistema de aprendizaje continuo",
            "Caché inteligente",
            "Análisis NLP"
        ],
        "endpoints": {
            "POST /api/crawler": "Procesar consulta con IA",
            "POST /api/feedback": "Enviar feedback para aprendizaje",
            "GET /api/stats": "Obtener estadísticas de aprendizaje",
            "GET /api/health": "Health check",
            "GET /": "Información del servicio"
        },
        "usage": {
            "query": {
                "endpoint": "/api/crawler",
                "method": "POST",
                "body": {
                    "prompt": "¿Qué es Python?"
                }
            },
            "feedback": {
                "endpoint": "/api/feedback",
                "method": "POST",
                "body": {
                    "prompt": "consulta original",
                    "response": "respuesta completa",
                    "useful": True
                }
            }
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Manejador de errores 404."""
    return jsonify({
        "error": "Endpoint no encontrado",
        "available_endpoints": [
            "/",
            "/api/crawler",
            "/api/feedback",
            "/api/stats",
            "/api/health"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500."""
    return jsonify({
        "error": "Error interno del servidor",
        "details": str(error)
    }), 500


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Iniciando Enhanced Crawler API v3.0")
    print("=" * 70)
    
    if crawler_instance:
        print(f"✓ Sistema inicializado correctamente")
        print(f"  - IA: {crawler_instance.ai_provider.provider if crawler_instance.ai_provider else 'No disponible'}")
        print(f"  - Caché: {'Activado' if crawler_instance.fetcher.cache else 'Desactivado'}")
        print(f"  - Aprendizaje: Activado")
    else:
        print(f"✗ Error de inicialización")
        print(f"  - {initialization_error}")
    
    print("=" * 70)
    print(f"🌐 URL: http://127.0.0.1:{os.getenv('FLASK_PORT', '5000')}")
    print(f"📋 Endpoints disponibles:")
    print(f"   - POST /api/crawler (consultas)")
    print(f"   - POST /api/feedback (feedback)")
    print(f"   - GET /api/stats (estadísticas)")
    print(f"   - GET /api/health (health check)")
    print("=" * 70)
    
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False
    )