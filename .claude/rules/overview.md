# PROJECT GOAL

Create a production-ready monorepo structure for a SaaS-ready aesthetic single-clinic booking web application and a correspondent back-office using:

## Backend:

* Django
* Django REST Framework
* PostgreSQL
* Redis
* Celery

## Frontend:

* Next.js (React using typescript)
* TanStack Query
* FullCalendar

## Infrastructure:

* Docker
* NGINX reverse proxy
* S3-compatible media storage support (future-ready)

## System requirements (high level):

* single clinic architecture with multiple staff workers
* handle concurrent booking by clients
* scheduling/editing services and workflows
* authentication roles (admin, clients and staff)
* background jobs (notifications to the staff to and reminders)
* cron jobs (monthly reports of services and money made)
* independent frontend deployment capability (client app and backoffice for staff and admin)
* compatibility and responsiveness across various devices (computers, ipads, android tablets, iphones and android phones)
* containerized local development

IMPORTANT: Use a domain-driven backend structure and feature-based frontend structure.

---

## MONOREPO ROOT STRUCTURE

beauty-studio/
    backend/
    frontend/
    infra/
    docker-compose.yml
    .env
    .gitignore
    Makefile
    README.md

---

FINAL REQUIREMENT

Generate:

directory structure
starter configuration files
docker-compose configuration
Django project bootstrap
Next.js bootstrap
Celery setup scaffold
NGINX scaffold
environment variable placeholders

The result should be a clean production-grade starter monorepo scaffold. 
If you need any values or have any questions before starting implementation ask first.
