# Travel Planner API

REST API for travel projects and places backed by SQLite and the Art Institute of Chicago API.

## Requirements

- Python 3.11+
- Poetry

## Setup

Install dependencies:

```bash
poetry install
```

Run the API locally:

```bash
poetry run uvicorn app.main:app --reload
```

Run with Docker:

```bash
docker compose up --build
```

## Environment Variables

The application uses:

- `DATABASE_URL` - SQLAlchemy async database URL

Default value:

```text
sqlite+aiosqlite:///./travel_planner.db
```

Optional `.env` example:

```env
DATABASE_URL=sqlite+aiosqlite:///./travel_planner.db
```

## API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

## Endpoints

### Projects

- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`

### Places

- `POST /projects/{project_id}/places`
- `GET /projects/{project_id}/places`
- `GET /projects/{project_id}/places/{place_id}`
- `PATCH /projects/{project_id}/places/{place_id}`

## Example Requests

### Create a project with places

```bash
curl -X POST http://127.0.0.1:8000/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rome trip",
    "description": "Trip planning",
    "start_date": "2026-06-25",
    "external_places": [129884, 146515]
  }'
```

### Add a place to an existing project

```bash
curl -X POST http://127.0.0.1:8000/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": 129884,
    "notes": "Visit in the morning"
  }'
```

### Update a place

```bash
curl -X PATCH http://127.0.0.1:8000/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{
    "is_visited": true,
    "notes": "Visited on arrival"
  }'
```

## Business Rules

- A project must contain at least 1 place and at most 10 places.
- A place must exist in the Art Institute of Chicago API before it can be added.
- The same external place cannot be added twice to the same project.
- A project cannot be deleted if any of its places are marked as visited.
- When all places in a project are visited, the project is completed.
