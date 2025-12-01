"""Entrenador mínimo para construir un índice TF-IDF sobre la KB local.

Genera archivos persistidos en `crawler/data/`:
- `vectorizer.joblib` (TfidfVectorizer)
- `tfidf.joblib` (matriz TF-IDF)
- `docs.joblib` (lista de documentos)

Este es un prototipo ligero ideal para búsquedas extractivas.
"""
import os
from typing import List, Dict, Any

try:
    import joblib
    _HAS_JOBLIB = True
except Exception:
    joblib = None
    _HAS_JOBLIB = False
import pickle
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    _HAS_SKLEARN = True
except Exception:
    TfidfVectorizer = None
    _HAS_SKLEARN = False

from fetcher import KNOWLEDGE_BASE
import json
import pathlib


class Trainer:
    @staticmethod
    def train(output_dir: str = 'data') -> Dict[str, Any]:
        os.makedirs(output_dir, exist_ok=True)

        docs: List[Dict[str, Any]] = []
        # Convertir la base de conocimiento en documentos (cada hecho es un doc)
        doc_id = 0
        for topic, facts in KNOWLEDGE_BASE.items():
            for fact in facts:
                docs.append({'id': doc_id, 'topic': topic, 'text': fact, 'source': f'KB:{topic}'})
                doc_id += 1

        texts = [d['text'] for d in docs]

        vectorizer = None
        tfidf = None
        # Vectorizador TF-IDF simple (si sklearn está instalado)
        if _HAS_SKLEARN:
            # Try to use a Spanish stopword list if available (nltk), otherwise fall back to no stop words
            stop_words = None
            try:
                from nltk.corpus import stopwords as nltk_stopwords
                # Ensure the corpus is downloaded; if not, this may raise an exception
                spanish_words = set(nltk_stopwords.words('spanish'))
                stop_words = list(spanish_words)
            except Exception:
                stop_words = None

            vectorizer = TfidfVectorizer(stop_words=stop_words, ngram_range=(1, 2), min_df=1)
            tfidf = vectorizer.fit_transform(texts)

        # Persistir artefactos
        vec_path = os.path.join(output_dir, 'vectorizer.joblib')
        tfidf_path = os.path.join(output_dir, 'tfidf.joblib')
        docs_path = os.path.join(output_dir, 'docs.joblib')

        # Incluir scraped docs si existen
        scraped_path_json = os.path.join(output_dir, 'scraped_docs.json')
        if os.path.exists(scraped_path_json):
            try:
                with open(scraped_path_json, 'r', encoding='utf-8') as f:
                    scraped = json.load(f)
                # añadir scraped docs al final
                for sd in scraped:
                    docs.append({'id': len(docs), 'topic': sd.get('title','scraped'), 'text': sd.get('text',''), 'source': sd.get('url','scraped')})
            except Exception:
                pass

        texts = [d['text'] for d in docs]

        # Persistir artefactos (joblib preferido, fallback a pickle)
        if _HAS_JOBLIB:
            joblib.dump(vectorizer, vec_path)
            joblib.dump(tfidf, tfidf_path)
            joblib.dump(docs, docs_path)
        else:
            with open(vec_path, 'wb') as f:
                pickle.dump(vectorizer, f)
            with open(tfidf_path, 'wb') as f:
                pickle.dump(tfidf, f)
            with open(docs_path, 'wb') as f:
                pickle.dump(docs, f)

        return {
            'vectorizer': vec_path,
            'tfidf': tfidf_path,
            'docs': docs_path,
            'n_docs': len(docs)
        }


if __name__ == '__main__':
    out = Trainer.train()
    print('Entrenamiento completado:', out)
