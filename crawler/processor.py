"""Clases para procesamiento de texto y extracción de información.

Incluye soporte opcional para SymPy (explicación/formulas) y spaCy (NER para timelines).
"""
import re
from typing import Dict, Any, List

# Dependencias opcionales
try:
    import sympy as _sympy
    _HAS_SYMPY = True
except Exception:
    _sympy = None
    _HAS_SYMPY = False

try:
    import spacy as _spacy
    _HAS_SPACY = True
    # intentar cargar modelo pequeño si está disponible
    try:
        _SPACY_NLP = _spacy.load('es_core_news_sm')
    except Exception:
        try:
            _SPACY_NLP = _spacy.load('en_core_web_sm')
        except Exception:
            _SPACY_NLP = None
            _HAS_SPACY = False
except Exception:
    _spacy = None
    _SPACY_NLP = None
    _HAS_SPACY = False


class TextProcessor:
    """Procesa prompts del usuario para extraer intent, keywords y entidades."""
    
    STOPWORDS = {
        'de', 'la', 'el', 'los', 'las', 'y', 'o', 'a', 'en', 'por', 'para',
        'con', 'sin', 'que', 'un', 'una', 'su', 'sus', 'al', 'del', 'es', 'mi', 'tu'
    }
    
    INTENT_KEYWORDS = ['dame', 'muéstrame', 'buscar', 'buscarme', 'encuentra', 'resumen', 'resume']
    
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.processed = self._process()
    
    def _process(self) -> Dict[str, Any]:
        """Realiza el análisis completo del prompt."""
        p = self.prompt.strip()
        lower = p.lower()
        
        intent = self._extract_intent(lower)
        keywords = self._extract_keywords(lower)
        entities = self._extract_entities(lower, p)
        
        return {
            'intent': intent,
            'keywords': keywords,
            'entities': entities
        }
    
    def _extract_intent(self, lower: str) -> str:
        """Detecta intención del usuario."""
        for kw in self.INTENT_KEYWORDS:
            if kw in lower:
                return 'buscar_informacion'
        return 'consulta'
    
    def _extract_keywords(self, lower: str) -> List[str]:
        """Extrae palabras clave relevantes."""
        tokens = re.findall(r"\b[\wáéíóúñü]+\b", lower)
        keywords = [
            t for t in tokens 
            if t not in self.STOPWORDS and len(t) >= 3
        ]
        return keywords
    
    def _extract_entities(self, lower: str, original: str) -> Dict[str, Any]:
        """Extrae entidades nombradas y patrones específicos."""
        entities = {}
        
        # Números
        nums = re.findall(r"\b\d{1,4}\b", original)
        if nums:
            entities['numbers'] = nums
        
        # Citas
        quotes = re.findall(r'"([^\"]+)"|\'([^\']+\')', original)
        if quotes:
            quote_vals = [q[0] or q[1] for q in quotes if q[0] or q[1]]
            entities['quotes'] = quote_vals
        
        # Tema explícito
        m_topic = re.search(r'tema[:=]\s*([\w\s,]+)', lower)
        if m_topic:
            entities['topics'] = [t.strip() for t in m_topic.group(1).split(',') if t.strip()]
        
        # Sitio específico
        m_site = re.search(r'site[:=]\s*([\w\.\-]+)', lower)
        if m_site:
            entities['site'] = m_site.group(1)
        
        return entities
    
    def get_processed(self) -> Dict[str, Any]:
        """Retorna el diccionario procesado."""
        # Añadir clasificación de estilo de respuesta
        self.processed['style'] = self._classify_style()
        return self.processed

    def _classify_style(self) -> str:
        """Clasifica el tipo de respuesta que se debe generar.

        Valores posibles: 'news', 'tutor', 'casual', 'technical', 'recommendation',
        'explain', 'historical', 'formula', 'overview'
        """
        lower = self.prompt.lower()
        kws = set(self.processed.get('keywords', []))

        # News
        if any(w in lower for w in ['noticias', 'últimas', 'último', 'reciente']):
            return 'news'

        # Historical event / narration
        if (re.search(r"\b(1[0-9]{3}|20[0-9]{2}|19[0-9]{2})\b", lower)
                or any(w in lower for w in ['qué pasó', 'que pasó', 'acontecimiento', 'batalla', 'revolución', 'guerra', 'nació', 'murió', 'fundó', 'fundación'])):
            return 'historical'

        # Formula / teorema / ecuación
        if ('fórmula' in lower or 'formula' in lower or 'ecuación' in lower or 'teorema' in lower
                or re.search(r'[=∫Σ√π\^]|deriv|derivada|integral|demostr', lower)):
            return 'formula'

        # Tutor / ejemplo / how-to
        if any(w in lower for w in ['cómo', 'como', 'ejemplo', 'pasos', 'tutorial', 'programa', 'codigo', 'código']):
            return 'tutor'

        # Technical / programación
        if any(w in kws for w in ['python', 'javascript', 'programacion', 'programación', 'api', 'json']):
            return 'technical'

        # Recommendation / compra / mejor
        if any(w in lower for w in ['mejor', 'recomienda', 'comprar', 'recomendación']):
            return 'recommendation'

        # Explain / definiciones
        if any(w in lower for w in ['qué es', 'que es', 'definición', 'definicion', 'explica', 'explicar']):
            return 'explain'

        # Overview / topic requests (broad overviews)
        if any(w in lower for w in ['introducción', 'introduccion', 'resumen', 'visión general', 'vision general', 'visió', 'tema', 'concepto']):
            return 'overview'

        # Default casual
        return 'casual'

    def extract_timeline_from_facts(self, facts: List[str]) -> List[Dict[str, Any]]:
        """Extrae timeline (año, texto, entidades) usando spaCy si está disponible, si no usa heurística."""
        timeline = []
        if not facts:
            return timeline

        if _HAS_SPACY and _SPACY_NLP:
            # concatenar facts para procesar
            text = '\n'.join(facts)
            doc = _SPACY_NLP(text)
            # buscar entes tipo DATE y PERSON y oraciones con años
            for ent in doc.ents:
                if ent.label_.lower() in ('date', 'time') or re.search(r"\b(1[0-9]{3}|20[0-9]{2}|19[0-9]{2})\b", ent.text):
                    # buscar oracion contenedora
                    sent = ent.sent.text if ent.sent else ent.text
                    year = None
                    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2}|19[0-9]{2})\b", sent)
                    if m:
                        year = int(m.group(1))
                    timeline.append({'year': year, 'text': sent, 'entity': ent.text})
            # fallback: si no hay entitades, buscar años manualmente
            if not timeline:
                for f in facts:
                    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2}|19[0-9]{2})\b", f)
                    if m:
                        timeline.append({'year': int(m.group(1)), 'text': f, 'entity': None})
        else:
            # heurística simple: buscar años en facts
            for f in facts:
                m = re.search(r"\b(1[0-9]{3}|20[0-9]{2}|19[0-9]{2})\b", f)
                if m:
                    timeline.append({'year': int(m.group(1)), 'text': f, 'entity': None})

        # ordenar por año siempre que sea posible
        timeline = sorted(timeline, key=lambda x: (x['year'] is None, x['year'] or 0))
        return timeline


