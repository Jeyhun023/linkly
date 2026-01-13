# Linkly - URL Shortener Service

FastAPI + PostgreSQL service with Alembic migrations.

## Quick Start

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

## Endpoints

- **GET /health** - Health check endpoint
- **GET /docs** - OpenAPI documentation (Swagger UI)
- **GET /redoc** - ReDoc documentation

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `BASE_DOMAIN` - Base domain for shortened URLs

See `.env.example` for configuration options.

## Project Structure

```
linkly/
├── app/
│   ├── __init__.py
│   ├── main.py      # FastAPI application
│   ├── db.py        # Database connection
│   ├── models.py    # SQLAlchemy models
│   ├── schemas.py   # Pydantic schemas
│   └── config.py    # Configuration management
├── alembic/         # Database migrations
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Development

Run migrations manually:
```bash
alembic upgrade head
```

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```
