"""Lógica principal del Crawler con IA Generativa y Aprendizaje."""
import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
import json
import os

from config import (
    STOPWORDS, INTENT_PATTERNS, KNOWLEDGE_BASE, SEARCH_ENGINES,
    HTML_PATTERNS, DEFAULT_TIMEOUT, USER_AGENT, MAX_SEARCH_RESULTS
)
from utils import (
    SmartCache, clean_html, is_valid_fragment, 
    extract_keywords, calculate_confidence
)

# Dependencias
try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    requests = None
    _HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except ImportError:
    BeautifulSoup = None
    _HAS_BS4 = False

try:
    from anthropic import Anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

try:
    import openai
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False


class AIProvider:
    """Proveedor de IA generativa (Claude o OpenAI)."""
    
    def __init__(self):
        self.provider = None
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa el proveedor de IA disponible."""
        # Intentar Claude primero
        if _HAS_ANTHROPIC:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                try:
                    self.client = Anthropic(api_key=api_key)
                    self.provider = 'claude'
                    return
                except Exception:
                    pass
        
        # Intentar OpenAI
        if _HAS_OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    openai.api_key = api_key
                    self.client = openai
                    self.provider = 'openai'
                    return
                except Exception:
                    pass
    
    def generate(self, prompt: str, context: List[str], max_tokens: int = 1000) -> str:
        """Genera respuesta usando IA generativa."""
        if not self.provider:
            return self._fallback_response(prompt, context)
        
        # Construir prompt mejorado
        enhanced_prompt = self._build_enhanced_prompt(prompt, context)
        
        try:
            if self.provider == 'claude':
                return self._generate_claude(enhanced_prompt, max_tokens)
            elif self.provider == 'openai':
                return self._generate_openai(enhanced_prompt, max_tokens)
        except Exception as e:
            print(f"Error en IA: {e}")
            return self._fallback_response(prompt, context)
    
    def _build_enhanced_prompt(self, prompt: str, context: List[str]) -> str:
        """Construye prompt mejorado con contexto."""
        context_text = "\n".join([f"- {c}" for c in context[:10]])
        
        return f"""Basándote en la siguiente información de contexto, responde la pregunta de forma natural, clara y conversacional.

CONTEXTO:
{context_text}

PREGUNTA: {prompt}

INSTRUCCIONES:
- Responde de forma natural y conversacional
- Sintetiza la información del contexto
- Si el contexto no es suficiente, indica qué información falta
- Estructura la respuesta en párrafos claros
- Sé preciso pero accesible

