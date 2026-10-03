# Vrixo

**AI photo magic — enhance, restore, and transform your photos.**

Vrixo is an AI photo tool: upload a photo and remove its background, upscale it, restore faces, repair old photos, or remove unwanted objects.

**Demo:** [vrixo-demo.vercel.app](https://vrixo-demo.vercel.app) — the real interface on one sample photo. Each result there was produced by the models in this repo and saved; the backend (PostgreSQL, Redis, and a worker that needs ~2 GB for the models) is not hosted, so nothing is processed live. Run the stack below to use your own photos.

---

## What works today

| Feature | Neural model | Fallback (no download needed) |
|---|---|---|
| Background removal | **rembg** — U²-Net, BiRefNet, ISNet (5 selectable models) | — |
| Upscaling 2× / 4× / 8× | **Real-ESRGAN x4** — RRDBNet implemented in PyTorch (`ai/models/realesrgan.py`), tiled for CPU | LANCZOS resampling |
| Face enhancement | **GFPGAN v1.4** — YuNet detection → landmark alignment → ONNX Runtime → feathered paste-back (`ai/models/gfpgan.py`) | Haar cascade + sharpening |
| Object removal | **LaMa** — TorchScript, mask-composited (`ai/models/lama.py`) | OpenCV TELEA inpainting |
| Old-photo restoration | — | OpenCV scratch repair + colour correction |

Every neural pipeline falls back to its classical implementation when its weights are not installed, so the app runs straight after `pip install`.

Also built: a Streamlit web UI with before/after comparison, email + password accounts (PBKDF2), daily usage quotas, watermarking, a health check, a Docker image, and a pytest suite.

## Tech stack (built)

- **Python 3.11+**, PyTorch, ONNX Runtime, OpenCV, Pillow, rembg
- **FastAPI** API · **SQLAlchemy 2 + PostgreSQL** (Alembic migrations) · **Celery + Redis** job queue
- **Next.js** + Tailwind + shadcn/ui frontend
- **Streamlit** web UI (standalone, SQLite accounts and quotas)
- **pytest** · ruff · Docker Compose

## Planned

The roadmap below moves Vrixo from a single Streamlit app to a web product:

- [x] Stage 1: Background removal (local prototype)
- [x] Stage 2: Upscaling + face enhancement
- [x] Stage 3: Streamlit web UI, accounts, quotas
- [x] Stage 3.5: Real neural models — Real-ESRGAN, GFPGAN, LaMa
- [x] Stage 4: FastAPI backend — upload / job / result endpoints, SQLAlchemy + PostgreSQL, Celery + Redis job queue
- [ ] Stage 5: Object storage (Cloudflare R2) and Supabase auth
- [x] Stage 6: Next.js + Tailwind + shadcn/ui frontend (sign in, upload, run a tool, compare, download, history)
- [ ] Stage 7: Cloud deployment
- [ ] Stage 8: Payments · mobile app

---

## Project structure

```
vrixo/
├── ai/
│   ├── models/       # one module per pipeline + weights registry
│   └── utils/        # image loading / saving / resizing helpers
├── backend/          # FastAPI app, SQLAlchemy models, Celery task, storage
├── frontend/         # Next.js + Tailwind + shadcn/ui web app
├── migrations/       # Alembic migrations
├── scripts/e2e.py    # end-to-end check against the running stack
├── web/              # Streamlit app, auth, quotas, watermark, health
├── tests/            # pytest suite (+ fixtures)
├── docs/             # feature list, deployment notes
├── models_cache/     # downloaded weights (git-ignored)
├── docker-compose.yml  # db + redis + migrate + api + worker
├── Dockerfile.backend
└── Dockerfile          # Streamlit image
```

---

## Getting started

```bash
git clone git@github.com:vishvam129/vrixo.git
cd vrixo

python3 -m venv .venv && source .venv/bin/activate
pip install -r ai/requirements.txt streamlit

# optional: download the neural model weights (~620 MB)
python -m ai.models.weights --download
python -m ai.models.weights              # show what is installed

streamlit run web/app.py                 # http://localhost:8501
```

No GPU is required. On CPU, Real-ESRGAN takes roughly a second per 192 px tile, so "auto" mode uses it for images up to 1024 px on the long side.

### Backend API (FastAPI + Celery)

Image processing is slow, so the API never does it in the request. It stores
the upload, writes a job row, publishes the job id to Redis and returns `202`;
a separate worker process runs the model and records the outcome in PostgreSQL.

```
client ──POST /uploads──▶ API ──▶ storage
client ──POST /jobs─────▶ API ──▶ PostgreSQL (job: queued) ──▶ Redis
                                        ▲                        │
client ──GET /jobs/{id}─▶ API ──────────┘        worker ◀────────┘
client ──GET /jobs/{id}/result ◀── storage ◀──── runs the model, marks succeeded / failed
```

```bash
docker compose up -d --build        # PostgreSQL, Redis, migrations, API, worker
python scripts/e2e.py               # sign up → upload → 3 jobs → download results
open http://127.0.0.1:58000/docs    # interactive API docs
docker compose down                 # stop (add -v to delete the data too)
```

| Endpoint | Purpose |
|---|---|
| `POST /auth/signup`, `POST /auth/login`, `GET /auth/me` | accounts (PBKDF2 passwords, JWT access tokens) |
| `POST /uploads` | store an image — validated from its bytes, size- and pixel-limited |
| `POST /jobs` | queue an operation: `remove_background`, `upscale`, `enhance_faces`, `restore`, `remove_object` |
| `GET /jobs`, `GET /jobs/{id}` | list / poll (`queued → running → succeeded \| failed`, with duration and error) |
| `GET /jobs/{id}/result` | download the result image |
| `GET /health` | liveness + database check |

Design notes:

- **Admission control.** Before a job is accepted the API checks the user's daily
  limit, their number of active jobs (`429`, `Retry-After`) and the global queue
  depth (`503`), so a burst cannot bury the single worker.
- **At-least-once delivery, exactly-once processing.** The worker acknowledges a
  message only after finishing (`acks_late`), so a crashed worker's job is
  redelivered; the `queued → running` transition is one conditional `UPDATE`, so a
  redelivered or duplicate message cannot run a job twice.
- **Failures are data.** A crashing model marks the job `failed` with the error;
  the worker keeps running. If Redis is unreachable the job is failed immediately
  instead of being left `queued` forever.
- **Parameters are validated at submission** (Pydantic, per operation), not in the worker.
- The compose stack binds only to `127.0.0.1` on non-default ports and caps each
  service's memory (worker: 3 GB, one job at a time).
- **Bounded worker memory.** The worker drops its cached models after every job
  (`ai/models/memory.py`); keeping all four loaded pushed it into its memory
  limit and made jobs swap.

Without Docker: `uvicorn backend.main:app --reload` uses SQLite, and
`VRIXO_CELERY_ALWAYS_EAGER=1` runs jobs inline — this is how the API tests run.

### Frontend (Next.js)

`frontend/` is a Next.js + Tailwind + shadcn/ui app that talks to the API:
sign in, drop a photo on the light table, pick one of the five tools, watch the
job move through the queue, compare before / after, download. Past jobs line
up as frames on a strip of film.

```bash
docker compose up -d                 # the API it talks to (http://127.0.0.1:58000)
cd frontend && pnpm install
pnpm dev                             # http://localhost:3000
```

`NEXT_PUBLIC_DEMO=1` builds the server-less sample demo (`frontend/src/lib/demo.ts`).
`NEXT_PUBLIC_API_URL` points it at a different API; `VRIXO_CORS_ORIGINS` on the
backend lists the origins allowed to call it.

### Command line

```bash
python -m ai.models.background_removal -i photo.jpg -o cutout.png
python -m ai.models.upscaler           -i photo.jpg -o big.png --scale 4 --engine realesrgan
python -m ai.models.face_enhance       -i photo.jpg -o faces.png
python -m ai.models.object_remove      -i photo.jpg -o clean.png --mask mask.png
```

### Tests

```bash
pip install -r requirements-dev.txt
pytest                 # unit tests — classical paths, no downloads needed
pytest -m models       # also run the real networks (needs the weights)
```

---

## Model licences

| Model | Source | Licence |
|---|---|---|
| Real-ESRGAN x4plus | xinntao/Real-ESRGAN | BSD-3-Clause |
| GFPGAN v1.4 | TencentARC/GFPGAN (ONNX export) | Apache-2.0 |
| YuNet face detector | opencv/opencv_zoo | MIT |
| LaMa (big-lama) | advimman/lama (TorchScript export) | Apache-2.0 |
| rembg models | danielgatis/rembg | MIT (model licences vary) |

Check each model's licence before commercial use.

## License

MIT License — see [LICENSE](./LICENSE) file for details.
