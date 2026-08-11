# AI-Powered Smart Tourism Planner

A smart tourism platform that creates personalized trip recommendations and itineraries from travellers' preferences, budgets, and available tourism data.

The system includes a React web app, Flutter mobile app, and FastAPI backend, with integrations for AI, maps, places, and weather data.

## Features

- User registration and role-based authentication
- AI-powered conversational trip planning with personalized itineraries
- Agentic trip planning with dynamic planning actions and iterative refinement
- Budget-aware recommendations, cost estimation, and route optimization
- Personalized recommendations for attractions, hotels, restaurants, and local events
- Weather-aware itinerary validation and nearby place discovery
- Trip creation, modification, saving, continuation, and management
- Web and mobile applications with tourism-data administration
- Super Admin controls for users, administrators, feedback, dashboards, and reports
  
## Technology Stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, PostgreSQL, JWT |
| Web | React |
| Mobile | Flutter |
| AI | Gemini API |
| External services | Google Maps API, Google Places API, Weather API |

## Repository Structure

```text
.
├── backend/        # FastAPI backend
├── web/            # React web application
├── mobile/         # Flutter mobile application
├── .github/        # GitHub templates and workflows
├── CONTRIBUTING.md
├── .env.example
└── README.md
```

## Prerequisites

Install Git, Python, Node.js with npm, the Flutter SDK, and PostgreSQL. Application-specific dependencies will be documented in their respective directories as development progresses.

## Getting Started

> **Note:** Detailed setup and run instructions will be added as development progresses.

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

## Testing

| Application | Tools | Coverage |
| --- | --- | --- |
| Backend | Pytest, HTTPX | Application logic and API endpoints |
| Web | Vitest, React Testing Library, Playwright | Components and end-to-end user flows |
| Mobile | Flutter Test, `integration_test` | Unit, widget, and integration flows |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch, commit, issue, and pull-request guidelines.

## Project Status

Under development as a Semester 5 Software Engineering Project by SEP Group 10.
