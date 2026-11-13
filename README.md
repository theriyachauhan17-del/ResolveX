
# ResolveX — Incident & SLA Management System

ResolveX is a multi-tenant Incident and Support Ticket Management System built using Python, Django, Django REST Framework, and PostgreSQL.

It enables multiple organizations to manage support incidents through secure REST APIs and a web-based interface. The system implements organization-level data isolation, role-based access control, JWT authentication, and configurable Service Level Agreement (SLA) policies.

The application supports ticket lifecycle management, SLA deadline calculation, response tracking, resolution tracking, and API documentation.

**Live Demo:** https://resolvex-web.onrender.com

**GitHub Repository:** https://github.com/theriyachauhan17-del/ResolveX

---

## Features

### 1. Authentication and Authorization
- Custom Django user model.
- JWT access and refresh token authentication.
- Role-based access control.
- Organization-based user membership.
- Permission-controlled ticket operations.

### 2. Multi-Tenant Architecture
- Multiple organizations supported.
- Organization-level ticket data isolation.
- Organization-scoped access permissions.
- Superuser cross-organization access.

### 3. Incident and Ticket Management
- Create, retrieve, update, and delete tickets through REST APIs.
- Ticket priority management:
  - LOW
  - MEDIUM
  - HIGH
  - CRITICAL
- Ticket status management:
  - OPEN
  - IN_PROGRESS
  - RESOLVED
  - CLOSED
- Ticket search and filtering.
- Ticket assignment and organization-based validation.

### 4. SLA Management
- Configurable SLA policies for each organization.
- Priority-based response deadlines.
- Priority-based resolution deadlines.
- Automatic deadline generation during ticket creation.
- First response timestamp tracking.
- Resolution timestamp tracking.
- Response SLA status monitoring.
- Resolution SLA status monitoring.

### 5. Web-Based Interface
- Login and logout functionality.
- Ticket listing and search.
- Status and priority filtering.
- Ticket creation form.
- Ticket detail page.
- Ticket status management.

### 6. API Documentation and Testing
- Swagger API documentation.
- Redoc API documentation.
- OpenAPI schema generation.
- Automated Django test suite.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| Authentication | Simple JWT |
| API Documentation | DRF Spectacular |
| Frontend | HTML, CSS, Bootstrap, Django Templates |
| Testing | Django Test Framework |
| Deployment | Render |
| Version Control | Git, GitHub |

---

## Project Structure

```text
ResolveX/
│
├── accounts/          # Custom user model and authentication
├── organizations/     # Organization management
├── tickets/           # Ticket models, serializers, APIs and permissions
├── sla/               # SLA policies and management APIs
├── frontend/          # Web interface, forms and views
├── config/            # Django project configuration
│
├── staticfiles/       # Collected static assets
├── manage.py
├── requirements.txt
├── build.sh
└── README.md
```

---

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

Create a `.env` file in the project root.

Configure the environment variables required by `config/settings.py`, including your Django secret key and local PostgreSQL database settings.

Use your own local database credentials.

Never commit `.env`, database URLs, passwords, or production secrets to GitHub.

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

Open:

- Application: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Tickets: http://127.0.0.1:8000/tickets/
- Django Admin: http://127.0.0.1:8000/admin/

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtain JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh access token |

### Ticket Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tickets/` | List tickets |
| POST | `/api/tickets/` | Create ticket |
| GET | `/api/tickets/<id>/` | Retrieve ticket |
| PUT/PATCH | `/api/tickets/<id>/` | Update ticket |
| DELETE | `/api/tickets/<id>/` | Delete ticket |

### SLA Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/sla/policies/` | List SLA policies |
| POST | `/api/sla/policies/` | Create SLA policy |
| GET | `/api/sla/policies/<id>/` | Retrieve SLA policy |
| PUT/PATCH | `/api/sla/policies/<id>/` | Update SLA policy |
| DELETE | `/api/sla/policies/<id>/` | Delete SLA policy |

SLA policy management is subject to configured authentication and permissions.

### API Documentation

| Resource | Endpoint |
|---|---|
| OpenAPI Schema | `/api/schema/` |
| Swagger UI | `/api/docs/` |
| Redoc | `/api/redoc/` |

---

## SLA Workflow

When a ticket is created, ResolveX checks for an active SLA policy matching the ticket's organization and priority.

The system then calculates:

- Response deadline.
- Resolution deadline.

During ticket processing:

1. A ticket is created with OPEN status.
2. When moved to IN_PROGRESS, the first response timestamp is recorded.
3. When moved to RESOLVED, the resolution timestamp is recorded.
4. Reopening a resolved ticket preserves the previous resolution timestamp until another resolution occurs.

The API also provides response and resolution SLA status information.

---

## Automated Testing

Run the complete test suite:

```powershell
python manage.py test
```

**Latest verified result:**

- 37 tests discovered.
- 37 tests passed.
- Django system checks passed.
- No test failures.

---

## Security and Access Control

- Organization-level data isolation.
- Role-based access permissions.
- JWT authentication.
- Organization-scoped ticket access.
- Assignment validation.
- Environment-based configuration for sensitive credentials.
- Production HTTPS support through Render.

---

## Deployment

ResolveX is deployed using Render.

**Live Application:** https://resolvex-web.onrender.com

The production environment uses PostgreSQL.

---

## Project Status

| Component | Status |
|---|---|
| Django Backend | Implemented |
| REST APIs | Implemented |
| PostgreSQL Integration | Implemented |
| JWT Authentication | Implemented |
| Role-Based Access | Implemented |
| Multi-Tenant Architecture | Implemented |
| SLA Management | Implemented |
| Frontend Interface | Implemented |
| API Documentation | Configured |
| Automated Tests | 37 Passed |
| Deployment | Live |

---

## Author

**Riya Chauhan**

Python Developer | Django | Django REST Framework | PostgreSQL

GitHub: https://github.com/theriyachauhan17-del
