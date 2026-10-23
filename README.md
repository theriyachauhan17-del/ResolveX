# ResolveX — Multi-Tenant Ticket Management API

ResolveX is a Django REST Framework project for managing support tickets across multiple organizations. It includes organization-based user membership, role-based access, JWT authentication, and RESTful ticket operations.

## Features

- Custom user model with organization membership.
- User roles: Administrator, Manager, Support Agent, and Customer.
- Organization and ticket management.
- JWT access and refresh tokens.
- RESTful API endpoints for ticket creation, listing, retrieval, updating, and deletion.
- PostgreSQL database integration.
- Automated Django tests.
- API schema/documentation support through DRF Spectacular.

## Technology Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- django-filter
- DRF Spectacular

## Project Applications

- `accounts` — custom user model and user roles.
- `organizations` — organization management.
- `tickets` — ticket management APIs.
- `config` — project settings and URL configuration.

## Local Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ResolveX
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Configure the variables required by `config/settings.py`, including:

```dotenv
SECRET_KEY=replace-with-your-secret-key
DB_NAME=resolvex_db
DB_USER=postgres
DB_PASSWORD=replace-with-your-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Use your own local credentials. Never commit `.env` or real secrets to GitHub.

### 5. Run migrations

```powershell
python manage.py migrate
```

### 6. Create an administrator

```powershell
python manage.py createsuperuser
```

### 7. Start the development server

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser. The Django admin is normally available at `/admin/`.

## API Testing

Use Postman with a valid JWT access token.

| Operation | Method | Endpoint |
|---|---|---|
| Obtain tokens | POST | `/api/token/` |
| Refresh access token | POST | `/api/token/refresh/` |
| List tickets | GET | `/api/tickets/` |
| Create ticket | POST | `/api/tickets/` |
| Retrieve a ticket | GET | `/api/tickets/<id>/` |
| Update a ticket | PATCH | `/api/tickets/<id>/` |
| Delete a ticket | DELETE | `/api/tickets/<id>/` |

Authentication, permissions, and required request fields depend on the project's configuration.

## Run Automated Tests

```powershell
python manage.py test
```

The current development test run passed all 20 tests.

## Security Notes

- Keep `.env` out of version control.
- Use strong passwords and secret keys.
- Use HTTPS and production-safe settings when deployed.
- Verify organization-level access restrictions before production release.
- Do not use the Django development server in production.

## Project Status

Core ticket CRUD operations, JWT token generation and refresh, organization-access checks, and the current automated test suite have been exercised during development. Production deployment and configuration still require verification.

## Author

Developed as a Django REST Framework learning and portfolio project.