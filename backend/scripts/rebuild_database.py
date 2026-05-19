from pathlib import Path

from bootstrap import BACKEND_DIR
from app.models.database import Base, engine, init_db


def main() -> None:
    sqlite_path = BACKEND_DIR / "latam_edu_agent.db"
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if sqlite_path.exists():
        sqlite_path.unlink()
    init_db()
    print(f"Base reconstruida: {sqlite_path}")


if __name__ == "__main__":
    main()
