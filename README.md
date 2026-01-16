# Simple Link Shortener App

## Quick Start

```bash
make up
```

The API will be available at `http://localhost:8000`

## Make Commands

| Command        | Description                          |
|----------------|--------------------------------------|
| `make up`      | Start all containers                 |
| `make down`    | Stop all containers                  |
| `make build`   | Build containers                     |
| `make logs`    | Show container logs (follow mode)    |
| `make destroy` | Stop containers and remove volumes   |
| `make migrate` | Run database migrations              |
| `make sh`      | Open shell in API container          |
| `make help`    | Show available commands              |

## Endpoints

- **POST /links** - Create a new short link (returns 201)
- **GET /links** - List all links with optional search query
- **GET /links/{slug}/stats** - Get click statistics for a link
- **GET /{slug}** - Redirect to target URL with click tracking (returns 302)
- **GET /docs** - OpenAPI documentation (Swagger UI)
- **GET /redoc** - ReDoc documentation
