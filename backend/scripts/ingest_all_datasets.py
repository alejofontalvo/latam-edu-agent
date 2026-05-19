from bootstrap import BACKEND_DIR  # noqa: F401
from app.models.database import SessionLocal, init_db
from app.services.dataset_service import ingest_all_registered_datasets


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        datasets = ingest_all_registered_datasets(db)
        for dataset in datasets:
            print(f"Ingerido: {dataset['registry_id']} ({dataset['row_count']} filas)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
