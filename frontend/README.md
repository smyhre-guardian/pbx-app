Phone List frontend

This is a tiny static frontend for the Phone List API in the project root.

How to use

- Start the backend API: python main.py (the API runs at http://127.0.0.1:8000 by default)
- Open the UI directly: open frontend/index.html in your browser.
  - Some browsers block fetch requests from file:// pages; if that happens, run a static server:

  python -m http.server 5500 --directory frontend

  and open http://127.0.0.1:5500

Configuration

If your API runs on a different host/port, edit `frontend/app.js` and change `baseUrl`.
