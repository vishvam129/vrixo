# Vrixo

**AI photo magic — enhance, restore, and transform your photos.**

Vrixo is an AI photo tool: upload a photo and remove its background, upscale it, restore faces, repair old photos, or remove unwanted objects.

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
- **Streamlit** web UI · **SQLite** for accounts and quotas
- **pytest** · ruff · Docker

## Planned

The roadmap below moves Vrixo from a single Streamlit app to a web product:

- [x] Stage 1: Background removal (local prototype)
- [x] Stage 2: Upscaling + face enhancement
- [x] Stage 3: Streamlit web UI, accounts, quotas
- [x] Stage 3.5: Real neural models — Real-ESRGAN, GFPGAN, LaMa
- [ ] Stage 4: FastAPI backend — upload / job / result endpoints, SQLAlchemy + PostgreSQL, Celery + Redis job queue
- [ ] Stage 5: Object storage (Cloudflare R2) and Supabase auth
- [ ] Stage 6: Next.js + Tailwind + shadcn/ui frontend
- [ ] Stage 7: Cloud deployment
- [ ] Stage 8: Payments · mobile app

---

## Project structure

```
vrixo/
├── ai/
│   ├── models/       # one module per pipeline + weights registry
│   └── utils/        # image loading / saving / resizing helpers
├── web/              # Streamlit app, auth, quotas, watermark, health
├── tests/            # pytest suite (+ fixtures)
├── docs/             # feature list, deployment notes
├── models_cache/     # downloaded weights (git-ignored)
└── Dockerfile
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