RESPUESTA:"""
    
    def _generate_claude(self, prompt: str, max_tokens: int) -> str:
        """Genera con Claude."""
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _generate_openai(self, prompt: str, max_tokens: int) -> str:
        """Genera con OpenAI."""
        response = self.client.ChatCompletion.create(
            model="gpt-4",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def _fallback_response(self, prompt: str, context: List[str]) -> str:
        """Respuesta de fallback sin IA."""
        if not context:
            return "No encontré suficiente información para responder esta pregunta."
        
        intro = f"Basándome en la información disponible sobre tu consulta:"
        body = "\n\n".join(context[:5])
        conclusion = "\n\n¿Te gustaría que profundice en algún aspecto específico?"
        
        return f"{intro}\n\n{body}{conclusion}"


class EnhancedContentFetcher:
    """Fetcher mejorado con scraping avanzado."""
    
    def __init__(self, use_cache: bool = True):
        self.cache = SmartCache() if use_cache else None
        self.has_requests = _HAS_REQUESTS
        self.has_bs4 = _HAS_BS4
        self.session = requests.Session() if _HAS_REQUESTS else None
        
        if self.session:
            self.session.headers.update({'User-Agent': USER_AGENT})
    
    def search(self, query: str, keywords: List[str], 
               max_results: int = MAX_SEARCH_RESULTS) -> Tuple[List[str], List[str]]:
        """Búsqueda mejorada en múltiples fuentes."""
        
        # Cache check
        if self.cache:
            cached = self.cache.get(query)
            if cached:
                return cached.get('fragments', []), cached.get('sources', [])
        
        fragments = []
        sources = []
        
        # 1. Base de conocimiento local
        kb_fragments, kb_sources = self._search_knowledge_base(keywords)
        fragments.extend(kb_fragments)
        sources.extend(kb_sources)
        
        # 2. Búsqueda web mejorada
        if len(fragments) < max_results and self.has_requests:
            web_fragments, web_sources = self._enhanced_web_search(
                query, keywords, max_results - len(fragments)
            )
            fragments.extend(web_fragments)
            sources.extend(web_sources)
        
        # 3. Fallback
        if not fragments:
            fragments, sources = self._generate_fallback(query, keywords)
        
        # Cache save
        if self.cache:
            self.cache.set(query, {'fragments': fragments, 'sources': sources})
        
        return fragments[:max_results], sources[:max_results]
    
    def _enhanced_web_search(self, query: str, keywords: List[str], 
                            max_results: int) -> Tuple[List[str], List[str]]:
        """Búsqueda web mejorada con múltiples estrategias."""
        fragments = []
        sources = []
        
        search_query = ' '.join(keywords[:5])
        
        # Estrategia 1: DuckDuckGo HTML
        ddg_fragments, ddg_sources = self._search_duckduckgo(search_query)
        fragments.extend(ddg_fragments)
        sources.extend(ddg_sources)
        
        # Estrategia 2: Wikipedia API
        if len(fragments) < max_results:
            wiki_fragments, wiki_sources = self._search_wikipedia(search_query)
            fragments.extend(wiki_fragments)
            sources.extend(wiki_sources)
        
        # Estrategia 3: Google (alternativa)
        if len(fragments) < max_results:
            google_fragments, google_sources = self._search_google_alternative(search_query)
            fragments.extend(google_fragments)
            sources.extend(google_sources)
        
        return fragments, sources
    
    def _search_duckduckgo(self, query: str) -> Tuple[List[str], List[str]]:
        """Búsqueda en DuckDuckGo."""
        fragments = []
        sources = []
        
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
            response = self.session.get(url, timeout=DEFAULT_TIMEOUT)
            
            if response.status_code == 200:
                extracted = self._extract_content(response.text, url)
                fragments.extend(extracted['fragments'][:10])
                sources.extend(['DuckDuckGo'] * len(extracted['fragments'][:10]))
        except Exception:
            pass
        
        return fragments, sources
    
    def _search_wikipedia(self, query: str) -> Tuple[List[str], List[str]]:
        """Búsqueda en Wikipedia API."""
        fragments = []
        sources = []
        
        try:
            url = f"https://es.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'utf8': 1,
                'srlimit': 3
            }
            
            response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            data = response.json()
            
            if 'query' in data and 'search' in data['query']:
                for result in data['query']['search'][:3]:
                    snippet = re.sub(r'<[^>]+>', '', result.get('snippet', ''))
                    if is_valid_fragment(snippet):
                        fragments.append(snippet)
                        sources.append(f"Wikipedia: {result.get('title', 'Artículo')}")
        except Exception:
            pass
        
        return fragments, sources
    
    def _search_google_alternative(self, query: str) -> Tuple[List[str], List[str]]:
        """Búsqueda alternativa usando Google Custom Search o similar."""
        # Aquí podrías integrar Google Custom Search API
        # Por ahora retorna vacío
        return [], []
    
    def _search_knowledge_base(self, keywords: List[str]) -> Tuple[List[str], List[str]]:
        """Búsqueda en base de conocimiento con aprendizaje."""
        fragments = []
        sources = []
        
        # Cargar conocimiento aprendido
        learned_kb = self._load_learned_knowledge()
        combined_kb = {**KNOWLEDGE_BASE, **learned_kb}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Búsqueda exacta
            if keyword_lower in combined_kb:
                fragments.extend(combined_kb[keyword_lower])
                sources.extend(['Base de conocimiento'] * len(combined_kb[keyword_lower]))
                continue
            
            # Búsqueda parcial
            for topic, facts in combined_kb.items():
                if keyword_lower in topic.lower():
                    fragments.extend(facts)
                    sources.extend([f'KB: {topic}'] * len(facts))
        
        return fragments, sources
    
    def _load_learned_knowledge(self) -> Dict[str, List[str]]:
        """Carga conocimiento aprendido de feedback."""
        learned_file = os.path.join(os.path.dirname(__file__), 'data', 'learned_knowledge.json')
        
        if os.path.exists(learned_file):
            try:
                with open(learned_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {}
    
    def _extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extracción mejorada de contenido."""
        if not html:
            return {'fragments': [], 'metadata': {}}
        
        html = clean_html(html)
        
        if self.has_bs4:
            return self._extract_with_bs4_enhanced(html, url)
        else:
            return self._extract_with_regex(html)
    
    def _extract_with_bs4_enhanced(self, html: str, url: str) -> Dict[str, Any]:
        """Extracción mejorada con BeautifulSoup."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Limpiar elementos no deseados
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            fragments = []
            
            # Priorizar contenido principal
            main_content = soup.find(['main', 'article', 'div'], class_=re.compile(r'content|main|article'))
            search_area = main_content if main_content else soup
            
            # Extraer párrafos
            for p in search_area.find_all('p', limit=20):
                text = p.get_text(strip=True)
                if is_valid_fragment(text):
                    fragments.append(text)
            
            # Extraer listas
            for li in search_area.find_all('li', limit=15):
                text = li.get_text(strip=True)
                if is_valid_fragment(text):
                    fragments.append(text)
            
            # Extraer definiciones
            for dt in search_area.find_all('dt', limit=10):
                dd = dt.find_next_sibling('dd')
                if dd:
                    text = f"{dt.get_text(strip=True)}: {dd.get_text(strip=True)}"
                    if is_valid_fragment(text):
                        fragments.append(text)
            
            return {
                'fragments': fragments[:25],
                'metadata': {'url': url, 'method': 'bs4_enhanced'}
            }
        except Exception:
            return self._extract_with_regex(html)
    
    def _extract_with_regex(self, html: str) -> Dict[str, Any]:
        """Extracción básica con regex."""
        fragments = []
        
        for pattern in HTML_PATTERNS:
            for match in re.finditer(pattern, html, flags=re.DOTALL | re.IGNORECASE):
                text = re.sub(r'<[^>]+>', ' ', match.group(1))
                text = re.sub(r'\s+', ' ', text).strip()
                
                if is_valid_fragment(text):
                    fragments.append(text)
        
        return {
            'fragments': fragments[:20],
            'metadata': {'method': 'regex'}
        }
    
    def _generate_fallback(self, query: str, keywords: List[str]) -> Tuple[List[str], List[str]]:
        """Genera contenido de fallback."""
        kw = keywords[0] if keywords else 'este tema'
        
        fallback_facts = [
            f"Basándome en tu consulta sobre '{query}', puedo ofrecerte información general.",
            f"El tema de '{kw}' es amplio y tiene múltiples perspectivas.",
            f"Para obtener información más específica sobre '{query}', te recomiendo precisar tu pregunta."
        ]
        
        sources = ['Sistema de respaldo'] * len(fallback_facts)
        
        return fallback_facts, sources


class LearningSystem:
    """Sistema de aprendizaje continuo."""
    
    def __init__(self):
        self.feedback_file = os.path.join(os.path.dirname(__file__), 'data', 'feedback.json')
        self.learned_file = os.path.join(os.path.dirname(__file__), 'data', 'learned_knowledge.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Asegura que exista el directorio de datos."""
        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
    
    def add_feedback(self, prompt: str, response: Dict[str, Any], useful: bool):
        """Añade feedback del usuario."""
        entry = {
            'prompt': prompt,
            'response': response,
            'useful': bool(useful),
            'timestamp': str(datetime.now())
        }
        
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
        except Exception:
            data = []
        
        data.append(entry)
        
        with open(self.feedback_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Aprender de feedback positivo
        if useful:
            self._learn_from_feedback(entry)
    
    def _learn_from_feedback(self, entry: Dict[str, Any]):
        """Aprende de feedback positivo."""
        try:
            # Cargar conocimiento aprendido
            if os.path.exists(self.learned_file):
                with open(self.learned_file, 'r', encoding='utf-8') as f:
                    learned = json.load(f)
            else:
                learned = {}
            
            # Extraer keywords del prompt
            keywords = entry['response'].get('keywords', [])
            response_text = entry['response'].get('response_text', '')
            
            # Dividir respuesta en oraciones
            sentences = re.split(r'[.!?]\s+', response_text)
            valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
            
            # Añadir a conocimiento aprendido
            for keyword in keywords[:3]:
                keyword_lower = keyword.lower()
                if keyword_lower not in learned:
                    learned[keyword_lower] = []
                
                # Añadir oraciones relevantes
                for sentence in valid_sentences[:3]:
                    if sentence not in learned[keyword_lower]:
                        learned[keyword_lower].append(sentence)
            
            # Guardar
            with open(self.learned_file, 'w', encoding='utf-8') as f:
                json.dump(learned, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"Error en aprendizaje: {e}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de aprendizaje."""
        stats = {
            'total_feedback': 0,
            'positive_feedback': 0,
            'learned_topics': 0,
            'learned_facts': 0
        }
        
        # Feedback stats
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    feedback = json.load(f)
                    stats['total_feedback'] = len(feedback)
                    stats['positive_feedback'] = sum(1 for f in feedback if f.get('useful'))
            except Exception:
                pass
        
        # Learned knowledge stats
        if os.path.exists(self.learned_file):
            try:
                with open(self.learned_file, 'r', encoding='utf-8') as f:
                    learned = json.load(f)
                    stats['learned_topics'] = len(learned)
                    stats['learned_facts'] = sum(len(facts) for facts in learned.values())
            except Exception:
                pass
        
        return stats


class TextProcessor:
    """Procesador de texto mejorado."""
    
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.lower = prompt.lower()
        self.processed = self._process()
    
    def _process(self) -> Dict[str, Any]:
        """Análisis completo del prompt."""
        return {
            'intent': self._extract_intent(),
            'keywords': self._extract_keywords(),
            'entities': self._extract_entities(),
            'complexity': self._assess_complexity(),
            'question_type': self._classify_question_type(),
            'style': self._classify_style()
        }
    
    def _extract_intent(self) -> str:
        """Detecta intención del usuario."""
        intent_scores = Counter()
        
        for intent_type, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in self.lower:
                    intent_scores[intent_type] += 1
        
        if intent_scores:
            return intent_scores.most_common(1)[0][0]
        
        return 'consulta_general'
    
    def _extract_keywords(self) -> List[str]:
        """Extrae palabras clave relevantes."""
        keywords = extract_keywords(self.prompt, STOPWORDS)
        phrases = self._extract_key_phrases()
        
        all_keywords = keywords + phrases
        keyword_scores = Counter(all_keywords)
        
        for i, kw in enumerate(keywords[:5]):
            keyword_scores[kw] += (5 - i)
        
        return [kw for kw, _ in keyword_scores.most_common(15)]
    
    def _extract_key_phrases(self) -> List[str]:
        """Extrae frases clave."""
        phrases = []
        
        # Frases entre comillas
        quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', self.prompt)
        for q in quoted:
            phrase = (q[0] or q[1]).lower()
            if phrase:
                phrases.append(phrase)
        
        # Nombres propios
        proper_nouns = re.findall(
            r'\b[A-ZÁÉÍÓÚÜ][a-záéíóúñü]+(?:\s+[A-ZÁÉÍÓÚÜ][a-záéíóúñü]+)*\b', 
            self.prompt
        )
        phrases.extend([pn.lower() for pn in proper_nouns])
        
        return phrases[:10]
    
    def _extract_entities(self) -> Dict[str, Any]:
        """Extrae entidades nombradas."""
        entities = {}
        
        nums = re.findall(r"\b\d{1,4}\b", self.prompt)
        if nums:
            entities['numbers'] = nums
        
        dates = re.findall(r"\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b", self.prompt)
        if dates:
            entities['dates'] = dates
        
        urls = re.findall(r'https?://[^\s]+|www\.[^\s]+', self.prompt)
        if urls:
            entities['urls'] = urls
        
        return entities
    
    def _assess_complexity(self) -> str:
        """Evalúa complejidad."""
        score = 0
        
        word_count = len(self.lower.split())
        if word_count > 20:
            score += 3
        elif word_count > 10:
            score += 2
        elif word_count > 5:
            score += 1
        
        keywords = self._extract_keywords()
        if len(keywords) > 10:
            score += 2
        elif len(keywords) > 5:
            score += 1
        
        if self.lower.count('?') > 1:
            score += 2
        
        if score >= 7:
            return 'muy_alta'
        elif score >= 5:
            return 'alta'
        elif score >= 3:
            return 'media'
        else:
            return 'baja'
    
    def _classify_question_type(self) -> str:
        """Clasifica tipo de pregunta."""
        if any(self.lower.startswith(word) for word in ['es', 'son', 'tiene', 'hay']):
            return 'closed'
        
        if 'qué es' in self.lower or 'definición' in self.lower:
            return 'definition'
        
        if self.lower.startswith(('cómo', 'como')) or 'pasos' in self.lower:
            return 'procedural'
        
        if 'por qué' in self.lower:
            return 'causal'
        
        if any(word in self.lower for word in ['diferencia', 'comparar', 'mejor']):
            return 'comparative'
        
        return 'open'
    
    def _classify_style(self) -> str:
        """Clasifica estilo de respuesta."""
        if any(w in self.lower for w in ['noticias', 'últimas', 'reciente']):
            return 'news'
        
        if self.lower.startswith(('cómo', 'como')) or 'pasos' in self.lower:
            return 'tutor'
        
        if 'qué es' in self.lower or 'definición' in self.lower:
            return 'explain'
        
        if any(word in self.lower for word in ['diferencia', 'comparar']):
            return 'comparison'
        
        if 'por qué' in self.lower:
            return 'analytical'
        
        return 'conversational'
    
    def get_processed(self) -> Dict[str, Any]:
        """Retorna análisis completo."""
        return self.processed


class EnhancedCrawler:
    """Crawler mejorado con IA y aprendizaje."""
    
    def __init__(self, use_cache: bool = True, use_ai: bool = True):
        self.fetcher = EnhancedContentFetcher(use_cache=use_cache)
        self.ai_provider = AIProvider() if use_ai else None
        self.learning = LearningSystem()
    
    def run(self, prompt: str) -> Dict[str, Any]:
        """Ejecuta ciclo completo con IA."""
        
        # 1. Procesar prompt
        processor = TextProcessor(prompt)
        processed = processor.get_processed()
        keywords = processed.get('keywords', [])
        
        # 2. Buscar contenido
        fragments, sources = self.fetcher.search(prompt, keywords)
        
        # 3. Rankear y consolidar
        ranked_facts = self._rank_and_consolidate(fragments, keywords)
        
        # 4. Generar respuesta con IA o fallback
        if self.ai_provider and self.ai_provider.provider:
            response_text = self.ai_provider.generate(prompt, ranked_facts)
        else:
            response_text = self._generate_fallback_response(prompt, ranked_facts)
        
        # 5. Construir respuesta completa
        response = {
            'query': prompt,
            'intent': processed.get('intent'),
            'topics': keywords[:5],
            'keywords': keywords,
            'complexity': processed.get('complexity'),
            'question_type': processed.get('question_type'),
            'response_text': response_text,
            'sources': list(set(sources)),
            'confidence': calculate_confidence(ranked_facts, keywords),
            'style': processed.get('style'),
            'ai_provider': self.ai_provider.provider if self.ai_provider else 'fallback',
            'learning_stats': self.learning.get_learning_stats()
        }
        
        return {
            'prompt': prompt,
            'response': response
        }
    
    def add_feedback(self, prompt: str, response: Dict[str, Any], useful: bool):
        """Añade feedback para aprendizaje."""
        self.learning.add_feedback(prompt, response, useful)
    
    def _rank_and_consolidate(self, fragments: List[str], keywords: List[str], 
                               limit: int = 10) -> List[str]:
        """Rankea y consolida fragmentos."""
        if not fragments:
            return []
        
        scored = []
        for fragment in fragments:
            score = self._calculate_relevance(fragment, keywords)
            scored.append((score, fragment))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        seen = set()
        consolidated = []
        for score, fragment in scored:
            if fragment not in seen:
                seen.add(fragment)
                consolidated.append(fragment)
                if len(consolidated) >= limit:
                    break
        
        return consolidated
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """Calcula relevancia."""
        score = 0
        text_lower = text.lower()
        
        for kw in keywords:
            if kw.lower() in text_lower:
                score += 3
        
        score += sum(1 for ch in text if ch.isdigit()) * 0.1
        
        if 100 < len(text) < 500:
            score += 2
        
        return score
    
    def _generate_fallback_response(self, prompt: str, facts: List[str]) -> str:
        """Genera respuesta sin IA."""
        if not facts:
            return "No encontré suficiente información para responder con precisión. ¿Podrías reformular tu pregunta?"
        
        intro = "Basándome en la información disponible:"
        body = "\n\n".join(facts[:5])
        conclusion = "\n\n¿Te gustaría que profundice en algún aspecto específico?"
        
        return f"{intro}\n\n{body}{conclusion}"


# Para mantener compatibilidad
Crawler = EnhancedCrawler   