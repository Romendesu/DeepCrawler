"""Módulo simple para almacenar feedback del usuario y permitir re-entrenar.
Guarda feedback en `crawler/data/feedback.json`.
"""
import json
import os
from typing import Dict, Any

FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), 'data', 'feedback.json')

def add_feedback(prompt: str, response: Dict[str, Any], useful: bool) -> None:
    os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
    entry = {'prompt': prompt, 'response': response, 'useful': bool(useful)}
    try:
        if os.path.exists(FEEDBACK_PATH):
            with open(FEEDBACK_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []
    data.append(entry)
    with open(FEEDBACK_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_feedback() -> Any:
    try:
        with open(FEEDBACK_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []
