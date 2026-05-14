# Agri-Space: Agricultural Weather Recommendation Platform

**Date:** 2026-05-14
**Stack:** Django REST Framework + React (Vite) + PostgreSQL + PostGIS
**Scope:** Multi-user platform that gives farmers weather-based agricultural activity recommendations for their plots of land.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    React SPA (Vite)                  │
│  Map (Leaflet)  │  Dashboard  │  Activity Feed       │
└────────────────────────┬────────────────────────────┘
                         │ REST (JWT)
┌────────────────────────▼────────────────────────────┐
│                  Django + DRF                        │
│  Auth  │  Plots API  │  Weather API  │  Reco Engine  │
└──────────────┬──────────────────────────────────────┘
               │ HTTP (on-demand)
┌──────────────▼──────────────┐    ┌───────────────────┐
│   Open-Meteo Free API        │    │   PostgreSQL       │
│  (forecast + historical)     │    │  Users/Plots/Crops │
└──────────────────────────────┘    └───────────────────┘
```

- React SPA communicates with Django over REST using JWT auth
- Django fetches weather from Open-Meteo on-demand and caches responses for 1 hour using the `WeatherCache` DB model (no Redis required — DB cache survives restarts and is shared across workers)
- LLM-powered recommendation engine lives as a Python module inside Django (`recommendations/engine.py`)
- PostgreSQL + PostGIS stores users, farm plots as GeoJSON, crop tags, and weather cache
- Single Django process — no Celery, no Redis, no microservices

---

## 2. Data Models

### User
| Field | Type | Notes |
|---|---|---|
| id | UUID | |
| email | string | unique, used for login |
| password | hashed | Django auth |
| farm_name | string | optional display name |
| role | enum | `farmer` or `admin` |
| is_active | bool | admins can deactivate |
| created_at | datetime | |

### Plot
| Field | Type | Notes |
|---|---|---|
| id | UUID | |
| owner | FK → User | |
| name | string | e.g. "North Field" |
| geometry | GeoJSON | Point (pin) or Polygon (boundary) |
| area_hectares | float | computed from geometry on model save |
| crop_tags | M2M → CropTag | |
| created_at | datetime | |

### CropTag
| Field | Type | Notes |
|---|---|---|
| id | UUID | |
| name | string | e.g. "Maize", "Wheat" |
| category | enum | `row_crop / horticulture / orchard / pasture / other` |

### WeatherCache
| Field | Type | Notes |
|---|---|---|
| id | UUID | |
| latitude | float | rounded to 2 decimal places (~1km grid) |
| longitude | float | rounded to 2 decimal places |
| fetched_at | datetime | |
| expires_at | datetime | fetched_at + 1 hour |
| forecast_json | JSON | raw 7-day Open-Meteo response |

### AnalyticsSnapshot (admin-facing, computed daily)
| Field | Type | Notes |
|---|---|---|
| id | UUID | |
| date | date | one row per day |
| total_users | int | |
| active_users_7d | int | users who loaded dashboard in last 7 days |
| total_plots | int | |
| recommendations_generated | int | counts unique LLM calls (cache misses only) |
| top_crop_tags_json | JSON | top 10 crop tags by plot count |

---

## 3. UI Layout

### Overall Page Structure
- **Map on top** (hero, ~50% viewport height) — farmer selects plot here
- **Recommendations panel below** — scrolls vertically, shows recommendation cards for selected plot

### Map Interactions
- Default: farmer can drop a pin anywhere on the map to define a plot location
- Optional refinement: switch to polygon draw mode to trace the exact field boundary
- Both modes supported — plot starts as a pin, can be upgraded to a polygon later
- Leaflet.js for the map, `leaflet-draw` plugin for polygon drawing

### Recommendation Cards
Each card shows:
- **Status colour:** 🟢 Green (good) / 🟡 Amber (caution) / 🔴 Red (hold)
- **Title:** Short action-oriented headline (e.g. "Good spraying conditions today")
- **Reason:** One sentence explaining the weather basis

Cards are stacked vertically, ordered by severity (red first).

---

## 4. Recommendation Engine

**Module:** `recommendations/engine.py`

**Flow:**
```
Plot selected
  → Fetch Open-Meteo 7-day forecast for plot coordinates
  → Check WeatherCache (1h TTL, keyed by rounded lat/lng + date)
  → Build LLM prompt with forecast JSON + crop tags + date + hemisphere (derived from plot latitude: positive = northern, negative = southern)
  → Call Claude API (claude-haiku-4-5) with structured output via tool use
  → Cache LLM response alongside weather data
  → Return recommendation cards to frontend
