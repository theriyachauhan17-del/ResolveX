# ResolveX — Multi-Tenant Ticket Management System

ResolveX is a multi-tenant support ticket management system built using Django and Django REST Framework. It enables multiple organizations to manage support tickets securely with organization-level data isolation, role-based access control, and JWT authentication.

The project includes RESTful APIs, a web-based interface, PostgreSQL database integration, and automated tests.

**Live Demo:** https://resolvex-web.onrender.com

**GitHub Repository:** https://github.com/theriyachauhan17-del/ResolveX

## Features

- Custom Django user model with organization membership.
- Role-based access control:
  - Administrator
  - Manager
  - Support Agent
  - Customer
- Multi-tenant organization management.
- Organization-level ticket isolation.
- Ticket creation, listing, retrieval, updating, and deletion through REST APIs.
- Ticket priority and status management.
- JWT authentication with access and refresh tokens.
- PostgreSQL database integration.
- Search and filtering functionality.
- Django admin integration.
- Automated test coverage.
- API schema and documentation support through DRF Spectacular.

## Technology Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Backend | Django |
| API | Django REST Framework |
| Database | PostgreSQL |
| Authentication | Simple JWT |
| Filtering | django-filter |
| API Documentation | DRF Spectacular |
| Frontend | Django Templates, HTML, CSS, Bootstrap |
| Deployment | Render |
| Version Control | Git and GitHub |

## Project Structure

- `accounts/` — Custom user model, authentication, and user roles.
- `organizations/` — Organization management and membership.
- `tickets/` — Ticket models, serializers, permissions, and APIs.
- `frontend/` — Web interface, forms, and frontend views.
- `config/` — Django project settings and URL configuration.

## Local Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/theriyachauhan17-del/ResolveX.git
cd ResolveX
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the environment variables required by `config/settings.py`.

Use your own local database credentials and Django secret key.

**Important:** Never commit `.env`, database credentials, or production secrets to GitHub.

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Create an administrator account

```powershell
python manage.py createsuperuser
```

### 7. Start the development server

```powershell
python manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

Django Admin:

http://127.0.0.1:8000/admin/

## API Testing

Use Postman to test the REST API endpoints with valid authentication credentials.

| Operation | Method | Endpoint |
|---|---|---|
| Obtain JWT tokens | POST | `/api/token/` |
| Refresh access token | POST | `/api/token/refresh/` |
| List tickets | GET | `/api/tickets/` |
| Create ticket | POST | `/api/tickets/` |
| Retrieve ticket | GET | `/api/tickets/<id>/` |
| Update ticket | PATCH | `/api/tickets/<id>/` |
| Delete ticket | DELETE | `/api/tickets/<id>/` |

Authentication, permissions, and required request fields depend on the API configuration.

## Run Automated Tests

Execute the Django test suite:

```powershell
python manage.py test
```

**Latest verified test result:** 27 tests passed successfully.

## Security and Access Control

- Organization-level data isolation.
- Role-based ticket access and management.
- JWT-based API authentication.
- Environment-based configuration for sensitive credentials.
- Production deployment using HTTPS.
- Database credentials and secret keys must remain private.

## Deployment

ResolveX is deployed on Render.

**Live Application:** https://resolvex-web.onrender.com

The production environment uses PostgreSQL and has successfully passed deployment and migration verification.

## Project Status

**Deployment:** Live

**Core functionality:** Implemented and tested

**Database:** PostgreSQL

**Automated tests:** 27 passed in the latest verified test run

**Production migration:** Verified

## Author

Developed by **Riya Chauhan** as a Python and Django REST Framework portfolio project.

GitHub: https://github.com/theriyachauhan17-del