from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.services.analytics_engine import AnalyticsEngine
from app.services.dataset_catalog_service import DatasetCatalogService
from app.services.evaluation_generator import generate_evaluation
from app.services.llm_service import call_llm
from app.services.rag_service import retrieve_context


class AgentOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.catalog = DatasetCatalogService(db)
        self.analytics = AnalyticsEngine(db)

    def classify_intent(self, message: str) -> str:
        lowered = message.lower()
        if any(token in lowered for token in ["evaluación", "evaluacion", "preguntas", "examen tipo", "crear evaluación"]):
            return "evaluation"
        if any(token in lowered for token in ["metodolog", "qué es", "que es", "define", "documento", "fuente"]):
            return "methodology"
        if any(token in lowered for token in ["reporte", "power bi", "powerbi"]):
            return "report"
        return self.analytics.classify_query(message)

    def inspect_available_data(self) -> dict[str, Any]:
        return self.catalog.get_dataset_catalog()

    def build_analysis_plan(self, message: str, intent: str) -> dict[str, Any]:
        return {
            "intent": intent,
            "needs_analytics": intent in {"overview", "comparison", "ranking", "trend", "gap", "chart", "report"},
            "needs_rag": intent == "methodology" or any(token in message.lower() for token in ["metodolog", "escala", "interpretar", "pisa", "saber", "enem"]),
            "needs_evaluation": intent == "evaluation",
        }

    async def receive_user_message(self, message: str) -> dict[str, Any]:
        intent = self.classify_intent(message)
        catalog = self.inspect_available_data()
        plan = self.build_analysis_plan(message, intent)

        evaluation = None
        if plan["needs_evaluation"]:
            evaluation = generate_evaluation(
                area="Lectura crítica",
                country=catalog["countries"][0] if catalog["countries"] else "Latinoamérica",
                exam_reference=catalog["exams"][0] if catalog["exams"] else "Prueba estatal",
                difficulty="media",
                number_of_questions=5,
                topic="competencias identificadas en el catálogo",
                db=self.db,
            )
            analysis = {
                "intent": "evaluation",
                "statistics": {},
                "charts": [],
                "tables": [],
                "insights": ["Generé una evaluación base usando el contexto disponible del catálogo."],
                "recommendations": ["Ajusta área, dificultad y país si necesitas una versión más específica."],
                "limitations": ["La evaluación es generada, no corresponde a ítems oficiales."],
                "datasets_used": [],
                "data_mode": "generativo",
            }
        elif plan["needs_analytics"] or intent in {"overview", "comparison", "gap", "trend"}:
            analysis = self.analytics.analyze_user_query(message)
        else:
            analysis = self.analytics.get_general_overview(message)

        rag_payload = {"context": "", "sources": []}
        if plan["needs_rag"]:
            rag_payload = retrieve_context(message, top_k=5)

        answer = await self.generate_final_answer(message, catalog, analysis, rag_payload, evaluation)
        return {
            "answer": answer,
            "data_mode": analysis.get("data_mode", "sin_datos"),
            "intent": analysis.get("intent", intent),
            "datasets_used": analysis.get("datasets_used", []),
            "statistics": analysis.get("statistics", {}),
            "charts": analysis.get("charts", []),
            "tables": analysis.get("tables", []),
            "insights": analysis.get("insights", []),
            "recommendations": analysis.get("recommendations", []),
            "limitations": analysis.get("limitations", []),
            "sources": rag_payload.get("sources", []),
            "evaluation": evaluation,
            "catalog_snapshot": {
                "countries": catalog["countries"],
                "exams": catalog["exams"],
                "years": catalog["years"],
                "subjects": catalog["subjects"],
            },
        }

    async def generate_final_answer(
        self,
        message: str,
        catalog: dict[str, Any],
        analysis: dict[str, Any],
        rag_payload: dict[str, Any],
        evaluation: dict[str, Any] | None,
    ) -> str:
        context = {
            "catalogo": {
                "countries": catalog["countries"],
                "exams": catalog["exams"],
                "years": catalog["years"],
                "subjects": catalog["subjects"],
                "dataset_count": len(catalog["datasets"]),
            },
            "analysis": {
                "intent": analysis.get("intent"),
                "statistics": analysis.get("statistics"),
                "insights": analysis.get("insights"),
                "recommendations": analysis.get("recommendations"),
                "limitations": analysis.get("limitations"),
                "datasets_used": analysis.get("datasets_used"),
            },
            "rag_context": rag_payload.get("context", "")[:2000],
            "evaluation": evaluation,
        }
        prompt = (
            "Redacta una respuesta ejecutiva en español para el usuario. "
            "No inventes cifras; usa únicamente el contexto JSON. "
            "Incluye advertencias metodológicas si aparecen limitaciones.\n\n"
            f"Pregunta: {message}\n\nContexto JSON:\n{json.dumps(context, ensure_ascii=False)}"
        )
        return await call_llm(prompt, json.dumps(context, ensure_ascii=False))
