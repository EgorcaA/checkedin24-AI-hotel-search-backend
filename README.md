# Welcome to checkedin24-AI-hotel-search-backend project

**Run server**

Follow these steps:

```sh
source .venv/bin/activate  # Linux/macOS
pip install pre-commit
uvicorn app.main:app --reload
curl "http://localhost:8000/api/hotels?prompt=I%20want%20a%20hotel%20with%20swimming%20pool"
```

'''sh

# Build the image

docker build -t checkedin24-backend ./backend

# Run the container

docker run -p 8000:8000 checkedin24-backend
'''

'''sh

# Start all services

docker-compose up

# Start in detached mode

docker-compose up -d

# Stop services

docker-compose down

# View logs

docker-compose logs -f
'''
