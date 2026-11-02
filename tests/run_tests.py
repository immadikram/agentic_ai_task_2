"""Runs the 10 required test cases, saves outputs, auto-checks them, writes tests/test_cases.md.
Run from project root:  python tests/run_tests.py"""
import json, shutil, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tests"))
from app.agent import TrendPilotAgent
from checks import check

CASES = [
    ("YOLOv8 helmet detection", "LinkedIn", "Professional", "Post"),
    ("AI internship experience", "LinkedIn", "Motivational", "Post"),
    ("Python learning journey", "Instagram", "Funny", "Reel Script"),
    ("Machine learning project", "X/Twitter", "Short and catchy", "Post"),
    ("Data annotation struggles", "LinkedIn", "Humorous", "Post"),
    ("Model failed in production", "Instagram", "Meme style", "Reel Script"),
    ("Final year project", "LinkedIn", "Professional", "Post + Reel Script"),
    ("Computer vision project", "YouTube Shorts", "Exciting", "Reel Script"),
    ("Debugging FastAPI", "X/Twitter", "Funny", "Post"),
    ("Open-source contribution", "LinkedIn", "Inspirational", "Post"),
]

results = []
for i, (topic, plat, tone, out) in enumerate(CASES, 1):
    print(f"\n##### TEST {i}/10: {topic} ({plat}) #####")
    t0 = time.time()
    row = {"no": i, "topic": topic, "platform": plat, "tone": tone, "output_type": out}
    try:
        r = TrendPilotAgent().run(topic, plat, tone, out)
        row.update(tools_used=r["tools_used"], saved_file=r["saved_file"], hook=r["hook"],
                   caption=r.get("caption", ""), hashtags=r.get("hashtags", []),
                   reel_script=r.get("reel_script", ""), review=r["review"],
                   improved=r["improved"], seconds=round(time.time() - t0, 1))
    except Exception as e:
        row.update(tools_used=[], saved_file="-", error=str(e), review={}, improved=False)
    row["issues"] = check(row)
    row["useful"] = "Yes" if not [x for x in row["issues"] if x[0] != "reviewer_flag"] else \
                    "No - " + row["issues"][0][1][:70]
    results.append(row)

T = ROOT / "tests"
(T / "test_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
if not (T / "test_results_run1.json").exists():      # keep the FIRST run (before prompt fixes) for before/after
    shutil.copy(T / "test_results.json", T / "test_results_run1.json")

md = ["# Test Cases & Results", "",
      "| # | Topic | Platform | Tone | Output | Tools used | Reviewer score | Saved file | Useful? |",
      "|---|-------|----------|------|--------|-----------|---------------|-----------|---------|"]
for r in results:
    md.append(f"| {r['no']} | {r['topic']} | {r['platform']} | {r['tone']} | {r['output_type']} | "
              f"{', '.join(r['tools_used'])} | {r['review'].get('score')} | {r['saved_file']} | {r['useful']} |")
(T / "test_cases.md").write_text("\n".join(md), encoding="utf-8")
ok = sum(1 for r in results if r["useful"] == "Yes")
print(f"\nDone. {ok}/10 passed the automatic checks. See tests/test_cases.md")
