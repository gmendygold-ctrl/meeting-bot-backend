from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

# Simple mémoire interne
MEETINGS = {}

class ScheduleMeetingRequest(BaseModel):
    meeting_url: str
    start_time: str
    duration_minutes: Optional[int] = None
    title: Optional[str] = None
    timezone: Optional[str] = "Africa/Dakar"

@app.post("/schedule_meeting")
def schedule_meeting(req: ScheduleMeetingRequest):
    meeting_id = str(uuid.uuid4())
    MEETINGS[meeting_id] = {
        "status": "scheduled",
        "title": req.title or "Réunion sans titre",
        "meeting_url": req.meeting_url,
        "start_time": req.start_time,
        "duration_minutes": req.duration_minutes,
        "timezone": req.timezone,
    }
    return {
        "meeting_id": meeting_id,
        "status": "scheduled"
    }

@app.get("/meeting_summary")
def meeting_summary(meeting_id: str):
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        return {
            "status": "failed",
            "error_message": "Réunion introuvable"
        }

    # À remplacer plus tard par le vrai résumé AI
    return {
        "status": "done",
        "title": meeting["title"],
        "summary_text": (
            f"Résumé automatique de la réunion '{meeting['title']}'. "
            "La logique de transcription n'est pas encore branchée."
        )
    }
