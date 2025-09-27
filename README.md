Phone List API
================

Simple FastAPI application to track a list of phone numbers.

Quick start
-----------

1. Create a virtual environment and install dependencies:

   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

2. Run the app:

   python main.py

3. Open http://127.0.0.1:8000/docs to use the interactive API docs.

Tests
-----

Run tests with pytest:

   .\.venv\Scripts\Activate.ps1; pytest -q

Frontend (optional)
-------------------

The `frontend/` folder was migrated to a Vite + Vue 3 app. To develop the frontend:

1. cd frontend
2. npm install
3. npm run dev

The dev server usually runs at http://localhost:5173
