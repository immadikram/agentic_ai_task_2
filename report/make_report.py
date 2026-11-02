"""Builds report/final_report.pdf from your real test results + screenshots.
Run AFTER: python tests/run_tests.py  and after filling report/error_analysis.json
Usage (from project root): python report/make_report.py"""
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether)

ROOT = Path(__file__).resolve().parent.parent
MODEL = "Gemma 3:4B"          # <-- change if you used another model
YOUR_NAME = "Immad Ikram"       # <-- change

st = getSampleStyleSheet()
S, H1, H2 = st["BodyText"], st["Heading1"], st["Heading2"]
small = st["BodyText"].clone("small", fontSize=7.5, leading=9)


def P(t, s=S):
    return Paragraph(t, s)


def table(rows, widths):
    t = Table([[P(str(c), small) for c in r] for r in rows], colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe6f1")),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def shot(name, caption):
    p = ROOT / "screenshots" / name
    if not p.exists():
        return [P(f"<b>[MISSING SCREENSHOT: screenshots/{name}]</b> - {caption}")]
    img = Image(str(p)); r = min(15 * cm / img.imageWidth, 9 * cm / img.imageHeight)
    img.drawWidth, img.drawHeight = img.imageWidth * r, img.imageHeight * r
    return [KeepTogether([img, P(f"<i>{caption}</i>")]), Spacer(1, 8)]


story = [P("TrendPilot: A Local Agentic AI Assistant Using Ollama", st["Title"]),
         P(f"AIRI Team PITB - AI Internship Task 2<br/>Submitted by: {YOUR_NAME}<br/>Submitted to: Omar Farooq, Associate AI/ML Engineer"),
         Spacer(1, 12),
         P("1. Project Overview", H1),
         P(f"TrendPilot is a local agentic AI assistant built with Python and Ollama using the {MODEL} model. "
           "Given a topic, platform, tone and output type, it plans its work, calls eight tools, reviews its own output, "
           "rewrites the caption if needed, and saves the final result as a Markdown file. "
           "It solves the problem of turning a raw project idea into a platform-ready content plan "
           "(idea, hook, caption, hashtags, reel script, title and thumbnail text) without any cloud API."),
         P("2. Tools and Technologies", H1),
         P(f"Python, Ollama, {MODEL}, requests, JSON memory, Markdown file saving, FastAPI, Streamlit, CLI, ReportLab, GitHub."),
         P("3. Agent Workflow", H1),
         P("User input (topic, platform, tone, output type) &rarr; Agent builds a plan &rarr; Trend Idea Generator creates 5 angles "
           "&rarr; Agent picks the best angle and audience &rarr; Caption Writer &rarr; Hashtag Generator &rarr; Reel Script Generator "
           "&rarr; Title/Thumbnail Generator &rarr; Content Reviewer &rarr; (if verdict is IMPROVE or score &lt; 7) Caption Writer rewrites "
           "using the reviewer's feedback &rarr; File Saver &rarr; Memory Tool &rarr; final output. Every tool call is printed as "
           "[Tool Called]: name."),
         P("4. Tools Implemented", H1)]
tools = [("Trend Idea Generator", "Produces 5 specific content angles; uses memory to avoid repeating old angles."),
         ("Caption Writer", "Writes the hook and caption following platform rules; also used for the improvement rewrite."),
         ("Hashtag Generator", "Creates relevant hashtags, de-duplicated and limited per platform."),
         ("Reel Script Generator", "Writes a 4-scene, ~30 second script with visuals and voiceover."),
         ("Title & Thumbnail Generator", "Creates a catchy title and short thumbnail text."),
         ("Content Reviewer", "Scores the content 1-10 and checks hook, clarity, length, tone, hashtags."),
         ("File Saver", "Saves the final result to .md (or .json) in outputs/."),
         ("Memory Tool", "Stores previous topics, platforms, tones and saved files in memory.json.")]
story.append(table([["Tool", "What it does"]] + [list(t) for t in tools], [5 * cm, 12 * cm]))
story += [P("5. Demo and Outputs", H1),
          P("Demos: CLI (python demo.py), Streamlit (streamlit run app/streamlit_app.py) and FastAPI "
            "(uvicorn app.main:app, POST /generate-content). Generated files are in outputs/."), Spacer(1, 6)]
story += shot("ollama_running.png", "Figure 1: Ollama running the local model")
story += shot("demo_output.png", "Figure 2: Agent output in the demo")
story += shot("saved_file_output.png", "Figure 3: Saved Markdown output file")
story += [PageBreak(), P("6. Testing (10 test cases)", H1)]
rp = ROOT / "tests" / "test_results.json"
if rp.exists():
    res = json.loads(rp.read_text(encoding="utf-8"))
    rows = [["#", "Topic", "Platform", "Tone", "Tools used", "Score", "Saved file", "Useful?"]]
    for r in res:
        rows.append([r["no"], r["topic"], r["platform"], r["tone"], ", ".join(r["tools_used"]), (r.get("review") or {}).get("score"), r["saved_file"], r["useful"]])
    story.append(table(rows, [0.6*cm, 2.6*cm, 1.8*cm, 1.8*cm, 4.4*cm, 1*cm, 3*cm, 2.2*cm]))
    r1 = ROOT / "tests" / "test_results_run1.json"
    if r1.exists():
        before = sum(1 for r in json.loads(r1.read_text(encoding="utf-8")) if r["useful"] == "Yes")
        after = sum(1 for r in res if r["useful"] == "Yes")
        story += [Spacer(1, 6), P(f"<b>Automatic quality checks (length, hashtags, format, tone):</b> {before}/10 passed in the first run, "
                                  f"{after}/10 passed after the prompt fixes.")]
else:
    story.append(P("<b>[Run python tests/run_tests.py first]</b>"))
story += [Spacer(1, 10), P("7. Error Analysis", H1)]
ep = ROOT / "report" / "error_analysis.json"
if ep.exists():
    ea = json.loads(ep.read_text(encoding="utf-8"))
    story.append(table([["Test case", "Problem found", "Possible reason", "Fix applied"]] +
                       [[e["test_case"], e["problem"], e["reason"], e["fix"]] for e in ea], [3.5*cm, 4.5*cm, 4.5*cm, 4.5*cm]))
story += [Spacer(1, 10), P("Suggested improvements", H2),
          P("1) Add few-shot examples to prompts (especially humour / meme style). 2) Add validation checks (word count, "
            "character limit for X, hashtag count). 3) Add a user-feedback loop and a web-search tool. 4) Try a larger local model."),
          P("8. What I Learned", H1),
          P("- How to run local LLMs with Ollama<br/>- Difference between a chatbot and an agent<br/>- Connecting tools to an LLM<br/>"
            "- Prompt design for structured output<br/>- Saving results and basic memory<br/>- Testing and improving an agentic workflow"),
          P("9. Future Improvements", H1),
          P("Web search, multi-agent workflow (planner / writer / reviewer), voice input, PDF export, SQLite memory, user feedback loop.")]

SimpleDocTemplate(str(ROOT / "report" / "final_report.pdf"), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                  topMargin=2*cm, bottomMargin=2*cm).build(story)
print("Created report/final_report.pdf")
