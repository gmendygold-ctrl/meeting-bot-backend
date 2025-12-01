from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
from datetime import datetime, timezone
import dateutil.parser

app = FastAPI()

# Dictionnaire en mémoire pour stocker les réunions
MEETINGS: Dict[str, dict] = {}

class ScheduleMeetingRequest(BaseModel):
    meeting_url: str
    start_time: str   # ISO 8601
    duration_minutes: Optional[int] = None
    title: Optional[str] = None
    timezone: Optional[str] = "Africa/Dakar"

@app.post("/schedule_meeting")
def schedule_meeting(req: ScheduleMeetingRequest):
    meeting_id = str(uuid.uuid4())
    MEETINGS[meeting_id] = {
        "id": meeting_id,
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

    # Pour l’instant on renvoie un faux résumé
    return {
        "status": "done",
        "title": meeting["title"],
        "summary_text": (
            f"Résumé automatique de la réunion '{meeting['title']}'. "
            "La logique d'enregistrement et de transcription n'est pas encore branchée."
        )
    }

@app.get("/meetings_to_join")
def meetings_to_join():
    """
    Retourne les réunions qui doivent être rejointes maintenant ou dans quelques minutes.
    Version simple : renvoie toutes les réunions 'scheduled'.
    Tu pourras filtrer côté bot.
    """
    return list(MEETINGS.values())
