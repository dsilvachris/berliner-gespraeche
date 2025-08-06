# API Specification: Klimaneustart Civic Dialogue App

## 1. Overview

This document specifies the REST API for the **Klimaneustart** application. The API's purpose is twofold:

- **Provide Lookup Data**: To dynamically supply the frontend with data needed to render UI elements like topics, initiatives, and district lists. This avoids hardcoding data on the frontend.
- **Handle Data Ingestion**: To receive and securely store complete dialogue submissions from the frontend into the normalized SQLite database.

**Base URL**: All endpoints should be prefixed with `/api/v1`.  
Example: `https://your-domain.com/api/v1/dialogues`

**Authentication**: For the MVP, these endpoints will be public and do not require an authentication token. Future versions will incorporate user-specific authentication.

---

## 2. Data Models (API Schemas)

These models define the JSON structures used in API requests and responses.

### Theme

Represents a single interest area.

```json
{
  "id": "Urban Garden",
  "name": "Urban Garden",
  "description": "Community gardens and community sovereignity",
  "icon": "icon link"
}
```

### Initiative

Represents a single initiative with its related data.

```json
{
  "id": "garten_projekt",
  "name": "Kreuzberg Community Garden",
  "description": "A local garden for residents to grow their own food.",
  "districts": ["Friedrichshain-Kreuzberg"],
  "themes": ["Urban Garden"]
}
```

### Topic

Represents the complete hierarchical structure for a topic category.

```json
{
  "id": "wohnen_bauwende",
  "name": "Wohnen/Bauwende",
  "subGroups": [
    {
      "id": "transport",
      "name": "Transport",
      "options": [
        { "id": "costs", "name": "Costs" },
        { "id": "bicycle", "name": "Bicycle" }
      ]
    }
  ]
}
```

### DialogueSubmission

Represents the full JSON payload sent from the frontend when saving a dialogue.

```json
{
  "mainInterest": "...",
  "livableCity": "...",
  "notes": "...",
  "topicDetails": {
    "wohnen_bauwende": {
      "transport": {
        "selectedOptions": ["bicycle"],
        "customNote": "The participant emphasized safety."
      }
    }
  },
  "districts": ["Pankow", "Mitte"],
  "interestAreas": ["Urban Garden"],
  "shareContact": false,
  "contactInfo": "",
  "isAnonymous": true,
  "observerReflection": "...",
  "surprise": "...",
  "numPeople": 2,
  "duration": 30
}
```

---

## 3. API Endpoints

### 3.1 Lookup Endpoints (Read-Only)

Used to populate the frontend UI dynamically.

#### Get All Themes (Interest Areas)

- **Endpoint**: `GET /lookup/themes`
- **Description**: Retrieves a list of all available interest areas.
- **Response (200 OK)**:

```json
[
  {
    "id": "Urban Garden",
    "name": "Urban Garden",
    "description": "Community gardens and community sovereignity"
  },
  {
    "id": "Repair Café",
    "name": "Repair Café",
    "description": "Fix things together, reduce waste"
  }
]
```

#### Get All Initiatives

- **Endpoint**: `GET /lookup/initiatives`
- **Description**: Retrieves all initiatives, including associated districts and themes.
- **Response (200 OK)**:

```json
[
  {
    "id": "garten_projekt",
    "name": "Kreuzberg Community Garden",
    "description": "A local garden for residents to grow their own food.",
    "districts": ["Friedrichshain-Kreuzberg"],
    "themes": ["Urban Garden"]
  }
]
```

#### Get All Topics

- **Endpoint**: `GET /lookup/topics`
- **Description**: Retrieves the complete, hierarchical topic structure.
- **Response (200 OK)**: An array of Topic objects (example above).

#### Get All Districts

- **Endpoint**: `GET /lookup/districts`
- **Description**: Retrieves a simple list of Berlin districts.
- **Response (200 OK)**:

```json
["Mitte", "Friedrichshain-Kreuzberg", "Pankow", ...]
```

---

### 3.2 Data Ingestion Endpoints (Write)

Endpoints to create new records in the database.

#### Create a New Initiative

- **Endpoint**: `POST /initiatives`
- **Description**: Adds a new initiative.
- **Request Body**: Matches the Initiative model. `id` can be omitted.
- **Response (201 Created)**: Returns the full created initiative object.
- **Error (422 Unprocessable Entity)**: If request validation fails.

#### Submit a Dialogue

- **Endpoint**: `POST /dialogues`
- **Description**: Submits a full dialogue session from the frontend.

**Backend Logic**:

- All actions MUST occur within a single database transaction.
- If any part fails, rollback the entire transaction.
- Insert data into appropriate tables:

  - `dialogues`
  - Conditional insert into `participant_contact`
  - Link tables: `dialogue_districts`, `dialogue_interest_areas`, `dialogue_topic_selections`

**Request Body**: Matches the `DialogueSubmission` schema.

**Success Response (201 Created)**:

```json
{
  "status": "success",
  "message": "Dialogue created successfully.",
  "dialogue_id": 123
}
```

**Error Responses**:

- `422 Unprocessable Entity`: If payload is malformed or incomplete.
- `500 Internal Server Error`: If database transaction fails.
