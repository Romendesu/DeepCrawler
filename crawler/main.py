#!/usr/bin/env python3
"""Entrypoint principal del crawler. Orquesta clases de processor y fetcher.

Uso:
  python main.py                          # Modo interactivo
  python main.py <prompt>                 # Ejecutar un prompt único
"""

import json
import os
import sys
from typing import Dict, Any

# Asegurar que el directorio actual está en sys.path
sys.path.insert(0, os.path.dirname(__file__))

from processor import TextProcessor, QueryBuilder, HTMLExtractor, FactConsolidator, generate_response
from fetcher import Fetcher
from trainer import Trainer
from retriever import Retriever
import argparse
import pathlib
from feedback import add_feedback


class Crawler:
    """Orquestador principal del flujo de crawling."""
    
    def __init__(self):
        self.fetcher = Fetcher()
    
    def run(self, prompt: str) -> Dict[str, Any]:
        """Ejecuta un ciclo completo: procesar -> buscar -> extraer -> consolidar."""
        # 1. Procesar el prompt
        text_proc = TextProcessor(prompt)
        processed = text_proc.get_processed()
        keywords = processed.get('keywords', [])
        
        # 2. Buscar en base de conocimiento local primero
        fragments = []
        sources = []

        # Intentar búsqueda en base de conocimiento local
        kb_html = self.fetcher.search_knowledge_base(keywords)
        if kb_html:
            html = self.fetcher.clean_html_with_bs4(kb_html)
            extractor = HTMLExtractor()
            fr = extractor.extract_fragments(html)
            if fr:
                fragments.extend(fr)
                sources.append('Base de conocimiento local')

        # Si no encontramos nada en KB, intentar búsquedas externas (si requests está disponible)
        if not fragments:
            query_builder = QueryBuilder(processed)
            urls = query_builder.build_urls()
            for url in urls:
                html = self.fetcher.fetch(url)
                if html:
                    html = self.fetcher.clean_html_with_bs4(html)
                    extractor = HTMLExtractor()
                    fr = extractor.extract_fragments(html)
                    if fr:
                        fragments.extend(fr)
                        sources.append(url)

        # Si aún no hay fragments, generar fallback realista
        if not fragments:
            html = self.fetcher.generate_realistic_fallback(prompt, keywords)
            extractor = HTMLExtractor()
            fr = extractor.extract_fragments(html)
            fragments.extend(fr)
            sources = ['Base de datos de referencia (fallback)']
        
        # 3. Consolidar facts
        consolidator = FactConsolidator(processed)
        facts = consolidator.consolidate(fragments)
        
        # 4. Generar respuesta
        response = generate_response(prompt, processed, facts, sources)
        
        return {
            'prompt': prompt,
            'response': response
        }


def interactive_loop():
    """Inicia un bucle interactivo para pruebas."""
    crawler = Crawler()
    print('Modo interactivo. Escribe tu prompt o Ctrl-C para salir.')
    try:
        while True:
            prompt = input('\nPrompt> ').strip()
            if not prompt:
                print('Saliendo.')
                break
            result = crawler.run(prompt)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            # Preguntar feedback al usuario
            try:
                fb = input('¿Fue útil la respuesta? (y/n/skip) > ').strip().lower()
                if fb in ('y','s'):
                    add_feedback(prompt, result['response'], True)
                elif fb in ('n','no'):
                    add_feedback(prompt, result['response'], False)
            except Exception:
                pass
    except (KeyboardInterrupt, EOFError):
        print('\nInteracción terminada.')


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(description='Crawler CLI')
    parser.add_argument('prompt', nargs='*', help='Prompt a ejecutar')
    parser.add_argument('--train', action='store_true', help='Entrenar/crear el índice TF-IDF desde la KB local')
    parser.add_argument('--data-dir', default=str(pathlib.Path(__file__).parent / 'data'), help='Directorio para artefactos de índice')
    args = parser.parse_args()

    # Si se solicita entrenamiento, lanzar y salir
    if args.train:
        out = Trainer.train(output_dir=args.data_dir)
        print('Entrenamiento completado:', out)
        return

    crawler = Crawler()

    # Modo directo: ejecutar prompt(s)
    if args.prompt:
        prompt = ' '.join(args.prompt).strip()
        # Si existe índice, intentar usar retriever para obtener fragments más relevantes
        data_dir = args.data_dir
        try:
            retr = Retriever(data_dir=data_dir)
            # obtener HTML con los top-k docs
            html = retr.retrieve_as_html(prompt, topk=6)
            if html:
                # bypass normal KB and use retriever results inside Crawler.run
                # lo hacemos creando un crawler y reemplazando temporalmente la búsqueda por estos fragments
                # Simplificar: guardar temporalmente en fetcher.search_knowledge_base behaviour is unchanged,
                # pero aquí llamamos a Crawler.run que ya intenta KB y luego web; para mayor precisión, si existe html,
                # llamaremos directamente al extractor/consolidator/generate_response para retornar respuesta basada en índice.
                extractor = HTMLExtractor()
                fr = extractor.extract_fragments(html)
                # Generar procesado y consolidar
                text_proc = TextProcessor(prompt)
                processed = text_proc.get_processed()
                consolidator = FactConsolidator(processed)
                facts = consolidator.consolidate(fr)
                response = generate_response(prompt, processed, facts, ['Índice local'])
                result = {'prompt': prompt, 'response': response}
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return
        except Exception:
            # si no hay índice o falla, seguimos con flow normal
            pass

        # Sin índice o fallback -> ejecutar flujo normal
        result = crawler.run(prompt)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Modo interactivo
        interactive_loop()


if __name__ == '__main__':
    main()
