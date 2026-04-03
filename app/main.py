from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from app.tasks import process_audio_task
import os

app = FastAPI(title="Call Centre Analytics API")

API_KEY = os.environ.get("API_KEY", "sk_track3_987654321")

class CallAnalyticsRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str

@app.post("/api/call-analytics")
async def analyze_call(request: CallAnalyticsRequest, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if not request.audioBase64:
        raise HTTPException(status_code=400, detail="Missing audioBase64")
    
    # Running synchronously for local testing without Redis
    result = process_audio_task(request.language, request.audioFormat, request.audioBase64)
    return result
