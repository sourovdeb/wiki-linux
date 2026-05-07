#!/usr/bin/env python3
"""
server.py — Wiki Automator local server.
FastAPI backend for the Chrome extension.

Start: python server.py
Port:  7070
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from email_batch import run_email_batch
from social_post import run_social_post
from activity_learner import analyse_recordings, save_recording
from session_store import save_session_cookies
from llm_helper import rewrite_with_ollama

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("automator")

app = FastAPI(title="Wiki Automator", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_DIR = Path(__file__).parent.parent / "recordings"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job tracker
_jobs: dict[str, dict] = {}


# ── Models ────────────────────────────────────────────────────────────────────

class SessionPayload(BaseModel):
    platform: str
    cookies: list[dict]
    captured_at: str


class RecordingPayload(BaseModel):
    platform: str
    url: str
    started: str
    actions: list[dict]
    ended: str | None = None
    partial: bool = False


class JobRequest(BaseModel):
    type: str  # "email_batch" | "social_post"
    # email_batch fields
    rows: list[dict] | None = None
    provider: str = "gmail"
    ai_model: str = "none"
    dry_run: bool = True
    # social_post fields
    platforms: list[str] | None = None
    title: str = ""
    content: str = ""
    ai_rewrite: bool = False


class AnalyseRequest(BaseModel):
    recordings: list[dict]


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ── Sessions ──────────────────────────────────────────────────────────────────

@app.post("/api/sessions/save")
async def save_session(payload: SessionPayload):
    save_session_cookies(payload.platform, payload.cookies)
    log.info("Session saved: %s (%d cookies)", payload.platform, len(payload.cookies))
    return {"ok": True}


# ── Recordings ────────────────────────────────────────────────────────────────

@app.post("/api/recordings/save")
async def save_recording_endpoint(payload: RecordingPayload):
    save_recording(payload.dict())
    return {"ok": True}


# ── Jobs ──────────────────────────────────────────────────────────────────────

@app.post("/api/jobs/run")
async def run_job(req: JobRequest):
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status": "queued", "done": 0, "total": 0, "failed": 0, "started": datetime.now().isoformat()}

    async def _run():
        try:
            if req.type == "email_batch":
                _jobs[job_id]["total"] = len(req.rows or [])
                await run_email_batch(
                    rows=req.rows or [],
                    provider=req.provider,
                    ai_model=req.ai_model,
                    dry_run=req.dry_run,
                    job=_jobs[job_id],
                )
            elif req.type == "social_post":
                _jobs[job_id]["total"] = len(req.platforms or [])
                content = req.content
                if req.ai_rewrite and content:
                    content = await rewrite_with_ollama(content, style="professional social media post")
                await run_social_post(
                    platforms=req.platforms or [],
                    title=req.title,
                    content=content,
                    job=_jobs[job_id],
                )
            _jobs[job_id]["status"] = "done"
        except Exception as e:
            log.exception("Job %s failed", job_id)
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = str(e)

    asyncio.create_task(_run())
    return {"job_id": job_id}


@app.get("/api/jobs/status/{job_id}")
def job_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


# ── Learn ─────────────────────────────────────────────────────────────────────

@app.post("/api/learn/analyse")
async def learn_analyse(req: AnalyseRequest):
    insights = await analyse_recordings(req.recordings)
    return {"insights": insights}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7070, log_level="info")
