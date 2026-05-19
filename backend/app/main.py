from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin_routes, analytics_routes, catalog_routes, chat_routes, dataset_routes, evaluation_routes, rag_routes, report_routes
from app.config import get_settings
from app.models.database import init_db


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agente inteligente para pruebas estatales y evaluación educativa en Latinoamérica.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "API lista. Consulta /docs para ver endpoints.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/system/status")
def system_status():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "data_dir": str(settings.data_dir),
        "incoming_dir": str(settings.project_dir / "data" / "incoming"),
        "llm_provider": settings.llm_provider,
    }


app.include_router(chat_routes.router)
app.include_router(catalog_routes.router)
app.include_router(dataset_routes.router)
app.include_router(analytics_routes.router)
app.include_router(rag_routes.router)
app.include_router(evaluation_routes.router)
app.include_router(report_routes.router)
app.include_router(admin_routes.router)
