# Summarizer

A scalable Django backend service for summarizing data, searching the web, and generating insights using Large Language Models (LLMs) like ChatGPT. The application integrates with web search APIs (e.g., Tavily) and LLMs via LangChain, supports asynchronous processing with Celery and Redis, and uses PostgreSQL for data storage. It exposes RESTful APIs for querying and a health endpoint for monitoring.

## Features
- Web Search and Summarization: Accepts user queries, fetches relevant web results, and generates concise summaries or explanations using LLMs.
- Asynchronous Processing: Uses Celery and Redis for handling long-running tasks like LLM calls and web searches.
- Scalable Architecture: Deployed with Docker and supports orchestration with Kubernetes for production.
- Health Monitoring: Provides a `/health/` endpoint to check the status of critical components (database, Redis, Celery, OpenAI, Tavily).
- Dependency Management: Uses `uv` for fast and reproducible Python environments.
- Caching: Leverages Redis for caching query results to reduce API costs and latency.

## Tech Stack
- Backend: Django, Django REST Framework
- LLM Integration: LangChain, OpenAI API
- Web Search: Tavily API
- Task Queue: Celery with Redis
- Database: PostgreSQL
- Caching: Redis
- Environment Management: `uv`
- Containerization: Docker, Docker Compose
- Dependencies: Managed via `pyproject.toml`

## Project Structure
summarizer/
├── core/
│   ├── __init__.py
│   ├── models.py           # Database models
│   ├── views.py            # API endpoints (query, health)
│   ├── serializers.py      # API serialization
│   ├── tasky.py            # Celery tasks
│   ├── llm_service.py      # LangChain and LLM logic
│   └── tests.py            # Unit tests
├── config/
│   ├── __init__.py
│   ├── celery.py           # Celery configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── .env                    # Environment variables (API keys, etc.)
├── pyproject.toml          # Dependency management
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # Docker build instructions
└── README.md               # Project documentation

## Prerequisites
- Python: 3.11
- Docker: For containerized deployment
- uv: Python package and environment manager
- API Keys:
  - [OpenAI API key](https://platform.openai.com) for LLM access
  - [Tavily API key](https://tavily.com) for web search
- PostgreSQL and Redis (handled by Docker Compose)

## Setup Instructions

### 1. Install `uv`
Install `uv` to manage the Python environment:
macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
Windows (PowerShell):
iwr -useb https://astral.sh/uv/install.ps1 | iex
Verify installation:
uv --version


### 2. Set Up Environment Variables
Create a `.env` file in the project root with the following:
OPENAI_API_KEY=openai-api-key
TAVILY_API_KEY=tavily-api-key
DJANGO_SECRET_KEY=django-secret-key
POSTGRES_DB=myproject
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
- Replace `openai-api-key` and `tavily-api-key` with actual API keys.
- Generate a Django secret key: `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
- Add `.env` to `.gitignore` to avoid committing sensitive data.

### 3. Set Up Python Environment
Create and activate a virtual environment with `uv`:
uv venv --python 3.11
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\activate   # Windows
Install dependencies from `pyproject.toml`:
uv sync

### 4. Run Database Migrations
Apply migrations to set up the PostgreSQL database:
uv run python manage.py migrate

### 5. Run the Application
Use Docker Compose to build and run the application, including Django, Celery, PostgreSQL, and Redis:
docker-compose up --build
This starts:
- Django server at `http://localhost:8000`
- PostgreSQL database (`db` service)
- Redis (`redis` service)
- Celery worker (`celery` service)
Alternatively, run locally without Docker:
uv run python manage.py runserver 0.0.0.0:8000
uv run celery -A config worker --loglevel=info
Note: For local runs, ensure PostgreSQL and Redis are installed and running locally.

## API Endpoints
- POST /api/query/: Submit a query for summarization or web search.
  - Request body: `{"query": "Your query here", "use_web_search": true}`
  - Response: `{"task_id": "<task-id>"}`
  - Example:
    curl -X POST http://localhost:8000/api/query/ \
      -H "Content-Type: application/json" \
      -d '{"query": "What is Django?", "use_web_search": true}'
- GET /health/: Check the health of critical components (database, Redis, Celery, OpenAI, Tavily).
  - Response:
    ```json
    {
      "status": "healthy",
      "components": {
        "database": {"status": "healthy", "error": null},
        "redis": {"status": "healthy", "error": null},
        "celery": {"status": "healthy", "error": null},
        "openai_api": {"status": "healthy", "error": null},
        "tavily_api": {"status": "healthy", "error": null}
      }
    }