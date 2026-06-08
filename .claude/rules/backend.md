# BACKEND

## TECH STACK 
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery

## STRUCTURE 

backend/
 ├── apps/
 │    ├── users/
 │    ├── services/
 │    ├── appointments/
 │    ├── billing/
 │    ├── notifications/
 │    └── reports/
 │
 ├── integrations/
 │    └── google_calendar/
 │    ├── mbway/
 | 
 | 
 ├── core/
 │    ├── settings.py
 │    └── tasks.py

backend/

config/
settings/
base.py
dev.py
prod.py
urls.py
asgi.py
wsgi.py

apps/

```
users/
clinics/
services/
appointments/
availability/
notifications/
```

common/

```
permissions.py
pagination.py
utils.py
constants.py
```

requirements/

```
base.txt
dev.txt
prod.txt
```

manage.py
Dockerfile

---

BACKEND DOMAIN STRUCTURE RULES

Each Django app must contain (file.py → purpose):
models.py → database schema
serializers.py → DRF serializers
views.py → API endpoints
selectors.py → database query layer
services.py → business logic
tasks.py → Celery background jobs
tests/ → unit tests

---

REQUIRED DJANGO APPS

users
clinics
services
appointments
availability
notifications
payments
analytics
