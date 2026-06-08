CELERY REQUIREMENTS

Add:

backend/celery.py

Worker container:

celery -A config worker

Use cases:

appointment reminders
email notifications
sms notifications
report generation
billing jobs

---

AUTHENTICATION ARCHITECTURE

users app must support:

custom user model
roles
staff vs client distinction
multi-clinic membership support

Must allow future support for:

JWT auth
session auth
mobile app tokens
