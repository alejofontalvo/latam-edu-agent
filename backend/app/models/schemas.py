from typing import Any

from pydantic import BaseModel, Field


class DatasetColumnSchema(BaseModel):
    name: str
    dtype: str
    null_count: int
    non_null_count: int
    sample_values: list[Any] = []


class DatasetSchema(BaseModel):
    id: int
    registry_id: str
    name: str
    country: str
    exam: str
    year: int | None = None
    year_range: str = ""
    areas: list[str] = []
    status: str = "procesado"
    is_demo: bool = False
    original_filename: str
    row_count: int
    column_count: int
    created_at: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2)
    dataset_id: int | str | None = None
    use_rag: bool = True


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]] = []
    used_dataset: bool = False
    blocks: dict[str, Any] = {}
    chart: dict[str, Any] | None = None
    actions: list[str] = []


class AnalyticsQueryRequest(BaseModel):
    dataset_id: int | str | None = None
    metric: str | None = None
    operation: str = "mean"
    group_by: str | None = None
    filters: dict[str, Any] = {}
    percentile: float | None = None


class CompareRequest(BaseModel):
    metric: str = "global_score"
    dimension: str = "country"
    filters: dict[str, Any] = {}
    dataset_ids: list[int | str] = []


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = 5


class EvaluationGenerateRequest(BaseModel):
    area: str = "lectura critica"
    country: str = "Colombia"
    exam_reference: str = "Saber 11"
    difficulty: str = "media"
    number_of_questions: int = Field(default=5, ge=1, le=20)
    topic: str | None = None


class ExportResponse(BaseModel):
    dataset_id: int
    path: str
    rows: int


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
