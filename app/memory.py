"""Simple JSON memory: remembers previous topics, platforms, tones and outputs."""
import json
from datetime import datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parent.parent / "outputs" / "saved_results" / "memory.json"


def _load() -> list:
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def save_memory(entry: dict) -> None:
    data = _load()
    entry = {**entry, "timestamp": datetime.now().isoformat(timespec="seconds")}
    data.append(entry)
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_recent(n: int = 3) -> list:
    return _load()[-n:]


def memory_context(n: int = 3) -> str:
    """Short text block injected into prompts so the agent 'remembers' past work."""
    recent = get_recent(n)
    if not recent:
        return ""
    lines = [f"- topic: {m.get('topic')} | platform: {m.get('platform')} | tone: {m.get('tone')}" for m in recent]
    return "Previous user requests (avoid repeating the same angles):\n" + "\n".join(lines)
