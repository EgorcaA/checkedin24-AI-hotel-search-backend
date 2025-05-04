# Welcome to checkedin24-AI-hotel-search-backend project

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- ✅ Tests with [Pytest](https://pytest.org).
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

**_Run server_**

**Local run**

```sh
source ./venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
pip install pre-commit
uvicorn app.main:app --reload
curl "http://localhost:8000/api/hotels?prompt=I%20want%20a%20hotel%20with%20swimming%20pool"
```

**Testing**

```sh
pytest tests/test_hotels.py -v
```

**Single container with docker**

```sh
docker build -t checkedin24-backend ./backend # Build the image

docker run -p 8000:8000 checkedin24-backend # should not work wo API KEY

docker run -p 8000:8000 -e OPENAI_API_KEY=<APIKEY> checkedin24-backend # Run the container

docker system prune -a --volumes # remove images
```

**Docker-compose option**

```sh

docker-compose up # Start all services

docker-compose up -d # Start in detached mode (background)

docker-compose down # Stop services (--remove-orphans)

docker-compose logs -f # View logs

```

**Talking to container**

```sh
docker ps # Running dockers, get (example)6ad4631b8626 (local)
docker exec -it 6ad4631b8626 bash # Run cmd of container (local)
flyctl ssh console -a checkedin24-ai-hotel-search-backend # same on fly.io

```
