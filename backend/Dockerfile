FROM python:3.12-slim

WORKDIR /repo/backend

# Copy only requirements first for layer caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

ENV FLASK_APP=app.py
# /repo is mounted at runtime (volume); PYTHONPATH lets "from backend.x" resolve
ENV PYTHONPATH=/repo

EXPOSE 5000

# Los seeds (idempotentes, nunca duplican) se re-ejecutan en cada arranque del contenedor para
# que un `docker compose down -v` (borra el volumen de Postgres) no pierda clientes/proyectos/
# equipos de prueba en ningun ambiente (dev, sywork_test, sywork_prod) — ver specs 026/029.
CMD ["sh", "-c", "alembic upgrade head && python -m backend.scripts.seed_clients_aris_vaxthera && python -m backend.scripts.seed_dev_users && flask run --host=0.0.0.0 --port=5000 --reload"]
