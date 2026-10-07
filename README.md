# Skill Swap

A student-friendly Flask marketplace for skill-based freelancer discovery. Built with Flask, SQLAlchemy, Flask-Login, SQLite, Jinja templates, Bootstrap 5, and plain JavaScript.

## Run locally

1. Install Python 3.10+.
2. Create and activate a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install packages: `pip install -r requirements.txt`
4. Start: `python app.py`
5. Open `http://127.0.0.1:5000`. SQLite is created and seeded on first run.

Set `SECRET_KEY` to a private random value before deployment. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL to move to Postgres later. `Flask-Migrate` is included for future schema migrations; install/setup can be done with `flask --app app db init` and `flask --app app db migrate -m "describe change"` after configuring the CLI.

## Demo logins

Password for each account: `demo1234`

- Client: `client@skillswap.local`
- Admin: `admin@skillswap.local`
- Freelancer: `demo1@skillswap.local` through `demo10@skillswap.local`

Register your own accounts to try the full flows. Do not use demo credentials in production.

## Features

- Registration, secure Werkzeug password hashes, login/logout, role checks
- Client and freelancer dashboards, profile editing, skills, portfolio
- Public freelancer browsing and filters, skill matching JSON API, transparent verified-skill score
- Project requests and status changes; requests are visible only to participants/admin
- Admin user activation, skill catalog, skill verification, request and contact inbox
- Contact form, responsive layout, validation and friendly error pages

## Matching

The API accepts skill IDs or names at `POST /api/freelancers/match`. Match percentage is matched requested skills divided by requested skills. Ranking score adds a small 10% proportional bonus for verified matched skills, then sorts by score and overlap. The UI displays the match percentage and verified count separately.

## Project notes

The app intentionally keeps routes and data models in `app.py` so a beginner can trace each feature. For a larger deployment, split routes into Blueprints and add CSRF protection, email verification, rate limiting, logging, backups, and production server configuration. SQLite is suitable for local/student use. No payment processing or file uploads are included.
