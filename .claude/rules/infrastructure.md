INFRASTRUCTURE STRUCTURE

infra/

nginx/

```
nginx.conf
```

postgres/

scripts/

---

DOCKER SERVICES REQUIRED

backend
frontend
postgres
nginx
celery worker

Example architecture:

browser --> nginx --> frontend
frontend --> django api
django --> postgres

---

MAKEFILE COMMANDS REQUIRED

run
migrate
makemigrations
shell
test

Commands must execute through docker-compose.

---

DEPLOYMENT TARGET COMPATIBILITY

Architecture must support deployment to Hetzner VPS 



