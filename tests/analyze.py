"""Reads the FIRST test run, drafts report/error_analysis.json (5 rows) and applies prompt fixes.
Run once, after the first `python tests/run_tests.py`:   python tests/analyze.py
Then run `python tests/run_tests.py` again to see the improvement."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tests"

INFO = {  # type: (problem, reason, fix text, code appended to prompts.py)
 "error": ("Test failed to run", "Ollama not running / model too large / timeout", "Restarted Ollama and re-ran the test", ""),
 "missing": ("A required section came out empty", "Small model ignored the HOOK:/CAPTION: output format",
             "Added a strict format reminder to the CAPTION prompt",
             'CAPTION += "\\nYou MUST reply with both lines: HOOK: and CAPTION: exactly as shown above."'),
 "x_length": ("Post too long for X/Twitter", "Prompt had no hard character limit",
              "Set a hard 250-character limit for X/Twitter in the platform rules and caption prompt",
              'PLATFORM_RULES["x/twitter"] = "HARD LIMIT 250 characters including spaces. One idea only. 2 hashtags."\n'
              'PLATFORM_RULES["twitter"] = PLATFORM_RULES["x/twitter"]\n'
              'CAPTION += "\\nIf the platform is X/Twitter the entire caption must be under 250 characters."'),
 "reel_long": ("Reel script too long", "Word limit (80) was too loose for a 30-second video",
               "Tightened the word limit to 60 words and 12 words per voiceover line",
               'REEL = REEL.replace("under 80 spoken words", "under 60 spoken words, max 12 words per voiceover line")'),
 "hashtags": ("Too many / no hashtags", "Hashtag prompt did not enforce the count or relevance",
              "Added relevance rule and count limits to the hashtag prompt",
              'HASHTAGS += "\\nUse only hashtags directly related to the topic. Never use generic tags like #love or #instagood. Obey the hashtag count in the platform rules."'),
 "humor_weak": ("Humor / meme style not convincing", "Model did not understand meme style from a tone word alone",
                "Added a humor instruction with an example to the caption and reel prompts",
                'CAPTION += "\\nIf the tone is funny, humorous or meme style: use a relatable developer joke with a clear punchline, short sentences and one playful emoji. Example: My model: 99% accuracy in the notebook. Production: exists."\n'
                'REEL += "\\nIf the tone is funny or meme style, make the final scene a punchline."'),
 "reviewer_flag": ("Output was generic on the first draft", "Prompt did not ask for specific details",
                   "Asked for specific details in angles and relied on the reviewer rewrite loop",
                   'TREND_IDEAS += "\\nEach angle must include a specific detail, number or personal experience. Avoid generic advice."'),
}

res = json.loads((T / "test_results_run1.json").read_text(encoding="utf-8"))
rows, used_cases, used_types = [], set(), set()


def add(r, typ, detail):
    p, reason, fix, _ = INFO[typ]
    rows.append({"test_case": f"{r['topic']} ({r['platform']}, {r['tone']})",
                 "problem": f"{p}: {detail}", "reason": reason, "fix": fix})
    used_cases.add(r["no"]); used_types.add(typ)


for pass_no in (1, 2):                      # pass 1: one row per issue type; pass 2: fill up to 5
    for r in res:
        for typ, detail in r["issues"]:
            if len(rows) >= 5: break
            if r["no"] in used_cases: continue
            if pass_no == 1 and typ in used_types: continue
            add(r, typ, detail); break
for r in sorted(res, key=lambda x: (x["review"] or {}).get("score") or 10):   # pad with lowest scores
    if len(rows) >= 5: break
    if r["no"] not in used_cases:
        add(r, "reviewer_flag", f"lowest reviewer score {(r['review'] or {}).get('score')}/10")

(ROOT / "report" / "error_analysis.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

pf = ROOT / "app" / "prompts.py"
src = pf.read_text(encoding="utf-8")
for typ in used_types:
    code, marker = INFO[typ][3], f"# FIX:{typ}"
    if code and marker not in src:
        src += f"\n\n{marker}\n{code}\n"
        print(f"Applied prompt fix: {typ}")
pf.write_text(src, encoding="utf-8")
print(f"\nWrote {len(rows)} rows to report/error_analysis.json. Now run:  python tests/run_tests.py  (second run, after fixes)")
