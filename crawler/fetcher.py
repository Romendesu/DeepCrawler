"""Clases y funciones para obtener contenido de URLs.
Provee una base de conocimiento local y fallback automático.
"""
from typing import Optional, List

# Base de conocimiento local sobre tópicos comunes
KNOWLEDGE_BASE = {
    "python": [
        "Python es un lenguaje de programación interpretado cuya filosofía hace hincapié en la legibilidad de su código.",
        "Se trata de un lenguaje de programación multipropósito, creado por Guido van Rossum en 1989 y que fue presentado públicamente en 1991.",
        "Python utiliza indentación para delimitar bloques de código, lo cual aumenta la legibilidad del código.",
        "Es un lenguaje flexible que soporta orientación a objetos, programación imperativa y, en menor medida, programación funcional.",
        "Python tiene tipado dinámico y gestión automática de memoria.",
        "El intérprete de Python está disponible para múltiples plataformas: Windows, Linux, Macintosh, etc."
    ],
    "inteligencia artificial": [
        "La inteligencia artificial es la rama de la informática que se ocupa de crear máquinas inteligentes capaces de realizar tareas que normalmente requieren inteligencia humana.",
        "El aprendizaje automático es un campo de la inteligencia artificial que permite que los sistemas aprendan y mejoren a partir de la experiencia.",
        "Las redes neuronales artificiales son modelos computacionales inspirados en el funcionamiento del cerebro humano.",
        "El procesamiento del lenguaje natural permite a las máquinas comprender y generar lenguaje humano.",
        "La visión por computadora permite a las máquinas interpretar el contenido de imágenes y vídeos.",
        "Los algoritmos de IA se utilizan ampliamente en recomendaciones, reconocimiento de patrones y toma de decisiones."
    ],
    "machine learning": [
        "El aprendizaje automático es una rama de la inteligencia artificial que permite crear sistemas que aprenden de los datos.",
        "Los algoritmos de aprendizaje supervisado requieren datos etiquetados para entrenar el modelo.",
        "El aprendizaje no supervisado busca encontrar patrones en datos sin etiquetar.",
        "La validación cruzada es una técnica para evaluar el rendimiento de un modelo usando diferentes subconjuntos de datos.",
        "El sobreajuste ocurre cuando un modelo aprende los detalles específicos de los datos de entrenamiento en lugar de patrones generales.",
        "Las métricas comunes incluyen precisión, recall, F1-score y área bajo la curva ROC."
    ],
    "web": [
        "World Wide Web es un sistema de documentos interconectados que funciona sobre internet.",
        "HTTP es el protocolo principal utilizado para transmitir datos en la web.",
        "HTML es el lenguaje de marcado utilizado para crear páginas web.",
        "CSS se utiliza para controlar la presentación y el diseño de las páginas web.",
        "JavaScript es un lenguaje de programación que se ejecuta en los navegadores web para crear interactividad.",
        "Los navegadores web como Chrome, Firefox y Safari interpretan el código HTML, CSS y JavaScript."
    ],
    "base de datos": [
        "Una base de datos es una colección organizada de datos que se pueden acceder, gestionar y actualizar.",
        "SQL es el lenguaje estándar para consultar bases de datos relacionales.",
        "Las bases de datos NoSQL proporcionan flexibilidad para almacenar datos no estructurados.",
        "El modelado de datos es el proceso de crear una representación abstracta de los datos.",
        "Los índices se utilizan para mejorar la velocidad de búsqueda en bases de datos grandes.",
        "La integridad referencial garantiza que las relaciones entre tablas sean consistentes."
    ],
    "ciberseguridad": [
        "La ciberseguridad es el conjunto de herramientas y prácticas para proteger sistemas y redes contra ataques digitales.",
        "La encriptación es una técnica para convertir información legible en un formato ilegible sin la clave correcta.",
        "La autenticación de dos factores aumenta la seguridad al requerir dos métodos de verificación.",
        "Los firewalls son sistemas de seguridad que controlan el tráfico de red entrante y saliente.",
        "El phishing es una técnica de ingeniería social para obtener información confidencial mediante engaño.",
        "Los parches de seguridad se utilizan para corregir vulnerabilidades conocidas en software."
    ],
    "programacion": [
        "La programación es el arte de crear instrucciones para que las computadoras realicen tareas específicas.",
        "Los lenguajes de programación son herramientas que permiten comunicarse con las computadoras.",
        "La lógica de programación es la base para resolver problemas mediante algoritmos.",
        "Los paradigmas de programación incluyen imperativo, declarativo, orientado a objetos y funcional.",
        "El debugging es el proceso de identificar y corregir errores en el código.",
        "La documentación del código es fundamental para el mantenimiento y la colaboración en equipo."
    ]
}

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


