# BACKEND

## TECH STACK 
- Django
- Django REST Framework
- PostgreSQL
- Celery

> NOTE: there is no need for cache since the app will have a low user volume

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

### BACKEND DOMAIN STRUCTURE RULES

Each Django app must contain (file.py → purpose):
models.py → database schema
serializers.py → DRF serializers
views.py → API endpoints
selectors.py → database query layer
services.py → business logic
tasks.py → Celery background jobs
tests/ → unit tests

### REQUIRED DJANGO APPS

users
services
appointments
availability
notifications
payments
analytics

### INTEGRATIONS

* Notifications:
    Email via provider
    SMS via providers:
        Twilio

* Integrations:
    Use Google Calendar API to sync the appointments with the staff google calendar app

---

### REST API Good Practices

* Design APIs around resources and nouns.
* Use HTTP methods according to their intended semantics.
* Version the API from the beginning.
* Return appropriate HTTP status codes.
* Implement pagination for collection endpoints.
* Support filtering, sorting, and searching.
* Maintain a consistent request and response structure.
* Validate all incoming data.
* Separate authentication from authorization.
* Protect sensitive data and internal implementation details.
* Ensure idempotency where applicable.
* Prevent N+1 database query issues.
* Use database indexes appropriately.
* Implement structured logging.
* Include request correlation ID accross the entire workflow.
* Apply rate limiting and throttling.
* Generate and maintain OpenAPI documentation.
* Keep business logic out of controllers/views.
* Use service layers for complex workflows.
* Apply repository or data access abstractions when beneficial.
* Use background workers for long-running tasks.
* Implement health check endpoints.
* Use database transactions for critical operations.
* Handle errors consistently across all endpoints.
* Define standard error codes and messages.
* Enforce HTTPS in all environments.
* Store secrets outside the codebase.
* Follow the principle of least privilege.
* Implement role-based or permission-based access control.
* Monitor performance metrics and latency.
* Track application errors and exceptions.
* Implement observability through logs, metrics, and tracing.
* Write automated unit tests.
* Write integration and end-to-end tests.
* Maintain backward compatibility whenever possible.
* Deprecate API features using a documented process.
* Apply input and output serialization consistently.
* Define clear timeout and retry strategies.
* Ensure API operations are resilient to failures.
* Maintain consistent naming conventions.
* Document breaking changes before release.
* Use configuration management for environment-specific settings.
* Follow secure coding practices throughout the codebase.
* Audit dependencies and keep them updated.
* Establish coding standards and code review processes.
* Design endpoints to be predictable and discoverable.
* Keep APIs simple and avoid unnecessary complexity.
* Measure, monitor, and continuously improve API reliability.
