from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import ChatHistory
from app.models.schemas import ChatRequest
from app.services.agent_orchestrator import AgentOrchestrator


router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    result = await AgentOrchestrator(db).receive_user_message(payload.message)
    db.add(
        ChatHistory(
            user_message=payload.message,
            assistant_response=result["answer"],
            sources=str(result.get("sources", [])),
        )
    )
    db.commit()
    return result
