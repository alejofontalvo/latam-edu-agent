import argparse

from bootstrap import BACKEND_DIR  # noqa: F401
from app.models.database import SessionLocal, init_db
from app.services.data_ingestion_service import DataIngestionService
from app.services.dataset_service import ingest_registered_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=False, help="registry_id del dataset")
    parser.add_argument("--file", required=False, help="archivo en data/incoming o ruta local")
    args = parser.parse_args()
    init_db()
    db = SessionLocal()
    try:
        if args.file:
            report = DataIngestionService(db).ingest_dataset_from_file(args.file)
            print(f"Ingerido desde archivo: {report['dataset_id']} ({report['rows']} filas largas)")
        elif args.id:
            dataset = ingest_registered_dataset(args.id, db)
            print(f"Ingerido: {dataset['registry_id']} ({dataset['row_count']} filas)")
        else:
            raise SystemExit("Usa --id <registry_id> o --file <ruta>")
    finally:
        db.close()


if __name__ == "__main__":
    main()
