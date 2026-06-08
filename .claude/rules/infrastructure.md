INFRASTRUCTURE STRUCTURE

infra/

nginx/

```
nginx.conf
```

postgres/

redis/

scripts/

---

DOCKER SERVICES REQUIRED

backend
frontend
postgres
redis
nginx
celery worker

Example architecture:

browser --> nginx --> frontend
frontend --> django api
django --> postgres
django --> redis
celery --> redis

---

MAKEFILE COMMANDS REQUIRED

run
migrate
createsuperuser
makemigrations
shell
test

Commands must execute through docker-compose.

---

DEPLOYMENT TARGET COMPATIBILITY

Architecture must support deployment to Hetzner VPS 



