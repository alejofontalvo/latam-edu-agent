# Guía de Despliegue Local

## Requisitos

- Python 3.10 o superior.
- Node.js 18 o superior.
- 8 GB de RAM mínimo.
- 16 GB de RAM recomendado.
- API key de LLM opcional para respuestas generativas avanzadas.

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Validación

Abrir:

- API: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

## PostgreSQL opcional

Para pasar de SQLite a PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/latam_edu_agent
```

Instalar el driver correspondiente y reiniciar la API.