class QueryBuilder:
    """Construye URLs de búsqueda a partir de prompts procesados."""
    
    DUCKDUCKGO_URL = 'https://html.duckduckgo.com/html/'
    WIKIPEDIA_SEARCH = 'https://en.wikipedia.org/w/api.php'
    
    def __init__(self, processed: Dict[str, Any], max_sites: int = 3):
        self.processed = processed
        self.max_sites = max_sites
    
    def build_urls(self) -> List[str]:
        """Genera lista de URLs para buscar."""
        urls = []
        kws = self.processed.get('keywords', [])
        
        # Si hay keywords, construir URLs múltiples
        if kws:
            # Wikipedia API search
            search_term = '+'.join(kws[:4])
            wiki_url = f"{self.WIKIPEDIA_SEARCH}?action=query&list=search&srsearch={search_term}&format=json&utf8"
            urls.append(wiki_url)
            
            # DuckDuckGo HTML
            ddg_q = '+'.join([re.sub(r'\s+', '+', kw) for kw in kws[:6]])
            urls.append(f"{self.DUCKDUCKGO_URL}?q={ddg_q}")
        else:
            # Fallback genérico
            urls.append(f"{self.DUCKDUCKGO_URL}?q=información")
        
        return urls[:self.max_sites]


class HTMLExtractor:
    """Extrae texto relevante de HTML."""
    
    PATTERNS = [
        r'<p[^>]*>(.*?)</p>',
        r'<li[^>]*>(.*?)</li>',
        r'<h[1-3][^>]*>(.*?)</h[1-3]>',
        r'<div[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</div>',
        r'<article[^>]*>(.*?)</article>',
        r'<section[^>]*>(.*?)</section>'
    ]
    
    @staticmethod
    def extract_fragments(html: str) -> list:
        """Extrae fragmentos de texto del HTML."""
        if not html:
            return []
        
        fragments = []
        
        # Buscar en tags comunes
        for pat in HTMLExtractor.PATTERNS:
            for m in re.finditer(pat, html, flags=re.IGNORECASE | re.DOTALL):
                    txt = re.sub(r'<[^>]+>', ' ', m.group(1))
                    txt = re.sub(r'\s+', ' ', txt).strip()
                    # Filtrar fragmentos muy cortos o ruidosos
                    if len(txt) > 50 and not HTMLExtractor._is_noise_fragment(txt):
                        fragments.append(txt)
        
        # Fallback: extraer del body si no hay fragmentos
        if not fragments:
            m = re.search(r'<body[^>]*>(.*?)</body>', html, flags=re.IGNORECASE | re.DOTALL)
            if m:
                txt = re.sub(r'<[^>]+>', ' ', m.group(1))
                txt = re.sub(r'\s+', ' ', txt).strip()
                if txt:
                    # Dividir en oraciones largas como fragmentos
                    frs = re.split(r'(?<=[\.|\!|\?])\s+', txt)
                    frs = [f for f in frs if 50 < len(f) < 500 and not HTMLExtractor._is_noise_fragment(f)]
                    fragments.extend(frs)
        return fragments

    @staticmethod
    def _is_noise_fragment(text: str) -> bool:
        """Detecta fragmentos con ruido típico (captchas, errores, navegación, etc.)."""
        if not text:
            return True
        t = text.lower()
        noise_signals = [
            'please complete the following challenge',
            'select all',
            'recaptcha',
            'error-lite',
            'access denied',
            'are you a robot',
            'to continue,',
            'javascript is required',
            'please enable javascript'
        ]
        for sig in noise_signals:
            if sig in t:
                return True
        # muchos enlaces o caracteres no alfabéticos
        if sum(1 for ch in t if ch.isalpha()) < 20 and len(t) < 200:
            return True
        return False

