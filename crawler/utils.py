"""Utilidades auxiliares para el Crawler."""
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from config import CACHE_DIR, CACHE_TTL_HOURS, NOISE_PATTERNS


class SmartCache:
    """Sistema de caché inteligente con expiración."""
    
    def __init__(self, cache_dir: Path = CACHE_DIR, ttl_hours: int = CACHE_TTL_HOURS):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.index_file = self.cache_dir / 'index.json'
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Carga índice de caché."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_index(self):
        """Guarda índice de caché."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _get_cache_key(self, query: str) -> str:
        """Genera clave única para query."""
        return hashlib.md5(query.encode('utf-8')).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Obtiene resultado cacheado si existe y no ha expirado."""
        cache_key = self._get_cache_key(query)
        
        if cache_key not in self.index:
            return None
        
        entry = self.index[cache_key]
        cached_time = datetime.fromisoformat(entry['timestamp'])
        
        if datetime.now() - cached_time > self.ttl:
            self.remove(query)
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        
        return None
    
    def set(self, query: str, data: Dict[str, Any]):
        """Guarda resultado en caché."""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.index[cache_key] = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'file': str(cache_file)
            }
            self._save_index()
        except Exception:
            pass
    
    def remove(self, query: str):
        """Elimina entrada de caché."""
        cache_key = self._get_cache_key(query)
        
        if cache_key in self.index:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                cache_file.unlink()
            
            del self.index[cache_key]
            self._save_index()
    
    def clear_expired(self):
        """Limpia entradas expiradas."""
        expired_keys = []
        
        for cache_key, entry in self.index.items():
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
            del self.index[key]
        
        if expired_keys:
            self._save_index()


def clean_html(html: str) -> str:
    """Limpia HTML de scripts y ruido."""
    if not html:
        return ""
    
    # Eliminar scripts y estilos
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    return html


def is_valid_fragment(text: str) -> bool:
    """Valida si un fragmento es relevante."""
    if not text or len(text) < 40:
        return False
    
    if len(text) > 1000:
        return False
    
    text_lower = text.lower()
    for noise in NOISE_PATTERNS:
        if noise in text_lower:
            return False
    
    # Verificar proporción de caracteres alfabéticos
    alpha_count = sum(1 for c in text if c.isalpha())
    if alpha_count < len(text) * 0.5:
        return False
    
    return True


def extract_keywords(text: str, stopwords: set) -> list:
    """Extrae palabras clave del texto."""
    tokens = re.findall(r"\b[\wáéíóúñü]+\b", text.lower())
    keywords = [t for t in tokens if t not in stopwords and len(t) >= 3]
    return keywords


def calculate_confidence(facts: list, keywords: list) -> float:
    """Calcula confianza en la respuesta."""
    if not facts:
        return 0.0
    
    fact_count_score = min(len(facts) / 5.0, 1.0)
    
    relevance_score = 0.0
    for fact in facts:
        fact_lower = fact.lower()
        matches = sum(1 for kw in keywords if kw.lower() in fact_lower)
        relevance_score += matches
    
    relevance_score = min(relevance_score / (len(keywords) * len(facts)), 1.0) if keywords and facts else 0.5
    
    confidence = (fact_count_score * 0.4 + relevance_score * 0.6)
    return round(confidence, 2)


def save_feedback(prompt: str, response: Dict[str, Any], useful: bool, 
                  feedback_file: Path = None):
    """Guarda feedback del usuario."""
    if feedback_file is None:
        feedback_file = Path(__file__).parent / 'data' / 'feedback.json'
    
    feedback_file.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        'prompt': prompt,
        'response': response,
        'useful': bool(useful),
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        if feedback_file.exists():
            with open(feedback_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []
    
    data.append(entry)
    
    with open(feedback_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)