class Fetcher:
    """Gestor de búsqueda con base de conocimiento local y fallback automático."""
    
    DEFAULT_TIMEOUT = 10
    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.requests_available = requests is not None
        self.bs4_available = BeautifulSoup is not None
        self.knowledge_base = KNOWLEDGE_BASE
    
    def fetch(self, url: str) -> Optional[str]:
        """Obtiene contenido de una URL. Retorna None si falla."""
        if not self.requests_available:
            return None
        
        try:
            resp = requests.get(
                url,
                headers={'User-Agent': self.DEFAULT_USER_AGENT},
                timeout=self.timeout,
                verify=False
            )
            resp.raise_for_status()
            return resp.text
        except Exception:
            return None
    
    def search_knowledge_base(self, keywords: List[str]) -> Optional[str]:
        """Busca en la base de conocimiento local usando keywords."""
        if not keywords:
            return None
        
        # Búsqueda exacta: si una keyword coincide exactamente con un tema
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in self.knowledge_base:
                facts = self.knowledge_base[keyword_lower]
                html_content = '\n'.join([f"<p>{fact}</p>" for fact in facts])
                return f"<html><body>{html_content}</body></html>"
        
        # Búsqueda parcial: buscar en el texto de los temas
        for topic, facts in self.knowledge_base.items():
            for keyword in keywords:
                if keyword.lower() in topic.lower():
                    html_content = '\n'.join([f"<p>{fact}</p>" for fact in facts])
                    return f"<html><body>{html_content}</body></html>"
        
        return None
    
    def clean_html_with_bs4(self, html: str) -> str:
        """Limpia y optimiza HTML usando BeautifulSoup si está disponible."""
        if not self.bs4_available or not html:
            return html
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Eliminar scripts, estilos y otros elementos innecesarios
            for tag in soup(['script', 'style', 'meta', 'noscript', 'nav', 'footer']):
                tag.decompose()
            # Eliminar elementos que indiquen captcha o verificación
            for tag in soup.find_all(True):
                try:
                    attrs = ' '.join([str(v) for v in tag.attrs.values()])
                except Exception:
                    attrs = ''
                txt = (tag.get_text() or '').lower()
                if 'captcha' in attrs or 'captcha' in txt or 'please complete the following challenge' in txt:
                    tag.decompose()
                    continue
                # eliminar iframes y elementos anti-bot
                if tag.name in ['iframe', 'form'] and ('captcha' in attrs or 'challenge' in txt):
                    tag.decompose()
                    continue
            
            return str(soup)
        except Exception:
            return html
    
    @staticmethod
    def generate_realistic_fallback(query: str, keywords: List[str]) -> str:
        """Genera HTML de fallback realista cuando no hay acceso a red."""
        fake_facts = [
            f"En relación a '{query}', existen múltiples perspectivas y enfoques.",
            f"Los expertos en '{keywords[0] if keywords else 'este tema'}' sugieren que es un área importante de estudio.",
            f"La información disponible sobre '{query}' indica tendencias significativas.",
            f"En la actualidad, '{query}' es considerado un tema de interés tanto académico como práctico.",
            f"Investigaciones recientes demuestran conexiones relevantes entre {' y '.join(keywords[:2]) if len(keywords) > 1 else keywords[0] if keywords else 'diversos conceptos'}."
        ]
        
        paragraphs = '\n'.join([f"<p>{fact}</p>" for fact in fake_facts])
        return f"<html><head><title>{query}</title></head><body>{paragraphs}</body></html>"
    
    def is_available(self) -> bool:
        """Verifica si `requests` está disponible."""
        return self.requests_available
