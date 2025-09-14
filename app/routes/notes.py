from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from app.database import get_db
from app import models, schemas, auth
from app.services.summarizer import process_note

router = APIRouter(prefix="/notes", tags=["Notes"])

# ---------- CREATE NOTE ----------
@router.post("", response_model=schemas.NoteOut, status_code=201)
def create_note(
    payload: schemas.NoteCreateIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    # idempotency: aynı user + aynı text varsa -> mevcut kaydı döndür
    raw_hash = models.Note.hash_text(payload.raw_text)
    existing = db.execute(
        select(models.Note).where(
            models.Note.user_id == user.id,
            models.Note.raw_text_sha256 == raw_hash
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    # yeni note oluştur
    note = models.Note(
        user_id=user.id,
        raw_text=payload.raw_text,
        raw_text_sha256=raw_hash,
        status=models.NoteStatus.QUEUED,
    )
    db.add(note); db.commit(); db.refresh(note)

    # background task başlat
    background_tasks.add_task(process_note, note.id)

    return note


# ---------- GET NOTE BY ID ----------
@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # erişim kontrolü
    if user.role != models.UserRole.ADMIN and note.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return note


# ---------- LIST NOTES ----------
@router.get("", response_model=list[schemas.NoteOut])
def list_notes(
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    stmt = select(models.Note)
    if user.role != models.UserRole.ADMIN:
        stmt = stmt.where(models.Note.user_id == user.id)

    return db.execute(stmt).scalars().all()


# ---------- UPDATE NOTE ----------
@router.put("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    payload: schemas.NoteCreateIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # erişim kontrolü
    if user.role != models.UserRole.ADMIN and note.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # notu güncelle
    note.raw_text = payload.raw_text
    note.raw_text_sha256 = models.Note.hash_text(payload.raw_text)
    note.summary = None                       
    note.status = models.NoteStatus.QUEUED    
    note.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(note)

    # yeni özet için background task çalıştır
    background_tasks.add_task(process_note, note.id)

    return note


# ---------- DELETE NOTE ----------
@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(auth.get_current_user),
):
    note = db.get(models.Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if user.role != models.UserRole.ADMIN and note.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(note)
    db.commit()
    return None
