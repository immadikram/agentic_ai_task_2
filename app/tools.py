"""Agent tools. Each tool is a plain Python function the agent decides to call."""
import json
import re
from pathlib import Path

from .llm import ask_ollama
from . import prompts as P
from .memory import save_memory, memory_context

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def slugify(text: str, max_len: int = 40) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:max_len] or "output"


# ---- Tool 1: Trend Idea Generator ----
def trend_idea_generator(topic, platform, tone) -> list:
    raw = ask_ollama(P.TREND_IDEAS.format(topic=topic, platform=platform, tone=tone, memory=memory_context()))
    ideas = [re.sub(r"^\s*\d+[\.\)]\s*", "", l).strip() for l in raw.splitlines() if re.match(r"^\s*\d+[\.\)]", l)]
    return ideas[:5] or [raw.strip()]


# ---- helper used by the agent: pick best angle (reasoning step) ----
def select_best_angle(topic, platform, angles) -> dict:
    listing = "\n".join(f"{i+1}. {a}" for i, a in enumerate(angles))
    raw = ask_ollama(P.PICK_ANGLE.format(topic=topic, platform=platform, angles=listing), temperature=0.2)
    m = re.search(r"NUMBER:\s*(\d)", raw)
    idx = int(m.group(1)) - 1 if m and 0 < int(m.group(1)) <= len(angles) else 0
    a = re.search(r"AUDIENCE:\s*(.+)", raw)
    return {"angle": angles[idx], "audience": a.group(1).strip() if a else "Tech students and early-career professionals"}


# ---- Tool 2: Caption Writer ----
def caption_writer(topic, platform, tone, angle, audience, feedback="") -> dict:
    fb = f"Reviewer feedback to apply in this rewrite: {feedback}" if feedback else ""
    raw = ask_ollama(P.CAPTION.format(topic=topic, platform=platform, tone=tone, angle=angle,
                                      audience=audience, rules=P.rules_for(platform), feedback=fb))
    hook = re.search(r"HOOK:\s*(.+)", raw)
    cap = re.search(r"CAPTION:\s*(.+)", raw, re.S)
    caption = cap.group(1).strip() if cap else raw.strip()
    caption = re.sub(r"(#\w+\s*)+$", "", caption).strip()  # strip trailing hashtags
    hook_text = hook.group(1).strip() if hook else caption.split("\n")[0]
    return {"hook": hook_text, "caption": caption}


# ---- Tool 3: Hashtag Generator ----
def hashtag_generator(topic, platform, caption) -> list:
    raw = ask_ollama(P.HASHTAGS.format(topic=topic, platform=platform, caption=caption[:500],
                                       rules=P.rules_for(platform)), temperature=0.3)
    tags, seen = [], set()
    for t in re.findall(r"#\w+", raw):
        if t.lower() not in seen:
            seen.add(t.lower())
            tags.append(t)
    return tags[:10] or ["#AI", "#Tech"]


# ---- Tool 4: Reel Script Generator ----
def reel_script_generator(topic, platform, tone, hook) -> str:
    return ask_ollama(P.REEL.format(topic=topic, platform=platform, tone=tone, hook=hook))


# ---- Tool 5: Title & Thumbnail Text ----
def title_thumbnail_generator(topic, platform, tone) -> dict:
    raw = ask_ollama(P.TITLE_THUMB.format(topic=topic, platform=platform, tone=tone), temperature=0.8)
    t = re.search(r"TITLE:\s*(.+)", raw)
    th = re.search(r"THUMBNAIL:\s*(.+)", raw)
    return {"title": t.group(1).strip() if t else topic, "thumbnail": th.group(1).strip() if th else topic[:30]}


# ---- Tool 6: Content Reviewer ----
def content_reviewer(platform, tone, hook, caption, hashtags) -> dict:
    raw = ask_ollama(P.REVIEW.format(platform=platform, tone=tone, rules=P.rules_for(platform), hook=hook,
                                     caption=caption, hashtags=" ".join(hashtags)), temperature=0.2)
    s = re.search(r"SCORE:\s*(\d+)", raw)
    v = re.search(r"VERDICT:\s*(GOOD|IMPROVE)", raw, re.I)
    c = re.search(r"COMMENTS:\s*(.+)", raw, re.S)
    return {"score": int(s.group(1)) if s else None,
            "verdict": v.group(1).upper() if v else "IMPROVE",
            "comments": c.group(1).strip() if c else raw.strip()}


# ---- Tool 7: Memory Tool ----
def memory_tool(result: dict) -> None:
    save_memory({k: result.get(k) for k in ("topic", "platform", "tone", "output_type", "hook", "saved_file")})


# ---- Tool 8: File Saver (mandatory) ----
def file_saver(result: dict, fmt: str = "md") -> str:
    slug = slugify(result["topic"])
    plat = slugify(result["platform"], 12)
    folder = "generated_scripts" if result.get("reel_script") and not result.get("caption") else "generated_posts"
    out_dir = OUTPUT_DIR / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slug}_{plat}.{fmt}"
    if fmt == "json":
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        lines = [f"# {result.get('title') or result['topic']}", "",
                 f"**Topic:** {result['topic']}  ", f"**Platform:** {result['platform']}  ",
                 f"**Tone:** {result['tone']}", "", "## Content Idea", result.get("content_idea", ""), "",
                 "## Hook", result.get("hook", ""), ""]
        if result.get("caption"):
            lines += ["## Caption", result["caption"], ""]
        if result.get("hashtags"):
            lines += ["## Hashtags", " ".join(result["hashtags"]), ""]
        if result.get("reel_script"):
            lines += ["## Reel Script", result["reel_script"], ""]
        if result.get("thumbnail"):
            lines += ["## Thumbnail Text", result["thumbnail"], ""]
        lines += ["## Review", f"Score: {result.get('review', {}).get('score')}/10",
                  result.get("review", {}).get("comments", ""), ""]
        path.write_text("\n".join(lines), encoding="utf-8")
    return str(path.relative_to(OUTPUT_DIR.parent))


TOOLS = {
    "Trend Idea Generator": trend_idea_generator,
    "Caption Writer": caption_writer,
    "Hashtag Generator": hashtag_generator,
    "Reel Script Generator": reel_script_generator,
    "Title & Thumbnail Generator": title_thumbnail_generator,
    "Content Reviewer": content_reviewer,
    "File Saver": file_saver,
    "Memory Tool": memory_tool,
}
