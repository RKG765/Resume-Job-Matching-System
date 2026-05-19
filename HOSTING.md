# 🌐 How to Host — Resume-Job Matching System

> Step-by-step guide to deploy a **fully working site on the internet** for FREE.

---

## 📌 Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│   FRONTEND (React)   │  ────►  │   BACKEND (FastAPI)  │
│   Hosted on VERCEL   │  API    │   Hosted on RENDER   │
│   vercel.com (free)  │  calls  │   render.com (free)  │
└──────────────────────┘         └──────────────────────┘
         │                                │
    Your users visit              Python + BERT model
    the Vercel URL                runs in Docker container
```

**Why two platforms?**
- Vercel is perfect for React/Vite frontends — instant deploys, free SSL, global CDN
- The backend uses PyTorch + BERT (~500MB) which exceeds Vercel's 250MB serverless limit
- Render supports Docker containers with no size limits on the free tier

---

## 📋 Prerequisites

Before you start, make sure you have:

- [ ] A **GitHub account** with your code pushed to a repository
- [ ] A **Vercel account** — sign up free at [vercel.com](https://vercel.com) (use GitHub login)
- [ ] A **Render account** — sign up free at [render.com](https://render.com) (use GitHub login)
- [ ] A **Groq API key** (optional, for LLM features) — free at [console.groq.com](https://console.groq.com)

---

## Step 1: Push Your Code to GitHub

If you haven't already:

```bash
cd resume_job_matcher

# Initialize git (skip if already done)
git init
git add .
git commit -m "Ready for cloud deployment"

# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/resume-job-matcher.git
git branch -M main
git push -u origin main
```

> ⚠️ Make sure `.env` is in your `.gitignore` — never push API keys to GitHub!

---

## Step 2: Deploy Backend on Render

### 2.1 — Create a New Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** → select your `resume-job-matcher` repo
4. If you don't see your repo, click **"Configure account"** to grant Render access

### 2.2 — Configure the Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `resume-job-matcher-api` |
| **Region** | Choose closest to you (e.g., `Oregon` or `Singapore`) |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Instance Type** | `Free` |

### 2.3 — Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add these one by one:

| Key | Value |
|-----|-------|
| `USE_SQLITE` | `true` |
| `DEBUG` | `false` |
| `CORS_ORIGINS` | `*` |
| `LLM_ENABLED` | `true` |
| `LLM_API_URL` | `https://api.groq.com/openai/v1` |
| `LLM_API_KEY` | `your_groq_api_key_here` |
| `LLM_MODEL` | `llama-3.3-70b-versatile` |

> 💡 If you don't have a Groq API key yet, set `LLM_ENABLED=false`. The system works fine without LLM — it uses rule-based explanations instead.

### 2.4 — Deploy

1. Click **"Create Web Service"**
2. Wait for the build to complete (first build takes **5-10 minutes** because it downloads PyTorch + BERT model)
3. Once it shows **"Live"** with a green dot, your backend is running!
4. **Copy your Render URL** — it looks like: `https://resume-job-matcher-api.onrender.com`

### 2.5 — Verify Backend is Working

Open this in your browser (replace with your actual URL):

```
https://resume-job-matcher-api.onrender.com/api/health
```

You should see:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "database": "sqlite",
  "llm_available": true
}
```

Also try the API docs:
```
https://resume-job-matcher-api.onrender.com/docs
```

> ⚠️ **Note:** Render free tier sleeps after 15 min of inactivity. First request after sleep takes ~30-60 seconds to wake up. This is normal.

---

## Step 3: Deploy Frontend on Vercel

### 3.1 — Import Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select your `resume-job-matcher` repo
4. If you don't see it, click **"Adjust GitHub App Permissions"**

### 3.2 — Configure the Project

| Setting | Value |
|---------|-------|
| **Project Name** | `resume-job-matcher` (or any name you want) |
| **Framework Preset** | `Vite` (Vercel usually auto-detects this) |
| **Root Directory** | Click **"Edit"** → type `frontend` → click **"Continue"** |

### 3.3 — Add Environment Variable

This is the **most important step** — it tells the frontend where to find the backend:

1. Expand **"Environment Variables"**
2. Add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://resume-job-matcher-api.onrender.com` |

