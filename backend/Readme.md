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

TripMate uses automated and manual testing techniques to verify the correctness, reliability, and performance of the system.

## Backend Testing

Backend tests use:

- pytest
- HTTPX (for FastAPI's `TestClient`)

Tests run against a real PostgreSQL database. The models use PostgreSQL-specific types such as `UUID` and `ARRAY`, so SQLite cannot be used.

Each test runs inside a database transaction that is rolled back afterward, so tests do not leave data behind in the database they run against.

## Running Backend Tests Locally

Make sure the containers are up and built with the latest dependencies:

```bash
docker compose up -d --build backend
```

The full backend test suite can be executed against the dedicated test database:

```bash
docker compose exec \
  -e TEST_DATABASE_URL="postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_migration_test" \
  backend pytest -v
```

Run a single test file:

```bash
docker compose exec \
  -e TEST_DATABASE_URL="postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_migration_test" \
  backend pytest tests/test_auth_register.py -v
```

Run a single test case:

```bash
docker compose exec \
  -e TEST_DATABASE_URL="postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_migration_test" \
  backend pytest tests/test_auth_register.py::test_register_duplicate_email_returns_conflict -v
```

Tests use `TEST_DATABASE_URL` when it is provided. Otherwise, the test configuration falls back to the database configured through `DATABASE_URL`.

## Authentication Testing

Authentication-related tests can also be executed as a focused test suite:

```bash
docker compose exec \
  -e TEST_DATABASE_URL="postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_migration_test" \
  backend pytest \
  tests/test_auth_register.py \
  tests/test_auth_login_logout.py \
  tests/test_auth_refresh.py \
  tests/test_auth_change_password.py \
  tests/test_auth_delete_account.py \
  -v
```

This covers the main authentication and account-management flows, including registration, login/logout, token refresh, password changes, and account deletion.

## Frontend Testing

Frontend tests are implemented using Vitest.

Navigate to the frontend directory:

```bash
cd web
```

Run the complete frontend test suite:

```bash
npm test -- --run
```

To run the tests in watch mode:

```bash
npm test
```

## AI Component Evaluation

TripMate includes dedicated evaluations for the AI planning components.

### Planner Evaluation

The Planner is evaluated using predefined scenarios to verify whether an appropriate planning action is selected for the current planning state.

Run the Planner evaluation tests:

```bash
docker compose exec backend pytest tests/evals/test_planner_eval.py -v
```

The live Planner evaluation requires a valid `OPENROUTER_API_KEY` configured in the backend environment.

### Critic Evaluation

The Critic is evaluated using predefined itinerary scenarios to assess its planning-quality decisions.

Run the Critic evaluation tests:

```bash
docker compose exec backend pytest tests/evals/test_critic_eval.py -v
```

The live Critic evaluation requires a valid `OPENROUTER_API_KEY` configured in the backend environment.

## API Testing

The FastAPI backend provides an interactive Swagger/OpenAPI interface.

Start the backend and open:

```text
http://localhost:8000/docs
```

The available API endpoints can be executed directly from Swagger to verify request and response behaviour.

For example, the destination retrieval endpoint can be tested using:

```text
GET /api/v1/destinations?page=1&limit=20
```

The response status and returned JSON data can then be inspected through the Swagger interface.

## Performance Testing

Performance testing is performed using Locust.

From the backend directory, run:

```bash
locust -f tests/performance/locustfile.py \
  --host http://localhost:8000 \
  --headless \
  -u 10 \
  -r 10 \
  -t 30s
```

The performance test simulates 10 concurrent users for 30 seconds against:

```text
GET /api/v1/destinations?page=1&limit=20
```

The command-line options are:

- `-u 10` - number of concurrent users
- `-r 10` - user spawn rate
- `-t 30s` - test duration
- `--headless` - runs Locust without the web interface

## Database Migration Testing

Alembic is used to manage and verify database migrations.

Check the current migration revision:

```bash
docker compose exec \
  -e DATABASE_URL="postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_migration_test" \
  backend alembic current
```

Apply all available migrations:

```bash
docker compose exec \
  -e DATABASE_URL="postgresql+psycopg2://tripmate_user:tripmate1234@database:5432/tripmate_migration_test" \
  backend alembic upgrade head
```

## Running Tests in CI

The GitHub Actions workflow (`.github/workflows/backend-ci.yml`) spins up its own throwaway PostgreSQL service container for every PR. It never touches anyone's local database.

Backend tests run automatically on every pull request to `main`.

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