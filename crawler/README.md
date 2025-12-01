Nuevo Crawler - minimal
=======================

Este crawler es una implementación mínima, sin uso de modelos LLM, pensada para pruebas locales.

Características principales
- Siempre retorna JSON con la forma: `{ "prompt": "...", "response": { ... } }`.
- Interactivo: ejecuta `python main.py` y escribe prompts en la consola.
- Procesamiento de texto con regex para extraer keywords y entidades simples.
- Búsqueda gratuita e ilimitada: intenta hacer scraping simple de páginas públicas (DuckDuckGo HTML) si `requests` está instalado; si no, devuelve contenido simulado de ejemplo.
- No usa modelos IA pre-entrenados.

Uso
-----
Desde la carpeta `crawler`:
```pwsh
python main.py
```
o para ejecutar un prompt directamente:
```pwsh
python main.py dame un resumen sobre la economía en 2025
```

La salida es JSON impreso en consola.

Advertencias
-----------
- Respeta `robots.txt` y términos de uso cuando realices scraping real.
- Para mejores resultados instala `requests`:
```pwsh
python -m pip install requests
```

Extensiones posibles
- Añadir parsing HTML más robusto con `beautifulsoup4`.
- Añadir caching y retrasos entre peticiones para respetar sitios.
- Integrar APIs de búsqueda pagadas si necesitas resultados más completos.
DeepCrawler — Crawler microservicio (módulo `crawler/`)

Resumen
- Este módulo implementa un flujo sencillo: tokenizar la consulta del usuario, buscar contenido web y procesarlo para extraer y resumir información.
- Está diseñado para ejecutarse en entornos de desarrollo incluso si falta alguna dependencia pesada (spaCy, requests, bs4, transformers). En esos casos usa fallbacks basados en reglas y HTML de ejemplo.

Archivos principales
- `main.py`: punto de entrada para ejecutar el microservicio con una consulta de ejemplo.
- `tokenizer.py`: tokenizador y extractor de keywords y tópicos generales. Ahora maneja cualquier tema (política, fútbol, educación, ciencia, tecnología, salud, economía, cultura, etc.).
- `fetcher.py`: construye consultas de búsqueda (usa DuckDuckGo HTML) y obtiene HTML. Si `requests` no está disponible o falla, devuelve un HTML de fallback para pruebas.
- `crawler_processor.py`: extrae texto del HTML, valida fragmentos relevantes y genera un resumen. Intenta usar `transformers` si está instalado; si no, usa una heurística para resumir.

Instalación recomendada (opcional)
1. Crear un entorno virtual (recomendado):
```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Actualizar `pip` e instalar dependencias:
```pwsh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download es_core_news_sm
```
DeepCrawler - Simple CLI Crawler

Uso rápido

- Ejecutar en modo interactivo:
	```pwsh
	python crawler\main.py
	```
	Escribe un prompt y recibirás un objeto JSON con `prompt` y `response`.

- Ejecutar con prompt directo:
	```pwsh
	python crawler\main.py últimas noticias sobre ciencia
	```

Características

- Salida JSON con formato: `{ "prompt": ..., "response": { "query","intent","topics","keywords","validated_facts","summary","source_urls" } }`.
- Procesamiento de texto basado en regex (no requiere spaCy).
- Búsqueda "gratis": intenta usar HTTP GET para obtener HTML (requiere `requests`), y si no hay red o `requests` no está instalado devuelve contenido simulado.
- No usa modelos LLM.

Notas y recomendaciones

- Para búsquedas reales instala `requests`:
	```pwsh
	python -m pip install -r crawler\requirements.txt
	```
- Respeta `robots.txt` y límites de cada sitio cuando uses scraping real.

Limitaciones

- El parser HTML es simple (regex) y puede fallar en páginas con JS o estructuras complejas. Para mejorar, instala `beautifulsoup4`.
- Este script es para pruebas y prototipos.