> ⚠️ Replace the URL above with YOUR actual Render URL from Step 2.4!

### 3.4 — Deploy

1. Click **"Deploy"**
2. Wait ~1-2 minutes for the build
3. Once done, Vercel gives you a URL like: `https://resume-job-matcher.vercel.app`
4. **That's your live site! 🎉**

---

## Step 4: Test Your Live Site

1. Open your Vercel URL in a browser
2. Paste a job description (e.g., "Senior Python Developer with Django, PostgreSQL, Docker experience")
3. Add a resume (paste text or upload a PDF)
4. Click **"Match"**
5. See the results with scores, skill gaps, and classifications

> 💡 The first request might be slow (~30s) if Render was sleeping. Subsequent requests are fast.

---

## 🔧 Troubleshooting

### "CORS Error" in Browser Console

**Cause:** Backend isn't allowing the frontend's domain.

**Fix:** Go to Render Dashboard → your service → Environment → make sure `CORS_ORIGINS` is set to `*`

---

### "Failed to fetch" or "Network Error"

**Cause:** Backend URL is wrong or Render is sleeping.

**Fix:**
1. Check your `VITE_API_URL` in Vercel matches your Render URL exactly
2. Visit your Render health check URL directly to wake it up:
   ```
   https://your-render-url.onrender.com/api/health
   ```
3. Wait 30-60 seconds, then try the frontend again

---

### Frontend Shows But No Matching Works

**Cause:** `VITE_API_URL` is not set or is wrong.

**Fix:**
1. Go to Vercel Dashboard → your project → **Settings** → **Environment Variables**
2. Make sure `VITE_API_URL` is set to your full Render URL (with `https://`)
3. **Important:** After changing env vars, you must **redeploy**:
   - Go to **Deployments** tab → click **"..."** on latest → **"Redeploy"**

---

### Build Fails on Render

**Cause:** Usually a dependency issue.

**Fix:** Check the build logs in Render Dashboard. Common fixes:
- Make sure `requirements.txt` is in the `backend/` directory
- Make sure `Dockerfile` is in the `backend/` directory
- Check that `Root Directory` is set to `backend`

---

### LLM Explanations Say "AI explanation unavailable"

**Cause:** Groq API key is missing, invalid, or expired.

**Fix:**
1. Go to [console.groq.com](https://console.groq.com) → create a new API key
2. Update `LLM_API_KEY` in Render Dashboard → Environment
3. Click **"Manual Deploy"** → **"Deploy latest commit"** to restart

---

## 🔄 How to Update After Making Changes

When you make code changes locally and want to update the live site:

```bash
# 1. Commit your changes
git add .
git commit -m "Update: description of changes"

# 2. Push to GitHub
git push origin main

# 3. Both Vercel and Render will auto-deploy from GitHub!
#    - Vercel: ~1-2 min
#    - Render: ~5-10 min (rebuilds Docker image)
```

> Both platforms have **auto-deploy** enabled by default — push to `main` branch and they update automatically.

---

## 💰 Cost Summary

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| **Vercel** | Hobby (Free) | $0 | 100GB bandwidth/month, unlimited deploys |
| **Render** | Free | $0 | 750 hours/month, sleeps after 15min inactivity |
| **Groq** | Free | $0 | Rate limited (30 req/min), unlimited usage |
| **GitHub** | Free | $0 | Unlimited public repos |
| **Total** | | **$0/month** | |

---

## 📌 Quick Reference — Your URLs

After deployment, bookmark these:

| What | URL |
|------|-----|
| **Live Site** | `https://resume-job-matcher.vercel.app` |
| **Backend API** | `https://resume-job-matcher-api.onrender.com` |
| **API Docs** | `https://resume-job-matcher-api.onrender.com/docs` |
| **Health Check** | `https://resume-job-matcher-api.onrender.com/api/health` |
| **Vercel Dashboard** | `https://vercel.com/dashboard` |
| **Render Dashboard** | `https://dashboard.render.com` |
| **Groq Console** | `https://console.groq.com` |

---

<p align="center">
  <strong>🎉 That's it! Your Resume-Job Matching System is live on the internet!</strong>
</p>
