from bootstrap import BACKEND_DIR  # noqa: F401
from app.models.database import SessionLocal, init_db
from app.services.powerbi_service import export_powerbi_files


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        outputs = export_powerbi_files(db)
        for name, path in outputs.items():
            print(f"{name}: {path}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
