### Mechanic Shop API

Flask REST API for a mechanic shop with customers, mechanics, service tickets, and inventory. Includes JWT auth, rate limiting, and caching.

## Setup
- Python 3.9+
- Install deps: `pip install -r requirements.txt`
- Configure `config.py` (DB URI, secret key, rate limits, cache)
- Run: `python server.py` (defaults to port 5000)

## Auth
- Customer login: `POST /customers/login` → returns `auth_token`
- Send protected requests with header `Authorization: Bearer <auth_token>`

## Key Endpoints
- Customers: `POST /customers` (create, rate limited), `GET /customers` (paginated, cached), `PUT /customers/`, `DELETE /customers/`, `GET /customers/<id>`
- Mechanics: `POST /mechanics`, `GET /mechanics`, `GET /mechanics/<id>` (cached), `PUT /mechanics/<id>`, `DELETE /mechanics/<id>`, `GET /mechanics/top-by-tickets`
- Service Tickets: `POST /tickets/`, `GET /tickets/` (cached), `GET /tickets/my-tickets` (auth), `PUT/DELETE /tickets/<id>` (auth), `PUT /tickets/<id>/assign-mechanic/<mechanic_id>` (auth), `PUT /tickets/<id>/remove-mechanic/<mechanic_id>` (auth), `PUT /tickets/<id>/add-part/<part_id>` (auth), `PUT /tickets/<id>/edit` (add/remove mechanics)
- Inventory: `POST /inventory`, `GET /inventory`, `GET /inventory/<id>`, `PUT /inventory/<id>`, `DELETE /inventory/<id>`

## Notes
- Rate limiting via Flask-Limiter (per-route decorators, default in `config.py`)
- Caching via Flask-Caching (applied to common read endpoints)
- JWTs via helpers in `App/utils/util.py` (1-hour expiry)
