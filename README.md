# Vrixo

**AI photo magic — enhance, restore, and transform your photos.**

Vrixo is an AI-powered photo platform where users can upload any photo and get instant magic: background removal, HD upscaling, face enhancement, old photo restoration, colorization, object removal, and more — all in one clean tool.

---

## Features (Planned)

- **Background Removal** — One-click transparent backgrounds
- **HD Upscaling** — Turn blurry photos into crystal-clear 4K
- **Face Enhancement** — Sharpen and clean up faces automatically
- **Photo Colorization** — Bring old black & white photos to life
- **Object Removal** — Remove photobombers, unwanted items, clutter
- **Passport Photo Generator** — Correct format for any country
- **AI Headshots** — Turn selfies into professional photos
- **Smart Restoration** — Repair damaged, torn, or faded photos

---

## Tech Stack

**Frontend**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui

**Backend**
- Python 3.11+
- FastAPI
- SQLAlchemy + PostgreSQL
- Celery + Redis

**AI / ML**
- PyTorch
- HuggingFace Transformers & Diffusers
- OpenCV
- Real-ESRGAN, GFPGAN, RemBG, LaMa

**Infrastructure**
- Supabase (Auth + DB)
- Cloudflare R2 (Storage)
- Vercel (Frontend hosting)
- HuggingFace Spaces (GPU inference)
- Razorpay (Payments)

---

## Project Structure

```
vrixo/
├── web/              # Next.js web app (frontend)
├── backend/          # FastAPI server (API + auth + DB)
├── ai/               # AI models and inference pipelines
│   ├── models/       # Model implementations
│   └── utils/        # Image processing utilities
├── tests/            # Tests for backend and AI
├── docs/             # Project documentation
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git

### Setup

```bash
# Clone the repo
git clone git@github.com:vishvam129/vrixo.git
cd vrixo

# Set up Python environment for AI
python3 -m venv venv
source venv/bin/activate
pip install -r ai/requirements.txt

# Run the first AI feature (background removal)
python ai/models/background_removal.py
```

---

## Roadmap

- [ ] Stage 1: Background removal (local prototype)
- [ ] Stage 2: HD upscaling + face enhancement
- [ ] Stage 3: Streamlit web UI
- [ ] Stage 4: Next.js frontend
- [ ] Stage 5: FastAPI backend with user auth
- [ ] Stage 6: Cloud deployment
- [ ] Stage 7: Payment integration
- [ ] Stage 8: Mobile app (React Native)

---

## License

MIT License — see [LICENSE](./LICENSE) file for details.

---

## Author

Built by [@vishvam129](https://github.com/vishvam129)
