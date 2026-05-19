from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import AnalyticsQueryRequest, CompareRequest
from app.services.analytics_engine import AnalyticsEngine
from app.services.analytics_service import compare_groups, get_basic_statistics, get_global_kpis, query_statistics


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/auto")
def analytics_auto(payload: dict, db: Session = Depends(get_db)):
    return AnalyticsEngine(db).analyze_user_query(payload.get("query", "Analiza los datos disponibles"))


@router.post("/overview")
def analytics_overview(payload: dict | None = None, db: Session = Depends(get_db)):
    return AnalyticsEngine(db).get_general_overview((payload or {}).get("query", ""))


@router.post("/trends")
def analytics_trends(payload: dict | None = None, db: Session = Depends(get_db)):
    return AnalyticsEngine(db).analyze_trends((payload or {}).get("query", ""))


@router.post("/gaps")
def analytics_gaps(payload: dict | None = None, db: Session = Depends(get_db)):
    return AnalyticsEngine(db).analyze_gaps((payload or {}).get("query", ""))


@router.post("/chart")
def analytics_chart(payload: dict, db: Session = Depends(get_db)):
    return AnalyticsEngine(db).generate_chart_payload(payload.get("query", "Genera una gráfica"))


@router.get("/basic/{dataset_id}")
def basic_statistics(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return get_basic_statistics(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    return get_global_kpis(db)


@router.post("/query")
def analytics_query(payload: AnalyticsQueryRequest, db: Session = Depends(get_db)):
    try:
        return query_statistics(
            dataset_id=payload.dataset_id,
            metric=payload.metric,
            operation=payload.operation,
            group_by=payload.group_by,
            filters=payload.filters,
            percentile=payload.percentile,
            db=db,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/compare")
def analytics_compare(payload: CompareRequest, db: Session = Depends(get_db)):
    try:
        return compare_groups(
            metric=payload.metric,
            dimension=payload.dimension,
            filters=payload.filters,
            dataset_ids=payload.dataset_ids,
            db=db,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
