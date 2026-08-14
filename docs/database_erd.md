# TripMate Database ERD

## Entity Relationship Diagram

```mermaid
erDiagram

    USERS ||--o{ TRIPS : "has"
    USERS ||--o{ FEEDBACK : "submits"

    DESTINATIONS ||--o{ ATTRACTIONS : "contains"
    DESTINATIONS ||--o{ HOTELS : "contains"
    DESTINATIONS ||--o{ RESTAURANTS : "contains"
    DESTINATIONS ||--o{ LOCAL_EVENTS : "contains"

    TRIPS ||--o{ ITINERARIES : "has"
    TRIPS ||--o{ PLANNING_SESSIONS : "has"

    ITINERARIES ||--o{ ITINERARY_DAYS : "contains"
    ITINERARY_DAYS ||--o{ ITINERARY_DAY_ITEMS : "contains"

    PLANNING_SESSIONS ||--o{ AGENT_EXECUTION_TRACES : "records"
    PLANNING_SESSIONS ||--o{ CONVERSATION_HISTORY : "contains"

    USERS {
        uuid id PK
    }

    DESTINATIONS {
        uuid id PK
    }

    ATTRACTIONS {
        uuid id PK
        uuid destination_id FK
    }

    HOTELS {
        uuid id PK
        uuid destination_id FK
    }

    RESTAURANTS {
        uuid id PK
        uuid destination_id FK
    }

    LOCAL_EVENTS {
        uuid id PK
        uuid destination_id FK
    }

    TRIPS {
        uuid id PK
        uuid user_id FK
    }

    ITINERARIES {
        uuid id PK
        uuid trip_id FK
    }

    ITINERARY_DAYS {
        uuid id PK
        uuid itinerary_id FK
    }

    ITINERARY_DAY_ITEMS {
        uuid id PK
        uuid itinerary_day_id FK
    }

    PLANNING_SESSIONS {
        uuid id PK
        uuid trip_id FK
    }

    AGENT_EXECUTION_TRACES {
        uuid id PK
        uuid planning_session_id FK
    }

    CONVERSATION_HISTORY {
        uuid id PK
        uuid planning_session_id FK
    }

    FEEDBACK {
        uuid id PK
        uuid user_id FK
    }
