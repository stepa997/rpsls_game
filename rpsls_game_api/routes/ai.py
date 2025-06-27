import os
import uuid

from fastapi import APIRouter
from fastapi import Query
from gtts import gTTS

from schemas.models import SpeakRequest

router = APIRouter()


@router.post("/speak")
def speak(req: SpeakRequest):
    filename = f"static/speech_{uuid.uuid4().hex}.mp3"
    tts = gTTS(req.text[:200])
    tts.save(filename)
    return {"url": f"/{filename}"}


@router.delete("/speak")
def delete_speech_file(filename: str = Query(...)):
    filename = filename.lstrip("/")
    if filename.startswith("static/") and filename.endswith(".mp3"):
        try:
            os.remove(filename)
            return {"status": "deleted"}
        except FileNotFoundError:
            return {"status": "not found"}
    return {"status": "invalid filename"}
