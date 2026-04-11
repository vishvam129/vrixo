# Vrixo Deployment Guide

Covers Features #73–#77: Docker, HuggingFace Spaces, Cloudflare CDN, Sentry, health checks.

## 1. Local Docker Test (#73)

```bash
docker build -t vrixo:local .
docker run -p 8501:8501 vrixo:local
```

Open <http://localhost:8501> to verify the app loads.

## 2. HuggingFace Spaces (#74)

1. Create a new Space at https://huggingface.co/new-space
2. Select **Streamlit** as the SDK
3. Rename `README_HF.md` to `README.md` at the repo root (Spaces reads the frontmatter)
4. Push the repo to the Space's git remote
5. Wait ~5 minutes for the build to complete
6. Your app will be available at `https://huggingface.co/spaces/<your-username>/vrixo`

**Free tier limits:**
- 16 GB RAM
- 2 vCPU
- CPU-only inference (no GPU)
- Sleeps after 48 hours of inactivity

## 3. Cloudflare CDN (#75)

Once the app is deployed (to HF Spaces, Render, or your own server):

1. Add your domain to Cloudflare
2. Create a CNAME record pointing to the deployed app URL
3. Enable these in Cloudflare dashboard:
   - **SSL/TLS → Full (strict)**
   - **Speed → Auto Minify → JS, CSS, HTML**
   - **Caching → Browser Cache TTL: 4 hours**
   - **Page Rules:** Cache `/static/*` aggressively
   - **Security → Bot Fight Mode: On**
   - **DDoS protection: On** (automatic on free tier)

### Cache configuration

Add this to Cloudflare Workers or Page Rules:

```
vrixo.com/static/*   → Cache Level: Cache Everything, Edge Cache TTL: 1 month
vrixo.com/api/*      → Cache Level: Bypass
vrixo.com/*          → Cache Level: Standard
```

## 4. Sentry Error Tracking (#76)

1. Create a free Sentry account at https://sentry.io
2. Create a new project (Python + Streamlit)
3. Copy the DSN and add it to your `.env`:

   ```bash
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```

4. Verify integration by triggering a test error in the Python shell:

   ```python
   import sentry_sdk
   sentry_sdk.init(dsn="your-dsn")
   try:
       1 / 0
   except ZeroDivisionError:
       sentry_sdk.capture_exception()
   ```

5. Check your Sentry dashboard — the error should appear within 1 minute.

## 5. Health Check Endpoint (#77)

The Dockerfile exposes a health check at `/_stcore/health` (Streamlit's built-in).
Additionally, `web/health.py` provides a custom endpoint:

```bash
curl https://vrixo.com/health
# → {"status": "ok", "version": "0.1.0", "uptime_s": 12345}
```

Streamlit's native health check:

```bash
curl https://vrixo.com/_stcore/health
# → ok
```

## 6. Production Checklist

Before going live:

- [ ] Set all secrets via environment variables (not in code)
- [ ] Enable 2FA on Cloudflare, HuggingFace, Sentry, GitHub accounts
- [ ] Configure Sentry DSN in deployment environment
- [ ] Test health endpoint returns 200
- [ ] Run the full test suite: `pytest tests/ -m "not slow"`
- [ ] Verify the Docker image builds without errors
- [ ] Set rate limits in environment (free tier 5/day)
- [ ] Configure upload auto-deletion cron (every hour)
- [ ] Enable Cloudflare DDoS protection
- [ ] Monitor Sentry for the first 24 hours
- [ ] Have a rollback plan ready
