"""Thin wrapper around the local Ollama API."""
import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")


def ask_ollama(prompt: str, model: str = None, temperature: float = 0.7) -> str:
    """Send a prompt to the local Ollama server and return the text reply."""
    if os.getenv("TRENDPILOT_MOCK") == "1":  # only for testing code without Ollama
        return "1. Mock idea one\n2. Mock idea two\n3. Mock idea three\n4. Mock idea four\n5. Mock idea five\nNUMBER: 2\nAUDIENCE: Students\nHOOK: Mock hook\nCAPTION: Mock caption.\nTITLE: Mock title\nTHUMBNAIL: Mock thumb\nSCORE: 6\nVERDICT: IMPROVE\nCOMMENTS: - add a metric\n#AI #Python #Mock"
    payload = {
        "model": model or MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=300)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot reach Ollama. Is it running? Try: `ollama serve`")
    return r.json()["response"].strip()
