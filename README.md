# Welcome to checkedin24-AI-hotel-search-backend project

**Run server**

Follow these steps:

```sh
source .venv/bin/activate  # Linux/macOS
pip install pre-commit
uvicorn app.main:app --reload
curl "http://localhost:8000/api/hotels?prompt=I%20want%20a%20hotel%20with%20swimming%20pool"
```
