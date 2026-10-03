import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

def utc_now():
    return datetime.now(timezone.utc)

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    auth_subject: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    requests: Mapped[List["GenerationRequestModel"]] = relationship("GenerationRequestModel", back_populates="user")


class GenerationRequestModel(Base):
    __tablename__ = "generation_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    style_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="queued", index=True, nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quality: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="requests")
    assets: Mapped[List["ImageAssetModel"]] = relationship("ImageAssetModel", back_populates="request", cascade="all, delete-orphan")
    quality_check: Mapped[Optional["QualityCheckModel"]] = relationship(
        "QualityCheckModel", uselist=False, cascade="all, delete-orphan")
    selections: Mapped[List["GenerationSelectionModel"]] = relationship(
        "GenerationSelectionModel", cascade="all, delete-orphan")

class ImageAssetModel(Base):
    __tablename__ = "image_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("generation_requests.id"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'target', 'reference', 'result'
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    request: Mapped["GenerationRequestModel"] = relationship("GenerationRequestModel", back_populates="assets")

class ConsentRecordModel(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("generation_requests.id"), nullable=True)
    consent_version: Mapped[str] = mapped_column(String(50), nullable=False)
    consented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class UsageEventModel(Base):
    __tablename__ = "usage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("generation_requests.id"), nullable=False)
    provider_status: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class QualityCheckModel(Base):
    """AI accuracy score of a generated result (a separate table so existing databases need no migration)."""
    __tablename__ = "quality_checks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("generation_requests.id"), unique=True, index=True, nullable=False)
    overall: Mapped[int] = mapped_column(Integer, nullable=False)
    scores_json: Mapped[str] = mapped_column(Text, nullable=False)
    issues_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class StyleTemplateModel(Base):
    """A catalogue template (hairstyle, hair colour, makeup, beard, nails or a look preset).

    Metadata that varies by category (face-shape tags, lengths, undertones, images...) lives in data_json.
    """
    __tablename__ = "style_templates"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    catalog_group: Mapped[str] = mapped_column(String(10), index=True, nullable=False)  # women | men | all
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False, default="draft")  # draft | published | archived
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    featured: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    data_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class GenerationSelectionModel(Base):
    """What a try-on applied to each area: a catalogue template (with its version), a custom style or the reference photo."""
    __tablename__ = "generation_selections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("generation_requests.id"), index=True, nullable=False)
    area: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)  # template | custom | reference
    template_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, index=True)
    template_version: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    intensity: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
