from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import EvaluationGenerateRequest
from app.services.evaluation_generator import generate_evaluation


router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/generate")
def generate(payload: EvaluationGenerateRequest, db: Session = Depends(get_db)):
    return generate_evaluation(
        area=payload.area,
        country=payload.country,
        exam_reference=payload.exam_reference,
        difficulty=payload.difficulty,
        number_of_questions=payload.number_of_questions,
        topic=payload.topic,
        db=db,
    )
