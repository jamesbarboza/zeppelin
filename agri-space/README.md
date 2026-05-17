# Agri-Space

Agricultural weather recommendation platform. Farmers pin or draw their plots on a map and get AI-powered activity recommendations (spray, irrigate, plant, harvest) based on a 7-day weather forecast.

**Stack:** Django 5 + PostGIS · React 18 + Vite · Open-Meteo · Claude Haiku

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in DB_PASSWORD, SECRET_KEY, ANTHROPIC_API_KEY
python manage.py migrate
python seed.py                # creates demo users and crop tags
python manage.py runserver    # http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

The Vite dev server proxies all `/api/*` requests to Django on port 8000.

---

## Test Credentials

| Role   | Email                   | Password     |
|--------|-------------------------|--------------|
| Farmer | farmer@demo.com         | farmer1234   |
| Admin  | admin@agrispace.com     | admin1234    |

The farmer account has a demo plot ("North Field") pre-created.

The admin account can access `/admin` for user management and analytics.

---

## Running Tests

```bash
cd backend && source venv/bin/activate
pytest -v
```

26 tests across auth, models, plots API, recommendations engine, and admin panel.

---

## Environment Variables

Copy `backend/.env.example` and fill in:

| Variable            | Description                          |
|---------------------|--------------------------------------|
| `SECRET_KEY`        | Django secret key                    |
| `DB_PASSWORD`       | PostgreSQL password                  |
| `DB_NAME`           | Database name (default: `agrispace`) |
| `DB_USER`           | Database user (default: `agrispace`) |
| `ANTHROPIC_API_KEY` | Required for LLM recommendations     |
| `GDAL_LIBRARY_PATH` | Path to libgdal (macOS: set via brew) |
| `GEOS_LIBRARY_PATH` | Path to libgeos (macOS: set via brew) |

On macOS with Homebrew:
```bash
GDAL_LIBRARY_PATH=$(brew --prefix gdal)/lib/libgdal.dylib
GEOS_LIBRARY_PATH=$(brew --prefix geos)/lib/libgeos_c.dylib
```
