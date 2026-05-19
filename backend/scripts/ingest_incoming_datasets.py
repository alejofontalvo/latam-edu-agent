from bootstrap import BACKEND_DIR  # noqa: F401
from app.models.database import SessionLocal, init_db
from app.services.data_ingestion_service import DataIngestionService


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        reports = DataIngestionService(db).ingest_all_from_folder()
        if not reports:
            print("No hay archivos en data/incoming.")
        for report in reports:
            print(f"Ingerido: {report['dataset_id']} ({report['rows']} filas largas)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
