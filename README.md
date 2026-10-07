# Skill Swap Freelancer Website

**Find the right talent by skill, not just by profile.**

Skill Swap is a full-stack freelancer marketplace built with Flask. Clients can search for freelancers by skills, compare matches, and send project requests. Freelancers can create profiles, list skills, and showcase portfolio projects. Admins can manage the skill catalog and verify freelancers’ skills.

## Features

- **Accounts and roles:** Register and sign in as a client or freelancer. Admin pages are restricted to admin accounts.
- **Freelancer profiles:** Add a professional title, introduction, location, experience level, hourly rate, availability, and skills.
- **Skill-based discovery:** Browse and filter freelancers by name, skill, experience, availability, and hourly rate.
- **Skill matching:** Select skills your project needs and view freelancers ranked by skill overlap and verified skills.
- **Project requests:** Clients can send project details, budget, deadline, and relevant skills. Freelancers can accept or reject requests and mark accepted work as completed.
- **Portfolios:** Freelancers can add projects with descriptions, technologies, and links.
- **Admin tools:** Manage users and skills, verify freelancer skills, and review project requests and contact messages.
- **Contact form:** Visitors can send a message through the website.
- **Sample data:** The app creates a local SQLite database and adds sample freelancers, skills, portfolios, and a project request on first run.

## How skill matching works

1. A client selects one or more required skills.
2. The app finds freelancers who have at least one of those skills.
3. Each match gets a percentage based on how many of the selected skills they have.
4. Verified matching skills provide a small ranking bonus, so freelancers with verified expertise appear higher when skill overlap is similar.

The match percentage shows skill overlap. The verified-skill count is displayed separately.

## Run locally

You’ll need **Python 3.10 or newer**.

### Windows

Open PowerShell in the project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell does not allow environment activation, use the environment’s Python directly:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

### macOS or Linux

Open a terminal in the project folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Once the server starts, visit **http://127.0.0.1:5000** in your browser. Keep the terminal open while using the website. Press **Ctrl+C** in the terminal to stop it.

The database file is created locally when the app runs.

## Tech stack

| Technology | Used for |
|---|---|
| Python | Application and matching logic |
| Flask | Web routes, forms, and JSON API |
| Flask-SQLAlchemy | Database models and queries |
| SQLite | Local database |
| Flask-Login | Login sessions and access control |
| Werkzeug | Password hashing |
| HTML and Jinja | Page structure and server-rendered templates |
| CSS | Styling and responsive layouts |
| JavaScript | Dynamic skill matching |
| Bootstrap 5 | Responsive layout components and utilities |

## API endpoints

The app includes JSON endpoints used by the website:

- `GET /api/skills` — list available skills
- `GET /api/freelancers` — list active freelancer profiles
- `GET /api/freelancers/<id>` — retrieve a freelancer profile
- `POST /api/freelancers/match` — find and rank matches for selected skills
- `POST /api/project-requests` — create a project request for a freelancer

The matching page sends its selected skills to Flask with JavaScript `fetch()` and displays the response dynamically.

## Project structure

```text
skill-swap/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   ├── app.js
│   └── style.css
└── templates/
    ├── admin.html
    ├── auth.html
    ├── base.html
    ├── browse.html
    ├── contact.html
    ├── dashboard.html
    ├── error.html
    ├── home.html
    ├── info.html
    ├── portfolio.html
    ├── profile.html
    ├── request_detail.html
    ├── request_form.html
    ├── settings.html
    └── skills.html
```

## Screenshots

<img width="1896" height="912" alt="Screenshot 2026-10-07 194418" src="https://github.com/user-attachments/assets/aac60837-5f36-40d9-a516-a0ee0858ff19" />
<img width="1897" height="906" alt="Screenshot 2026-10-07 194359" src="https://github.com/user-attachments/assets/338f13e2-eba1-49f8-bf12-c203d6d4621b" />
<img width="1901" height="911" alt="Screenshot 2026-10-07 194314" src="https://github.com/user-attachments/assets/8d794058-1c47-4382-a18b-b24a87ff28ea" />
<img width="1902" height="911" alt="Screenshot 2026-10-07 194254" src="https://github.com/user-attachments/assets/e0b52e05-65c9-462e-a0a6-107deae044d7" />



## Project scope

Skill Swap is a learning and portfolio project. It demonstrates freelancer discovery, profiles, skill matching, project requests, and role-based dashboards. It does not currently include payments, built-in chat, file uploads, or automated skill exams.
