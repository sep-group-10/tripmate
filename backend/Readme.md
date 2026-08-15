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

# Testing

Backend tests use:

* pytest
* HTTPX

Run tests:

```bash
pytest
```

or inside Docker:

```bash
docker compose exec backend pytest
```

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