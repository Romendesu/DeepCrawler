"""Scraper simple para poblar `crawler/data/scraped_docs.joblib` con texto limpio.

Respeta robots.txt y usa `requests` y `beautifulsoup4` si están disponibles.
Guardará una lista de documentos: {'id','url','text','title','source'}.
"""
import os
import time
from typing import List, Dict

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

import json
import pathlib
import urllib.robotparser as robotparser

def clean_text_from_html(html: str) -> str:
    if not html:
        return ''
    if BeautifulSoup:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script','style','nav','footer','header','aside','noscript']):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return ' '.join(text.split())
        except Exception:
            return html
    else:
        # fallback básico
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        return ' '.join(text.split())

def can_fetch(url: str, user_agent: str = '*') -> bool:
    try:
        p = robotparser.RobotFileParser()
        parsed = requests.utils.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        p.set_url(robots_url)
        p.read()
        return p.can_fetch(user_agent, url)
    except Exception:
        return True

def scrape_urls(urls: List[str], out_dir: str = 'data', delay: float = 1.0) -> List[Dict]:
    os.makedirs(out_dir, exist_ok=True)
    docs = []
    doc_id = 0
    for url in urls:
        if requests is None:
            break
        try:
            if not can_fetch(url):
                continue
            r = requests.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
            r.raise_for_status()
            html = r.text
            text = clean_text_from_html(html)
            title = ''
            if BeautifulSoup:
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    if soup.title:
                        title = soup.title.string or ''
                except Exception:
                    title = ''
            docs.append({'id': doc_id, 'url': url, 'title': title, 'text': text, 'source': url})
            doc_id += 1
            time.sleep(delay)
        except Exception:
            continue

    # persistir en JSON para compatibilidad (y joblib si se desea)
    out_path = pathlib.Path(out_dir) / 'scraped_docs.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    return docs


if __name__ == '__main__':
    import sys
    urls = sys.argv[1:]
    if not urls:
        print('Usage: scraper.py <url1> <url2> ...')
    else:
        out = scrape_urls(urls)
        print(f'Scraped {len(out)} docs')
