**Development commands**

```sh
sudo apt install python3.12
sudo apt install python3.12-venv && python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt # if added packages
pre-commit install

pytest tests/test_hotels.py -v

git add *
git commit -m "new commit"
```

**Testing import**

```python
from app.process_hotels import find_matching_hotels
test_hotels = {"hotel1": {"name": "Test Hotel"}}
result = find_matching_hotels("test query", test_hotels)
```

flyctl auth login
