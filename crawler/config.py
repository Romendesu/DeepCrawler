"""Configuración y constantes del Crawler."""
from pathlib import Path

# Directorios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
CACHE_DIR = DATA_DIR / 'cache'

# Configuración de caché
CACHE_TTL_HOURS = 24
USE_CACHE = True

# Configuración de búsqueda
MAX_SEARCH_RESULTS = 5
DEFAULT_TIMEOUT = 10
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Stopwords en español
STOPWORDS = {
    'de', 'la', 'el', 'los', 'las', 'y', 'o', 'a', 'en', 'por', 'para',
    'con', 'sin', 'que', 'un', 'una', 'su', 'sus', 'al', 'del', 'es', 
    'mi', 'tu', 'pero', 'como', 'si', 'no', 'más', 'muy', 'este', 'ese'
}

# Patrones de intención
INTENT_PATTERNS = {
    'explicación': ['qué es', 'que es', 'explica', 'definir', 'definición'],
    'comparación': ['diferencia', 'comparar', 'vs', 'versus', 'mejor que'],
    'procedimiento': ['cómo', 'como', 'pasos', 'tutorial', 'guía'],
    'causas': ['por qué', 'porque', 'razón', 'motivo', 'causa'],
    'ejemplos': ['ejemplo', 'ejemplos', 'caso', 'demostración'],
    'actualidad': ['actual', 'últimas', 'reciente', 'hoy', 'ahora'],
    'listado': ['lista', 'enumera', 'cuáles', 'tipos', 'categorías']
}

# Base de conocimiento local
KNOWLEDGE_BASE = {
    "python": [
        "Python es un lenguaje de programación interpretado cuya filosofía hace hincapié en la legibilidad de su código.",
        "Python fue creado por Guido van Rossum en 1989 y presentado públicamente en 1991.",
        "Python utiliza indentación para delimitar bloques de código.",
        "Es un lenguaje multipropósito que soporta orientación a objetos, programación imperativa y funcional.",
        "Python tiene tipado dinámico y gestión automática de memoria."
    ],
    "inteligencia artificial": [
        "La inteligencia artificial es la rama de la informática que crea máquinas capaces de realizar tareas que requieren inteligencia humana.",
        "El aprendizaje automático permite que los sistemas aprendan y mejoren a partir de la experiencia.",
        "Las redes neuronales artificiales son modelos inspirados en el cerebro humano.",
        "El procesamiento del lenguaje natural permite a las máquinas comprender y generar lenguaje humano.",
        "La visión por computadora permite interpretar el contenido de imágenes y vídeos."
    ],
    "machine learning": [
        "El aprendizaje automático es una rama de la IA que permite crear sistemas que aprenden de los datos.",
        "Los algoritmos de aprendizaje supervisado requieren datos etiquetados para entrenar.",
        "El aprendizaje no supervisado busca encontrar patrones en datos sin etiquetar.",
        "La validación cruzada evalúa el rendimiento de un modelo usando diferentes subconjuntos.",
        "El sobreajuste ocurre cuando un modelo aprende detalles específicos en lugar de patrones generales."
    ],
    "web": [
        "World Wide Web es un sistema de documentos interconectados que funciona sobre internet.",
        "HTTP es el protocolo principal utilizado para transmitir datos en la web.",
        "HTML es el lenguaje de marcado para crear páginas web.",
        "CSS controla la presentación y el diseño de las páginas web.",
        "JavaScript se ejecuta en los navegadores para crear interactividad."
    ],
    "programacion": [
        "La programación es el arte de crear instrucciones para que las computadoras realicen tareas.",
        "Los lenguajes de programación permiten comunicarse con las computadoras.",
        "Los paradigmas incluyen imperativo, declarativo, orientado a objetos y funcional.",
        "El debugging es el proceso de identificar y corregir errores en el código.",
        "La documentación del código es fundamental para el mantenimiento."
    ]
}

# Motores de búsqueda
SEARCH_ENGINES = {
    'duckduckgo': 'https://html.duckduckgo.com/html/?q={query}',
    'wikipedia': 'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json'
}

# Patrones HTML para extracción
HTML_PATTERNS = [
    r'<p[^>]*>(.*?)</p>',
    r'<li[^>]*>(.*?)</li>',
    r'<h[1-3][^>]*>(.*?)</h[1-3]>',
    r'<article[^>]*>(.*?)</article>'
]

# Patrones de ruido
NOISE_PATTERNS = [
    'captcha', 'recaptcha', 'challenge', 'verify', 'robot',
    'javascript required', 'enable javascript', 'cookies required',
    'access denied', '403', '404', 'error', 'blocked'
]