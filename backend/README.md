# FastAPI Backend

minimal fastapi backend for hackathon ai endpoints.

## setup

1. create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on windows: venv\Scripts\activate
```

2. install dependencies:
```bash
pip install -r requirements.txt
```

3. create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. add your api keys to `.env`

## running

```bash
uvicorn main:app --reload
```

api will be available at `http://localhost:8000`

## endpoints

- `GET /` - health check
- `GET /health` - health check
- `POST /api/ai/generate` - example ai endpoint

## documentation

swagger ui: `http://localhost:8000/docs`
redoc: `http://localhost:8000/redoc`