```

**Open-Meteo variables used:**
- `precipitation_sum` — rain forecast (mm/day)
- `wind_speed_10m_max` — wind speed (km/h)
- `relative_humidity_2m_max` — humidity (%)
- `soil_moisture_0_to_1cm` — soil wetness
- `temperature_2m_min` / `temperature_2m_max` — frost/heat risk
- `et0_fao_evapotranspiration` — irrigation demand indicator

**LLM setup:**
- Model: `claude-haiku-4-5` (cost-efficient, fast)
- System prompt: agronomist persona + output schema definition
- Structured output enforced via Claude tool use to avoid parsing failures
- Crop tags included in prompt for crop-aware recommendations

**Output schema per card:**
```json
{
  "activity": "spray | irrigate | plant | harvest",
  "status": "green | amber | red",
  "title": "Short headline",
  "reason": "One-sentence weather explanation"
}
```

**Caching:** LLM response cached for 1 hour per plot coordinates + date. Multiple farmers viewing the same plot area share one LLM call.

**Fallback:** If LLM call fails or times out, a minimal rule-based fallback runs against the weather data so the dashboard is never empty.

**Cost estimate:** ~$0.001 per unique plot/hour at Haiku pricing — affordable at early scale.

---

## 5. API Endpoints

### Auth
```
POST /api/auth/register/
POST /api/auth/login/          → returns JWT (stored in httpOnly cookie)
POST /api/auth/refresh/
```

### Plots
```
GET    /api/plots/             → list current farmer's plots
POST   /api/plots/             → create plot (geometry + crop tags)
GET    /api/plots/:id/
PATCH  /api/plots/:id/         → update name, geometry, crop tags
DELETE /api/plots/:id/
```

### Recommendations
```
GET    /api/plots/:id/recommendations/   → fetch + cache LLM recommendations for plot
```

### Crop Tags
```
GET    /api/crop-tags/         → list all tags (for autocomplete in UI)
```

### Admin (role=admin only)
```
GET    /api/admin/users/       → list users with search/filter
PATCH  /api/admin/users/:id/   → activate or deactivate user
GET    /api/admin/analytics/   → AnalyticsSnapshot data for charts
```

**Auth:** JWT tokens stored in `httpOnly` cookies (not localStorage) to prevent XSS. DRF `SimpleJWT` handles issuance and refresh. React silently refreshes on app load.

---

## 6. Frontend Pages

```
/login                  → Login / Register
/dashboard              → Map + plot selector (default landing after login)
/plots/new              → Create plot (map draw flow)
/plots/:id              → Plot detail + recommendation cards
/plots/:id/edit         → Edit plot geometry or crop tags
/admin                  → Admin: user list + analytics (admin role only)
```

---

## 7. Key Dependencies

### Backend (Python)
- `django` + `djangorestframework`
- `djangorestframework-simplejwt`
- `django.contrib.gis` + `psycopg2` + PostGIS
- `anthropic` (Claude API SDK)
- `httpx` (for Open-Meteo requests)

### Frontend (JS)
- `react` + `react-router-dom`
- `vite`
- `leaflet` + `react-leaflet` + `leaflet-draw`
- `axios` (API calls)
- `recharts` (admin analytics charts)

---

## 8. Out of Scope (v1)

- Push notifications / email alerts
- Historical recommendation logs / analytics per farmer
- Native mobile app
- Satellite imagery or NDVI overlays
- Multi-plot comparison view
- Celery background jobs / Redis (upgrade path for v2)
