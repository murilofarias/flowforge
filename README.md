# FlowForge

<p align="center">
  <strong>Visual workflow automation for modern B2B SaaS — drag, drop, automate.</strong>
</p>

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/python-3.11-blue">
  <img alt="fastapi" src="https://img.shields.io/badge/FastAPI-0.110-009688">
  <img alt="react" src="https://img.shields.io/badge/React-18-61dafb">
  <img alt="typescript" src="https://img.shields.io/badge/TypeScript-5-3178c6">
  <img alt="celery" src="https://img.shields.io/badge/Celery-5-a9dc76">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="ci" src="https://img.shields.io/badge/CI-passing-brightgreen">
</p>

FlowForge is an n8n-style visual workflow builder designed as a polished portfolio piece. It ships a
production-shaped microservice split (FastAPI + Celery worker + React Flow editor), a pastel playful-technical
UI, and a clean execution engine that walks node graphs topologically with fixture-mode-aware integrations
for HubSpot, Salesforce, Slack, and OpenAI.

## Features

- **Drag-and-drop editor** built on React Flow with category-colored node cards, minimap, grid background, and a Figma/Retool-inspired inspector.
- **Typed workflow schema** validated with Pydantic v2; nodes expose JSON schemas consumed by the dynamic inspector form.
- **Async execution** via Celery + Redis with per-node logs, input/output capture, topological resolution, branching, and filter short-circuit.
- **11 built-in node types** across Triggers, Actions, Transform, Logic, and AI categories.
- **Live run status** polling with a timeline of node events.
- **Webhook + cron triggers** with signature verification hooks.
- **Fixture mode** (`FIXTURE_MODE=true`) — every external integration has a deterministic simulated response, so the demo runs offline.
- **Dockerized** with a single `docker-compose up`.

## Architecture

```mermaid
flowchart LR
    subgraph Client
        W[web - React + Vite]
    end
    subgraph Backend
        A[api - FastAPI]
        Q[redis]
        K[worker - Celery]
        P[(postgres)]
    end
    W -- REST --> A
    A -- SQLAlchemy --> P
    A -- enqueue --> Q
    Q -- consume --> K
    K -- SQLAlchemy --> P
    K -. shares app.services .-> A
```

Shared domain code (models, schemas, node services) lives in `api/app/` and is imported directly by the
worker container via a mounted volume + shared Python path. This keeps the split genuine (separate
containers, separate processes) without duplicating business logic.

## Screenshots

| Dashboard | Editor | Inspector |
| --- | --- | --- |
| ![dashboard](docs/screenshots/dashboard.png) | ![editor](docs/screenshots/editor.png) | ![inspector](docs/screenshots/inspector.png) |

| Run detail | Palette |
| --- | --- |
| ![run-detail](docs/screenshots/run-detail.png) | ![palette](docs/screenshots/palette.png) |

## Local setup

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Web: http://localhost:5173
- API docs: http://localhost:8000/docs

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://flowforge:flowforge@postgres:5432/flowforge` | Postgres DSN |
| `REDIS_URL` | `redis://redis:6379/0` | Broker + result backend |
| `FIXTURE_MODE` | `true` | Bypass external calls with canned responses |
| `OPENAI_API_KEY` | — | Optional, used when `FIXTURE_MODE=false` |
| `HUBSPOT_TOKEN` | — | Optional |
| `SALESFORCE_TOKEN` | — | Optional |
| `SLACK_WEBHOOK_URL` | — | Optional |
| `WEBHOOK_SIGNING_SECRET` | `dev-secret` | Verifies inbound webhook HMAC |
| `API_CORS_ORIGINS` | `http://localhost:5173` | Comma-separated origins |

## API reference

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/workflows` | List workflows |
| POST | `/api/workflows` | Create workflow |
| PATCH | `/api/workflows/{id}` | Update workflow graph/metadata |
| DELETE | `/api/workflows/{id}` | Delete workflow |
| POST | `/api/workflows/{id}/run` | Enqueue a run, returns `run_id` |
| GET | `/api/runs` | List runs (filter by `workflow_id`, `status`) |
| GET | `/api/runs/{id}` | Run detail with per-node logs |
| GET | `/api/nodes/catalog` | Available node types + JSON schemas |
| POST | `/api/webhooks/{trigger_id}` | External webhook trigger entrypoint |

## Deployment

- Images built and pushed via `.github/workflows/deploy.yml` on tag pushes.
- Target platform: any container host (Fly.io, Render, ECS). Postgres + Redis managed.
- `alembic upgrade head` runs on api container start.
- Horizontal scaling: add worker replicas; API is stateless.

## CI/CD

- `.github/workflows/ci.yml` runs `ruff` + `pytest` for Python and `eslint` + `vite build` for the web.
- `deploy.yml` builds and pushes `ghcr.io/<org>/flowforge-{api,worker,web}` on tag pushes.

## Security notes

- **Workflow sandboxing** — the Transform node uses a whitelisted expression evaluator (no `eval`); HTTP nodes enforce egress allow-listing via `HTTP_ALLOWED_HOSTS`.
- **Secret handling** — node configs flagged `secret: true` in the catalog are stored encrypted at rest (Fernet) and masked in API responses.
- **Webhook signatures** — inbound webhooks verify `X-FlowForge-Signature` with HMAC-SHA256 against `WEBHOOK_SIGNING_SECRET`.
- **Connection pooling** — SQLAlchemy engine configured with `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True` for Postgres resilience.
- **CORS** — explicit allow-list via `API_CORS_ORIGINS`; no wildcard in production.

## License

MIT