class FactConsolidator:
    """Consolida y puntúa fragmentos para obtener facts relevantes."""
    
    def __init__(self, processed: Dict[str, Any]):
        self.processed = processed
    
    def consolidate(self, fragments: List[str], limit: int = 8) -> List[str]:
        """Selecciona y ordena los mejores fragmentos."""
        if not fragments:
            return []
        
        scored = sorted(fragments, key=self._score, reverse=True)
        seen = set()
        out = []
        
        for f in scored:
            if f in seen:
                continue
            seen.add(f)
            out.append(f)
            if len(out) >= limit:
                break
        
        return out
    
    def _score(self, text: str) -> int:
        """Calcula puntuación de relevancia de un fragmento."""
        score = 0
        lower_text = text.lower()
        kws = [k.lower() for k in self.processed.get('keywords', [])]
        
        # Puntos por coincidencia de keywords
        for kw in kws:
            if kw in lower_text:
                score += 3
        
        # Puntos por números
        score += sum(1 for ch in text if ch.isdigit())
        
        # Puntos por longitud
        score += min(len(text) // 100, 3)
        
        return score


def generate_response(prompt: str, processed: Dict[str, Any], facts: List[str], source_urls: List[str]) -> Dict[str, Any]:
    """Genera el objeto response y una 'conversación' (diálogo) según el estilo.

    Devuelve dict con campos habituales + `dialogue`: lista de turnos {speaker, text}.
    """
    style = processed.get('style', 'casual')

    # Preparar summary corto
    if not facts:
        summary = 'No se encontraron resultados relevantes.'
    else:
        summary = ' '.join(facts[:4])

    # Construir diálogo según estilo
    dialogue = []

    if style == 'news':
        dialogue.append({'speaker': 'assistant', 'text': 'Aquí tienes un resumen rápido de las noticias relacionadas:'})
        for f in facts[:5]:
            dialogue.append({'speaker': 'assistant', 'text': f'- {f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Quieres que busque más detalles sobre alguno de estos puntos?'})

    elif style == 'tutor':
        dialogue.append({'speaker': 'assistant', 'text': 'Perfecto — vamos paso a paso:'})
        # Desglosar facts en pasos si es posible
        for i, f in enumerate(facts[:5], start=1):
            dialogue.append({'speaker': 'assistant', 'text': f'Paso {i}: {f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Quieres que te muestre un ejemplo concreto o código de ejemplo?'})

    elif style == 'technical':
        dialogue.append({'speaker': 'assistant', 'text': 'Te explico desde el punto de vista técnico:'})
        for f in facts[:4]:
            dialogue.append({'speaker': 'assistant', 'text': f'{f}'})
        # Añadir un pequeño ejemplo si keywords sugieren código
        if any(k in ['python','programacion','programación','api','json'] for k in processed.get('keywords', [])):
            dialogue.append({'speaker': 'assistant', 'text': 'Ejemplo simple (pseudo-código):'})
            dialogue.append({'speaker': 'assistant', 'text': "```python\nprint('Hola mundo')\n```"})
        dialogue.append({'speaker': 'assistant', 'text': '¿Te gustaría ver más detalle técnico? (logs, ejemplos, comparativas) '})

    elif style == 'recommendation':
        dialogue.append({'speaker': 'assistant', 'text': 'Según lo que buscas, te recomiendo lo siguiente:'})
        for f in facts[:5]:
            dialogue.append({'speaker': 'assistant', 'text': f'- {f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Prefieres que compare opciones concretas (precio, características)?'})

    elif style == 'explain':
        dialogue.append({'speaker': 'assistant', 'text': 'Vale — te lo explico con palabras sencillas:'})
        for f in facts[:5]:
            dialogue.append({'speaker': 'assistant', 'text': f'{f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Quieres una versión más técnica o un resumen aún más breve?'})

    elif style == 'historical':
        # Intent: narrar un acontecimiento histórico. Ordenar facts por año si es posible.
        dialogue.append({'speaker': 'assistant', 'text': 'Te cuento la secuencia de hechos relacionada con esto:'})
        # intentar extraer años de los facts y ordenar
        def extract_year(s):
            m = re.search(r"\b(1[0-9]{3}|20[0-9]{2}|19[0-9]{2})\b", s)
            return int(m.group(1)) if m else None

        facts_with_years = []
        facts_without = []
        for f in facts:
            y = extract_year(f)
            if y:
                facts_with_years.append((y, f))
            else:
                facts_without.append(f)

        facts_with_years.sort(key=lambda x: x[0])
        # si spaCy está disponible, construir timeline más rico
        if _HAS_SPACY and _SPACY_NLP:
            # `generate_response` is a function, not a method; use a TextProcessor instance to access the extractor
            timeline = TextProcessor('').extract_timeline_from_facts(facts)
            if timeline:
                for item in timeline:
                    if item['year']:
                        dialogue.append({'speaker': 'assistant', 'text': f"{item['year']}: {item['text']}"})
                    else:
                        dialogue.append({'speaker': 'assistant', 'text': item['text']})
            else:
                for y, f in facts_with_years:
                    dialogue.append({'speaker': 'assistant', 'text': f'{y}: {f}'})
                for f in facts_without[:6]:
                    dialogue.append({'speaker': 'assistant', 'text': f'{f}'})
        else:
            for y, f in facts_with_years:
                dialogue.append({'speaker': 'assistant', 'text': f'{y}: {f}'})
            for f in facts_without[:6]:
                dialogue.append({'speaker': 'assistant', 'text': f'{f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Quieres que profundice en algún año o personaje específico?'})

    elif style == 'formula':
        # Intent: explicar una fórmula y su porqué. Buscar fórmula en prompt o facts.
        dialogue.append({'speaker': 'assistant', 'text': 'Voy a explicar la fórmula y el razonamiento detrás:'})
        # intentar identificar texto con símbolo '=' o palabras clave matemáticas
        formula = None
        for f in facts:
            if '=' in f or 'integral' in f or 'deriv' in f or 'teorema' in f or re.search(r'[∫Σ√π\^]', f):
                formula = f
                break
        # Si no hay, intentar sacar fórmula del prompt
        if not formula:
            m = re.search(r'([A-Za-z0-9\s\^\*\/=\+\-\(\)\.]+=[A-Za-z0-9\s\^\*\/=\+\-\(\)\.]+)', prompt)
            if m:
                formula = m.group(1)

        if formula:
            # Presentar la fórmula y descomponerla
            dialogue.append({'speaker': 'assistant', 'text': f'Fórmula encontrada: {formula}'})
            # Intentar usar SymPy para explicar/derivar
            if _HAS_SYMPY:
                try:
                    expr = _sympy.sympify(formula, evaluate=False)
                    simp = _sympy.simplify(expr)
                    dialogue.append({'speaker': 'assistant', 'text': f'Simplificación simbólica: {str(simp)}'})
                    # Si se pide derivada explícitamente en prompt, hacer derivada respecto a variable si es posible
                    if re.search(r'deriv|derivada|derivar|d/d', prompt.lower()):
                        # intentar detectar variable
                        vars = list(expr.free_symbols)
                        if vars:
                            var = vars[0]
                            deriv = _sympy.diff(expr, var)
                            dialogue.append({'speaker': 'assistant', 'text': f'Derivada respecto a {var}: {str(deriv)}'})
                            dialogue.append({'speaker': 'assistant', 'text': 'Paso a paso (resumen): aplicar reglas de derivación básicas y simplificar.'})
                        else:
                            dialogue.append({'speaker': 'assistant', 'text': 'No pude identificar la variable para derivar automáticamente.'})
                    else:
                        # ofrecer derivación
                        dialogue.append({'speaker': 'assistant', 'text': 'Puedo derivarla paso a paso si lo deseas. ¿Quieres que lo haga?'})
                except Exception:
                    # fallback a descomposición simple
                    parts = re.split(r'(=|\+|\-|\*|/|\^)', formula)
                    parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) > 1:
                        dialogue.append({'speaker': 'assistant', 'text': 'Descomposición de la fórmula:'})
                        for p in parts:
                            dialogue.append({'speaker': 'assistant', 'text': f'- {p}'})
                        dialogue.append({'speaker': 'assistant', 'text': 'Explicación: cada término tiene su significado; la relación se deriva mediante definiciones y operaciones algebraicas o cálculo según corresponda.'})
                    else:
                        dialogue.append({'speaker': 'assistant', 'text': 'Descripción: ' + formula})
                    dialogue.append({'speaker': 'assistant', 'text': '¿Quieres que haga una derivación paso a paso (si aplica)?'})
            else:
                parts = re.split(r'(=|\+|\-|\*|/|\^)', formula)
                parts = [p.strip() for p in parts if p.strip()]
                if len(parts) > 1:
                    dialogue.append({'speaker': 'assistant', 'text': 'Descomposición de la fórmula:'})
                    for p in parts:
                        dialogue.append({'speaker': 'assistant', 'text': f'- {p}'})
                    dialogue.append({'speaker': 'assistant', 'text': 'Explicación: cada término tiene su significado; la relación se deriva mediante definiciones y operaciones algebraicas o cálculo según corresponda.'})
                else:
                    dialogue.append({'speaker': 'assistant', 'text': 'Descripción: ' + formula})
                dialogue.append({'speaker': 'assistant', 'text': '¿Quieres que haga una derivación paso a paso (si aplica)?'})
        else:
            dialogue.append({'speaker': 'assistant', 'text': 'No encontré una fórmula explícita en los resultados, pero puedo explicarte el concepto matemático relacionado:'})
            for f in facts[:5]:
                dialogue.append({'speaker': 'assistant', 'text': f'{f}'})
            dialogue.append({'speaker': 'assistant', 'text': '¿Te interesa que lo desarrolle con notación matemática y pasos formales?'})

    elif style == 'overview':
        dialogue.append({'speaker': 'assistant', 'text': 'Aquí tienes una visión general del tema:'})
        # bullets con puntos clave
        for f in facts[:6]:
            dialogue.append({'speaker': 'assistant', 'text': f'- {f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Quieres que amplíe alguno de estos puntos o prefieres referencias para leer más?'})

    else:  # casual
        dialogue.append({'speaker': 'assistant', 'text': '¡Buena pregunta! Te cuento lo esencial:'})
        for f in facts[:4]:
            dialogue.append({'speaker': 'assistant', 'text': f'{f}'})
        dialogue.append({'speaker': 'assistant', 'text': '¿Te interesa profundizar en algún punto o seguimos con otra cosa?'})

    return {
        'query': prompt,
        'intent': processed.get('intent'),
        'topics': processed.get('entities', {}).get('topics', []),
        'keywords': processed.get('keywords', []),
        'validated_facts': facts,
        'summary': summary,
        'source_urls': source_urls,
        'dialogue': dialogue,
        'style': style
    }
