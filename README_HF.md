---
title: Vrixo
emoji: ✨
colorFrom: purple
colorTo: pink
sdk: streamlit
sdk_version: 1.56.0
app_file: web/app.py
pinned: true
license: mit
short_description: AI photo magic — enhance, restore, and transform photos
---

# Vrixo

AI photo magic platform. Upload any photo to:

- ✂️ Remove backgrounds
- 🔍 Upscale to HD / 4K
- 😊 Enhance faces
- 🕰️ Restore old photos
- 🧽 Remove unwanted objects

Built with Streamlit + PyTorch + rembg. 100% free, no API keys needed.

## Deploy to HuggingFace Spaces

1. Create a new Space at https://huggingface.co/new-space
2. Choose **Streamlit** as the SDK
3. Rename this file to `README.md` and push the repo
4. Spaces will automatically build and deploy

The free tier provides CPU-only inference, which is fine for most features.
For GPU-accelerated upscaling, upgrade to a paid hardware tier.
