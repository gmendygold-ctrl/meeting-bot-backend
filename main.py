from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from uuid import uuid4
from datetime import datetime
from dateutil import parser as dateparser

app = FastAPI()

# ---- Modèles ----

class ScheduleMeetingRequest(BaseModel):
    meeting_url: str
    start_time: str  # ISO 8601
    duration_minutes: Optional[int] = None
    title: Optional[str] = None
    timezone: str = "Africa/Dakar"

class MarkMeetingStartedBody(BaseModel):
    meeting_id: str

# ---- Stockage en mémoire (simple dict pour l’instant) ----

MEETINGS: Dict[str, Dict] = {}


# ---- API ----

@app.post("/schedule_meeting")
def schedule_meeting(payload: ScheduleMeetingRequest):
    """Planifier une réunion (appelée par ton GPT)."""
    meeting_id = str(uuid4())
    data = payload.dict()

    # Normaliser l'heure si possible
    try:
        dt = dateparser.parse(data["start_time"])
        data["start_time"] = dt.isoformat()
    except Exception:
        pass

    data["status"] = "scheduled"  # important !
    data["created_at"] = datetime.utcnow().isoformat()

    MEETINGS[meeting_id] = data

    return {"meeting_id": meeting_id, "status": "scheduled"}


@app.get("/next_meeting_to_join")
def next_meeting_to_join():
    """
    Endpoint utilisé par le worker Render.
    Retourne la prochaine réunion avec status = 'scheduled'.
    """
    # Filtrer uniquement les réunions "scheduled"
    candidates = [
        {"id": mid, **meta}
        for mid, meta in MEETINGS.items()
        if meta.get("status") == "scheduled"
    ]

    if not candidates:
        return {"status": "none"}

    # Trier par start_time si possible
    def sort_key(m):
        try:
            return dateparser.parse(m["start_time"])
        except Exception:
            return datetime.max

    candidates.sort(key=sort_key)
    m = candidates[0]

    return {
        "status": "scheduled",
        "id": m["id"],
        "meeting_url": m["meeting_url"],
        "title": m.get("title"),
        "start_time": m.get("start_time"),
        "timezone": m.get("timezone"),
        "duration_minutes": m.get("duration_minutes"),
    }


@app.post("/mark_meeting_started")
def mark_meeting_started(body: MarkMeetingStartedBody):
    """
    Appelé par le worker juste après avoir choisi une réunion.
    Permet de passer la réunion en 'in_progress' pour qu’elle
    ne soit plus renvoyée par /next_meeting_to_join.
    """
    meeting = MEETINGS.get(body.meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion introuvable")

    meeting["status"] = "in_progress"
    return {"status": "in_progress"}


@app.get("/meeting_summary")
def meeting_summary(meeting_id: str):
    """
    Stub simple pour le moment : retourne un résumé fictif.
    Plus tard on branchera ici la vraie transcription.
    """
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Réunion introuvable")

    return {
        "status": "pending",
        "title": meeting.get("title"),
        "summary_text": None,
        "error_message": None,
    }
