# Recipe Recommender API

A FastAPI application that recommends recipes based on user pantry items and preferences.  
It integrates a vector database for similarity search and uses an LLM (Ollama) to generate detailed instructions and substitutions.

---

## Table of Contents
1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Setup & Installation](#setup--installation)
4. [Environment Variables](#environment-variables)
5. [Running with Docker](#running-with-docker)
6. [API Endpoints](#api-endpoints)
8. [Screenshots](#screenshots)
9. [Testing](#testing)
10. [Notes](#notes)

---

## Features
- Recommend recipes based on pantry items, diet, cuisine, time, and servings.
- Generates step-by-step cooking instructions using LLM (Ollama).
- Suggests ingredient substitutions if something is missing.
- Vector DB integration for fast and accurate similarity-based recipe retrieval.
- Dockerized setup for easy local deployment.

---

## Prerequisites
- Python 3.12+
- pip
- Ollama installed and running on host machine
- Docker & Docker Compose (optional for containerized deployment)
- Git (for cloning repo)

---

## Setup & Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd recipe-recommender
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Ollama is installed, and download a lightweight model:
```bash
ollama list
ollama run llama3.2:1b #for lighter version
```

5. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

- Frontend accessible at: `http://localhost:8000/`
- API docs available at: `http://localhost:8000/docs`

---

## Environment Variables

Create a `.env` file in project root:

```
VECTOR_DB_PATH=./vector_db
LLM_MODEL=llama3.2:1b
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

---

## Running with Docker

1. Build and run using Docker Compose:
```bash
docker compose up --build
```

2. The API will be available at:
```
http://localhost:8000/
```

**Note:** Ollama must be running on the host machine to allow LLM integration.

---

## API Endpoints

### Health Check
```
GET /health
```
Response:
```json
{
  "status": "ok",
  "message": "API is running"
}
```

### Recommend Recipes
```
POST /recommend-recipes
```
Request body:       #its only example , you can do this with frontend like sending the request
```json
{
  "pantry_items": ["chickpeas", "tomato", "garam masala"],
  "diet": "vegan",
  "cuisine": "indian",
  "time_available": 60,
  "servings_required": 2
}
```

Sample response:
```json
[
  {
    "name": "Chana Masala",
    "ingredients": "chickpeas, onion, tomato, garam masala, ginger, garlic",
    "tags": "vegan, indian, curry, gluten-free",
    "time_minutes": 40,
    "servings": 4,
    "match_score": 3,
    "time_ok": true,
    "servings_ok": true,
    "cuisine_ok": true,
    "llm": {
      "rank": "high",
      "substitutions": ["onion->shallots (add 1/4 cup chopped)"],
      "instructions": [
        "Heat oil in a pan over medium heat.",
        "Add minced ginger and sauté for 1 minute, until fragrant.",
        "Add minced garlic and cook for another minute.",
        "Add diced onion and cook until softened, about 5 minutes.",
        "Add diced tomato and cook for 2-3 minutes, until they start to break down.",
        "Add a pinch of salt and garam masala. Mix well.",
        "Add the chickpeas and stir well.",
        "Reduce heat to low and let it simmer for 15-20 minutes, stirring occasionally.",
        "Adjust seasoning as needed with salt, cumin powder, or more ginger.",
        "Serve hot over basmati rice or with naan bread."
      ]
    }
  }
]
```

---

## Sample cURL Requests

**Health Check**
```bash
curl -X GET http://localhost:8000/health
```


---

## Screenshots
added in document
---

## Testing

Run unit tests:
```bash
pytest
```

- Ensure coverage includes endpoints, vector DB query logic, and LLM helper.
- Example test cases: pantry match filtering, LLM instruction generation, diet/cuisine filtering.

---

## Notes
- Ollama LLM must be running on the host machine for recipe instructions.
- For low-RAM systems, use lightweight models like `llama3.2:1b`.
- Docker allows containerized setup but Ollama access from container must be ensured.
- Adjust `time_available` and `servings_required` in request body to filter recipes efficiently.

