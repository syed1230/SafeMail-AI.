Deployment notes (Render / Railway)

1) Ensure model files are included in the `model/` directory (e.g. `phishing_model.pkl`, `vectorizer.pkl`). The app uses absolute paths so cloud platforms load them correctly.

2) Environment variables
   - `APP_ENV=production` (set on the platform)
   - Optional: `PORT` (platform will set it automatically; default 5000 locally)
   - Optional local debugging: create a `.env` (copy `.env.sample`) and set `FLASK_DEBUG=1`

3) Start command
   - A `Procfile` with `web: gunicorn app:app` is included and required by many PaaS providers. This uses Gunicorn as the WSGI server (ensure `gunicorn` is in `requirements.txt`).

4) Python runtime
   - `runtime.txt` pins to `python-3.11.4` for platforms that support it.

5) Local testing
   - Install dependencies: `pip install -r requirements.txt`
   - Run locally: `python app.py` (respects `APP_ENV` and `.env`)

6) Notes
   - Debug mode is disabled automatically in production (`APP_ENV=production`).
   - No Dockerfile is provided by design.
