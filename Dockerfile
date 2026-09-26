# Built by .github/workflows/deploy.yml (context ., file Dockerfile) and pushed
# to Artifact Registry. Adapted from the fleet's python stack pack.
#
# Deviations from the pack, and why:
#   - replaces the generator's poetry/Python-3.11 Dockerfile, which hardcodes port
#     8080, ignores $PORT, and installs from pyproject - bypassing the httpx<0.28
#     pin in requirements.txt that this app needs to import at all.

FROM python:3.12-slim AS build
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt ./
RUN python -m venv /venv \
 && /venv/bin/pip install -r requirements.txt

FROM python:3.12-slim AS runtime
ARG BUILD_ID=""
WORKDIR /app
ENV PATH=/venv/bin:$PATH PYTHONUNBUFFERED=1 PORT=8000 BUILD_ID=$BUILD_ID
RUN useradd -r -u 10001 app
COPY --from=build /venv /venv
COPY --chown=app:app . .
USER app
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.server:app --host 0.0.0.0 --port ${PORT}"]
