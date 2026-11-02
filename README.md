# TrendPilot: Local Agentic AI Assistant (Ollama)

AIRI Team PITB - AI Internship Task 2. A local agent that turns a topic into a full viral content plan
(idea, hook, caption, hashtags, reel script, title, thumbnail text, review) and saves it to a file.
No cloud API: runs on **Ollama + Gemma 3:4B**.

## Agent workflow
```
User input -> Plan -> Trend Idea Generator -> pick best angle -> Caption Writer -> Hashtag Generator
-> Reel Script Generator -> Title/Thumbnail Generator -> Content Reviewer
-> (rewrite caption if reviewer says IMPROVE) -> File Saver -> Memory Tool -> Final output
```
Every tool call is logged as `[Tool Called]: <name>`.

## Tools (8)
Trend Idea Generator, Caption Writer, Hashtag Generator, Reel Script Generator,
Title & Thumbnail Generator, Content Reviewer, File Saver (mandatory), Memory Tool (JSON).

## Setup
```bash
ollama --version
ollama pull gemma3:4b          # or llama3.2:3b / phi3:mini / qwen2.5:3b
pip install -r requirements.txt
# optional: use another model
#   Windows (PowerShell): $env:OLLAMA_MODEL="llama3.2:3b"
#   Linux/Mac:            export OLLAMA_MODEL=llama3.2:3b
```

## Run
| Demo | Command |
|------|---------|
| CLI | `python demo.py` |
| Streamlit | `streamlit run app/streamlit_app.py` |
| FastAPI | `uvicorn app.main:app --reload` then POST `/generate-content` at http://localhost:8000/docs |
| 10 tests | `python tests/run_tests.py` |
| PDF report | `python report/make_report.py` |

FastAPI example body:
```json
{"topic": "YOLOv8 helmet detection project", "platform": "LinkedIn",
 "tone": "professional and exciting", "output_type": "post and reel script"}
```

## Structure
```
app/ (main.py, agent.py, tools.py, memory.py, prompts.py, llm.py, streamlit_app.py)
outputs/ (generated_posts, generated_scripts, saved_results/memory.json)
tests/ (run_tests.py, test_cases.md)   screenshots/   report/   demo.py   requirements.txt
```

## Known limitations
Small local models can be generic, weak at humour, and sometimes ignore the output format; the parsers
have fallbacks. See the error analysis in `report/final_report.pdf`.
