"""Retriever mínimo que carga el índice TF-IDF y recupera documentos relevantes."""
from typing import List, Dict, Any
import os
try:
    import joblib
    _HAS_JOBLIB = True
except Exception:
    joblib = None
    _HAS_JOBLIB = False
import pickle
try:
    from sklearn.metrics.pairwise import cosine_similarity
    _HAS_SKLEARN = True
except Exception:
    cosine_similarity = None
    _HAS_SKLEARN = False


class Retriever:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.vectorizer = None
        self.tfidf = None
        self.docs = None
        self._load()

    def _load(self):
        vec_path = os.path.join(self.data_dir, 'vectorizer.joblib')
        tfidf_path = os.path.join(self.data_dir, 'tfidf.joblib')
        docs_path = os.path.join(self.data_dir, 'docs.joblib')

        # Intentar cargar los 3 artefactos; si faltan vectorizer/tfidf, cargamos docs y usamos fallback sencillo
        if not os.path.exists(docs_path):
            raise FileNotFoundError('Docs no encontrado. Ejecuta `trainer.Trainer.train()` primero.')

        # Cargar docs siempre
        if _HAS_JOBLIB:
            self.docs = joblib.load(docs_path)
        else:
            with open(docs_path, 'rb') as f:
                self.docs = pickle.load(f)

        # Intentar cargar vectorizer/tfidf si existen
        if os.path.exists(vec_path) and os.path.exists(tfidf_path):
            try:
                if _HAS_JOBLIB:
                    self.vectorizer = joblib.load(vec_path)
                    self.tfidf = joblib.load(tfidf_path)
                else:
                    with open(vec_path, 'rb') as f:
                        self.vectorizer = pickle.load(f)
                    with open(tfidf_path, 'rb') as f:
                        self.tfidf = pickle.load(f)
            except Exception:
                # ignorar y usar fallback
                self.vectorizer = None
                self.tfidf = None
        # intentar incluir scraped docs si existen (paralelo a docs)
        scraped_json = os.path.join(self.data_dir, 'scraped_docs.json')
        if os.path.exists(scraped_json):
            try:
                import json
                with open(scraped_json, 'r', encoding='utf-8') as f:
                    scraped = json.load(f)
                # mapear scraped a formato docs
                for sd in scraped:
                    self.docs.append({'id': len(self.docs), 'topic': sd.get('title','scraped'), 'text': sd.get('text',''), 'source': sd.get('url','scraped')})
            except Exception:
                pass

    def retrieve(self, query: str, topk: int = 5) -> List[Dict[str, Any]]:
        if not query:
            return []

        # Si tenemos vectorizer/tfidf y sklearn disponible, usar búsqueda TF-IDF
        if self.vectorizer is not None and self.tfidf is not None and _HAS_SKLEARN:
            qv = self.vectorizer.transform([query])
            sims = cosine_similarity(qv, self.tfidf).flatten()
            idxs = sims.argsort()[::-1][:topk]
            results = []
            for idx in idxs:
                results.append({
                    'score': float(sims[idx]),
                    'text': self.docs[idx]['text'],
                    'topic': self.docs[idx]['topic'],
                    'source': self.docs[idx]['source']
                })
            return results

        # Fallback: puntuación por solapamiento simple de tokens
        q_tokens = set([w.lower() for w in query.split() if len(w) > 2])
        scored = []
        for d in self.docs:
            d_tokens = set([w.lower() for w in d['text'].split() if len(w) > 2])
            score = len(q_tokens & d_tokens)
            scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, d in scored[:topk]:
            results.append({'score': float(score), 'text': d['text'], 'topic': d['topic'], 'source': d['source']})
        return results

    def retrieve_as_html(self, query: str, topk: int = 5) -> str:
        """Devuelve los resultados formateados en HTML (compatible con el extractor actual)."""
        results = self.retrieve(query, topk=topk)
        if not results:
            return ''
        paragraphs = '\n'.join([f"<p>{r['text']}</p>" for r in results])
        return f"<html><body>{paragraphs}</body></html>"


if __name__ == '__main__':
    # uso rápido desde CLI
    import sys
    q = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'python'
    try:
        r = Retriever()
        print(r.retrieve(q))
    except Exception as e:
        print('Error:', e)
