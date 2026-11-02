"""FastAPI demo.  Run from project root:  uvicorn app.main:app --reload
Docs UI: http://localhost:8000/docs"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agent import TrendPilotAgent

app = FastAPI(title="TrendPilot - Local Agentic AI")


class Req(BaseModel):
    topic: str
    platform: str = "LinkedIn"
    tone: str = "professional and exciting"
    output_type: str = "post and reel script"


@app.post("/generate-content")
def generate_content(req: Req):
    try:
        r = TrendPilotAgent(logger=print).run(req.topic, req.platform, req.tone, req.output_type)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"hook": r["hook"], "caption": r["caption"], "hashtags": r["hashtags"],
            "reel_script": r.get("reel_script", ""), "title": r.get("title"),
            "thumbnail": r.get("thumbnail"), "review": r["review"],
            "tools_used": r["tools_used"], "saved_file": r["saved_file"]}
