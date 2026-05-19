from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registry_id: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str] = mapped_column(String(120), index=True, default="Latinoamérica")
    exam: Mapped[str] = mapped_column(String(120), index=True, default="No especificada")
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    year_range: Mapped[str] = mapped_column(String(80), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(255), default="")
    source_url: Mapped[str] = mapped_column(Text, default="")
    areas_json: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(60), default="procesado")
    public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    original_filename: Mapped[str] = mapped_column(String(255))
    raw_path: Mapped[str] = mapped_column(Text)
    processed_path: Mapped[str] = mapped_column(Text)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    column_count: Mapped[int] = mapped_column(Integer, default=0)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    columns: Mapped[list["DatasetColumn"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    dtype: Mapped[str] = mapped_column(String(80))
    null_count: Mapped[int] = mapped_column(Integer, default=0)
    non_null_count: Mapped[int] = mapped_column(Integer, default=0)
    sample_values: Mapped[str] = mapped_column(Text, default="[]")

    dataset: Mapped[Dataset] = relationship(back_populates="columns")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    source: Mapped[str] = mapped_column(String(255), default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    exam: Mapped[str] = mapped_column(String(120), default="")
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    document_type: Mapped[str] = mapped_column(String(120), default="metodologico")
    path: Mapped[str] = mapped_column(Text)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_message: Mapped[str] = mapped_column(Text)
    assistant_response: Mapped[str] = mapped_column(Text)
    sources: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GeneratedEvaluation(Base):
    __tablename__ = "generated_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    area: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(120))
    exam_reference: Mapped[str] = mapped_column(String(120))
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NormalizedResult(Base):
    __tablename__ = "normalized_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_registry_id: Mapped[str] = mapped_column(String(160), index=True)
    country: Mapped[str] = mapped_column(String(120), index=True)
    exam: Mapped[str] = mapped_column(String(120), index=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    student_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(160), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    age: Mapped[float | None] = mapped_column(Float, nullable=True)
    institution_type: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    socioeconomic_level: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    math_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reading_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    science_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    social_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    english_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    global_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_data_json: Mapped[str] = mapped_column(Text, default="{}")
