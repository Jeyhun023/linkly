# Simple Link Shortener App

## Quick Start

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

## Endpoints

- **GET /health** - Health check endpoint
- **POST /links** - Create a new short link (returns 201)
- **GET /links** - List all links with optional search query
- **GET /links/{slug}/stats** - Get click statistics for a link
- **GET /{slug}** - Redirect to target URL with click tracking (returns 302)
- **GET /docs** - OpenAPI documentation (Swagger UI)
- **GET /redoc** - ReDoc documentation

### POST /links

Create a new short link with auto-generated slug.

**Request:**
```json
{
  "target_url": "https://example.com/very/long/url",
  "campaign": "summer-sale",
  "label": "homepage-banner",
  "source": "email",
  "created_by": "user@example.com"
}
```

**Response (201):**
```json
{
  "id": 123,
  "slug": "Ab3k9Z",
  "short_url": "https://go.wpml.org/Ab3k9Z",
  "target_url": "https://example.com/very/long/url",
  "created_at": "2026-01-14T12:00:00Z",
  "metadata": {
    "campaign": "summer-sale",
    "label": "homepage-banner",
    "source": "email",
    "created_by": "user@example.com"
  }
}
```

**Notes:**
- `target_url` is required and must be http/https
- All other fields are optional
- Slug is auto-generated (base62, 6+ characters)
- Links are immutable (no update endpoint)
- Collision-safe slug generation

### GET /{slug}

Redirect to the target URL and log click analytics.

**Behavior:**
- Returns **302 Found** redirect to target URL
- Returns **404 Not Found** if slug doesn't exist or link is disabled
- Logs click event with privacy-safe tracking

**Click Tracking:**
- `clicked_at` - UTC timestamp
- `link_id` - Reference to the link
- `referrer` - HTTP Referer header (if present)
- `user_agent` - User agent string
- `ip_hash` - SHA256(IP + user_agent + link_id + date) - privacy-safe
- `ip_truncated_or_null` - Truncated IP (e.g., 192.168.1.xxx) or null
- `day` - Date for aggregation queries

**Privacy:**
- Raw IP addresses are **never stored**
- IP hash includes daily salt for privacy
- Only truncated IP is optionally stored

**Example:**
```bash
curl -L http://localhost:8000/Ab3k9Z
# Returns 302 redirect to target URL
# Logs click event in database
```

### GET /links

List all links with optional search filtering.

**Query Parameters:**
- `query` (optional) - Search term to filter links by slug, target_url, campaign, label, or source

**Response:**
```json
{
  "links": [
    {
      "id": 123,
      "slug": "Ab3k9Z",
      "target_url": "https://example.com",
      "created_at": "2026-01-14T12:00:00Z",
      "created_by": "user@example.com",
      "campaign": "summer-sale",
      "label": "homepage",
      "source": "email",
      "is_disabled": false
    }
  ],
  "total": 1
}
```

**Example:**
```bash
# List all links
curl http://localhost:8000/links

# Search links
curl "http://localhost:8000/links?query=summer"
```

### GET /links/{slug}/stats

Get click statistics and analytics for a specific link.

**Response:**
```json
{
  "link": {
    "id": 123,
    "slug": "Ab3k9Z",
    "target_url": "https://example.com",
    "created_at": "2026-01-14T12:00:00Z",
    "is_disabled": false
  },
  "total_clicks": 1234,
  "unique_clicks_approx": 456,
  "daily": [
    {
      "date": "2026-01-14",
      "clicks": 100,
      "unique": 75
    },
    {
      "date": "2026-01-13",
      "clicks": 150,
      "unique": 120
    }
  ]
}
```

**Metrics:**
- `total_clicks` - Total number of clicks (all time)
- `unique_clicks_approx` - Approximate unique visitors (based on distinct ip_hash)
- `daily` - Daily breakdown with click count and unique visitors per day
  - Sorted by date descending (most recent first)
  - `unique` per day based on distinct ip_hash for that day

**Example:**
```bash
curl http://localhost:8000/links/Ab3k9Z/stats
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `BASE_DOMAIN` - Base domain for shortened URLs

See `.env.example` for configuration options.

## Database Schema

### Link Model
- `id` (bigint) - Primary key
- `slug` (string, unique) - Short URL identifier
- `target_url` (string) - Original URL to redirect to
- `created_at` (timestamp) - Link creation timestamp
- `created_by` (string, nullable) - Creator identifier
- `campaign` (string, nullable) - Campaign tracking
- `label` (string, nullable) - Custom label
- `source` (string, nullable) - Source tracking
- `is_disabled` (boolean) - Link disabled flag (default: false)

### LinkClick Model
- `id` (bigint) - Primary key
- `link_id` (bigint, FK) - Foreign key to links table
- `clicked_at` (timestamp) - Click timestamp
- `referrer` (string, nullable) - HTTP referrer
- `user_agent` (string, nullable) - User agent string
- `ip_hash` (string) - Hashed IP address for privacy
- `ip_truncated_or_null` (string, nullable) - Truncated IP or null for privacy
- `day` (date) - Date for aggregation queries

### Indexes
- `links.slug` - Unique index for fast lookups
- `link_clicks.link_id + clicked_at` - For time-based queries
- `link_clicks.link_id + ip_hash` - For unique visitor counting

## Project Structure

```
linkly/
├── app/
│   ├── __init__.py
│   ├── main.py      # FastAPI application
│   ├── db.py        # Database connection
│   ├── models.py    # SQLAlchemy models (Link, LinkClick)
│   ├── schemas.py   # Pydantic schemas
│   └── config.py    # Configuration management
├── alembic/         # Database migrations
│   └── versions/    # Migration scripts
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Database Migrations

### Run migrations using docker compose:
```bash
# Upgrade to latest migration
docker compose run --rm api alembic upgrade head

# View current migration status
docker compose run --rm api alembic current

# View migration history
docker compose run --rm api alembic history

# Downgrade one revision
docker compose run --rm api alembic downgrade -1
```

### Create a new migration:
```bash
# Auto-generate migration from model changes
docker compose run --rm api alembic revision --autogenerate -m "description"

# Create empty migration
docker compose run --rm api alembic revision -m "description"
```

### Local development (without docker):
```bash
# Upgrade to latest
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```
