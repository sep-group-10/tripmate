# Backend

## Overview

The backend provides the REST API for the AI-Powered Smart Tourism Assistant.

It is built using **FastAPI** and handles:

- Business logic
- Authentication and authorization
- Database operations
- External service integration
- AI service integration

The backend uses **PostgreSQL** as the database and **Alembic** for database schema migrations.

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migration Tool | Alembic |
| Authentication | JWT |
| Testing | pytest, HTTPX |
| Containerization | Docker |

---

## Backend Structure

```text
backend/
│
├── app/                    # Application source code
│
├── alembic/                # Database migration files
│
├── tests/                  # Backend tests
│
├── Dockerfile              # Backend container configuration
├── docker-compose.yml      # Development environment setup
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md
```

---

# Development Setup

## Prerequisites

Install:

* Python
* Docker
* Docker Compose

---

## Environment Configuration

Create a local environment file from the example:

```bash
cp .env.example .env
```

Configure the required variables:

```env
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

DATABASE_URL=
```

### Important

* `.env` contains local credentials and must not be committed.
* `.env.example` should be committed as a reference for developers.

---

# Running with Docker

The backend development environment uses Docker to run:

* FastAPI backend
* PostgreSQL database

Start the environment:

```bash
docker compose up --build
```

The startup process:

```text
1. PostgreSQL container starts
2. Database health check passes
3. Backend container starts
4. Alembic migrations are applied
5. FastAPI application starts
```

The backend will be available at:

```
http://localhost:8000
```

API documentation:

```
http://localhost:8000/docs
```

---

# Database Migration

The project uses **Alembic** to manage database schema changes.

## Creating a Migration

After modifying SQLAlchemy models:

```bash
docker compose exec backend alembic revision --autogenerate -m "migration description"
```

Review the generated migration file before committing.

Migration files are stored in:

```text
alembic/
└── versions/
```

---

## Applying Migrations

Apply all pending migrations:

```bash
docker compose exec backend alembic upgrade head
```

Database migrations are automatically applied when the backend container starts.

Manual migration commands are mainly used for development and troubleshooting.

---

## Checking Current Migration

```bash
docker compose exec backend alembic current
```

View migration history:

```bash
docker compose exec backend alembic history
```

---

## Rolling Back a Migration

Rollback the latest migration:

```bash
docker compose exec backend alembic downgrade -1
```

Rollback to a specific revision:

```bash
docker compose exec backend alembic downgrade <revision_id>
```

---

# Database Seeding

Seed scripts populate the database with initial reference data.

Run a seed script inside the running `backend` container:

```bash
docker compose exec backend python -m app.core.seed
docker compose exec backend python -m app.core.seed_tourism
```

The `backend` container already has `DATABASE_URL` configured, so seeding runs against the dockerized PostgreSQL database directly.

---

# Testing

Backend tests use:

* pytest
* HTTPX (for FastAPI's `TestClient`)

Tests run against a real PostgreSQL database (the models use Postgres-only
types like `UUID` and `ARRAY`, so SQLite cannot be used). Each test runs
inside a database transaction that is rolled back afterward, so tests never
leave data behind in the database they run against.

## Running tests locally

Make sure the containers are up and built with the latest dependencies:

```bash
docker compose up -d --build backend
```

Run the full suite:

```bash
docker compose exec backend pytest -v
```

Run a single test file or test case:

```bash
docker compose exec backend pytest tests/test_auth_register.py -v
docker compose exec backend pytest tests/test_auth_register.py::test_register_duplicate_email_returns_conflict -v
```

By default, tests connect to the same database as the `backend` container
(`DATABASE_URL`). To point tests at a different database, set
`TEST_DATABASE_URL`.

## Running tests in CI

The GitHub Actions workflow (`.github/workflows/backend-ci.yml`) spins up its
own throwaway PostgreSQL service container for every PR — it never touches
anyone's local database. Tests run automatically on every PR to `main`.

---

# Docker Troubleshooting

## Check running containers

```bash
docker compose ps
```

---

## View backend logs

```bash
docker compose logs backend
```

---

## View database logs

```bash
docker compose logs database
```

---

## Rebuild containers

```bash
docker compose up --build
```

---

## Reset Development Database

Stop containers and remove volumes:

```bash
docker compose down -v
```

Start again:

```bash
docker compose up --build
```

**Warning:** Removing volumes deletes the local PostgreSQL data.

---

# Development Notes

* Do not commit `.env` files.
* Review generated Alembic migrations before committing.
* Database schema changes must be committed together with their migration files.
* The backend container will not start if database migration fails.