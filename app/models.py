import enum, hashlib
from datetime import datetime, timezone
from sqlalchemy import String, Text, Enum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# ----------------- ENUMS -----------------
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"

class NoteStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

# ----------------- MODELS -----------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.AGENT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ilişkiler
    notes: Mapped[list["Note"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    raw_text: Mapped[str] = mapped_column(Text)
    raw_text_sha256: Mapped[str] = mapped_column(String(64))  # idempotency için
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[NoteStatus] = mapped_column(
        Enum(NoteStatus), default=NoteStatus.QUEUED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(back_populates="notes")

    __table_args__ = (
        UniqueConstraint("user_id", "raw_text_sha256", name="uq_user_note_hash"),
    )

    @staticmethod
    def hash_text(txt: str) -> str:
        """Metnin SHA-256 hash’ini döndür (idempotency için)."""
        return hashlib.sha256(txt.encode("utf-8")).hexdigest()
