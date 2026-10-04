# TripMate: AI-Powered Smart Tourism Planner

TripMate creates personalized trip plans from a traveller's preferences, budget, and real tourism data. Users chat with an AI assistant and get a full itinerary they can edit and save.

It has a React web app, a Flutter mobile app, and a FastAPI backend.

## Features

**For travellers**
- Register, log in, and use role-based access
- Plan trips by chatting with an AI assistant
- Get personalized itineraries with attractions, hotels, restaurants, and local events
- Budget-aware suggestions, cost estimates, and route optimization
- Weather-aware checks and nearby place discovery
- Create, edit, save, continue, and manage trips

**For admins**
- Manage tourism data on web and mobile
- Super Admin tools for users, admins, feedback, dashboards, and reports

**AI**
- Agentic planning: the AI picks planning actions and improves the plan step by step


## Technology Stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL (pgvector), JWT |
| Web | React, Vite, Tailwind CSS |
| Mobile | Flutter |
| AI | Google Gemini, LangGraph, LangChain |
| External services | Google Maps API, Google Places API, Weather API, AWS SES, AWS S3/CloudFront |

## Repository Structure

```text
.
├── backend/        # FastAPI backend
├── web/            # React web application
├── mobile/         # Flutter mobile application
├── docs/           # Architecture, API contract, auth flow, and RBAC docs
├── .github/        # GitHub templates and workflows
├── CONTRIBUTING.md
└── README.md
```

## Prerequisites

| Tool | Needed for |
| --- | --- |
| Git | Cloning the repo |
| Docker and Docker Compose | Running the backend and PostgreSQL |
| Node.js and npm | Web app |
| Flutter SDK | Mobile app |
| Python 3.11+ | Only if you run the backend without Docker |

## Getting Started

Clone the repository:

```bash
git clone https://github.com/sep-group-10/tripmate.git
cd tripmate
```

### 1. Backend

```bash
cd backend
cp .env.example .env   # then fill in your keys (see below)
docker compose up --build
```

- API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs
- Database migrations (Alembic) run automatically on startup.

**Environment variables:** open `.env.example` to see all keys. You need at least a JWT secret, a Google Gemini key, and Google Maps/Places keys. AWS keys are needed for email (SES) and file storage (S3/CloudFront).

### 2. Web

```bash
cd web
npm install
npm run dev
```

The app runs at http://localhost:5173.

### 3. Mobile

```bash
cd mobile
flutter pub get
flutter run
```

To use a physical device with a local backend, see [mobile/README.md](mobile/README.md).

## Testing

| Application | Tools | Command |
| --- | --- | --- |
| Backend | Pytest, HTTPX | `pytest` |
| Web | Vitest, React Testing Library, Playwright | `npm test` / `npx playwright test` |
| Mobile | Flutter Test, `integration_test` | `flutter test` |

## Building for Production

```bash
# Web
cd web && npm run build

# Mobile (Android)
cd mobile && flutter build apk
```

## Documentation

See [docs/](docs/) for the API contract, authentication flow, and role-based access control (RBAC) reference.

## Team

SEP Group 10, Semester 5 Software Engineering Project, University of Moratuwa.

| Name |
| --- |
| Kajatheepan |
| Babijana |  
| Jitharsanan |  

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch, commit, issue, and pull-request guidelines.

## Project Status

Under development.