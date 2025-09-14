import time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models

def summarize_text(raw_text: str) -> str:
    """Stub summarizer: sadece ilk 200 karakteri döndürür."""
    return (raw_text[:200] + "...") if len(raw_text) > 200 else raw_text

def process_note(note_id: int):
    """Notu özetleme işini arka planda yapar."""
    db: Session = SessionLocal()
    try:
        note = db.get(models.Note, note_id)
        if not note:
            return

        # status -> PROCESSING
        note.status = models.NoteStatus.PROCESSING
        db.commit(); db.refresh(note)

        # gecikme simülasyonu
        time.sleep(2)

        # özet oluştur
        note.summary = summarize_text(note.raw_text)
        note.status = models.NoteStatus.DONE
        db.commit(); db.refresh(note)

    except Exception:
        note = db.get(models.Note, note_id)
        if note:
            note.status = models.NoteStatus.FAILED
            db.commit()
    finally:
        db.close()
