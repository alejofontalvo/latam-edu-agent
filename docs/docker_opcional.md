# Despliegue Opcional con Docker

Docker no es obligatorio para la primera versión académica. La solución principal está diseñada para ejecutarse localmente con comandos tradicionales.

## Cuándo conviene usar Docker

- Cuando se requiere replicar el entorno en varios equipos.
- Cuando el proyecto pasa a pruebas de integración o producción.
- Cuando se desea aislar backend, frontend, PostgreSQL y ChromaDB.
- Cuando se despliega en un servidor cloud.

## Servicios que podrían contenerizarse

- Backend FastAPI.
- Frontend React servido por Nginx.
- PostgreSQL.
- Servicio de ChromaDB persistente.
- n8n si se automatizan ingestas.

## Ejemplo futuro de docker-compose

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://latam:latam@db:5432/latam
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "5173:80"

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: latam
      POSTGRES_PASSWORD: latam
      POSTGRES_DB: latam
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Ventajas para producción

- Entornos reproducibles.
- Despliegues consistentes.
- Mejor separación de servicios.
- Escalabilidad más clara.

Para la entrega académica inicial se recomienda mantener ejecución local sin Docker.
