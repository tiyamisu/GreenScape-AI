# Run Instructions

## 1. FastAPI (Backend)

Install dependencies:
```bash
pip install -r backend/requirements.txt
```

Run FastAPI server:
```bash
python -m uvicorn greenscape.api:app --app-dir backend --reload --port 8000
```

*Alternative (PowerShell):*
```powershell
$env:PYTHONPATH = "backend"
python -m uvicorn greenscape.api:app --reload
```

*Alternative (Linux / macOS):*
```bash
PYTHONPATH=backend python -m uvicorn greenscape.api:app --reload
```

FastAPI URLs:
- Base API: `http://127.0.0.1:8000`
- Swagger UI docs: `http://127.0.0.1:8000/docs`
- ReDoc docs: `http://127.0.0.1:8000/redoc`

---

## 2. Frontend (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

---

## 3. Tests (Optional)

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "backend"
python -m unittest discover -s backend/tests
```

**Linux / macOS (Bash):**
```bash
PYTHONPATH=backend python -m unittest discover -s backend/tests
```
