# Free Hosting Guide for AuraLink

AuraLink consists of a Django backend and a React frontend, requiring a few different services to run. You can host the entire stack for absolutely **free** using modern cloud providers.

Here is the recommended architecture for free hosting:

## 1. Frontend (React + Vite)
**Recommended Host:** [Vercel](https://vercel.com) or [Netlify](https://www.netlify.com/)
**Cost:** $0/month

**How to deploy on Vercel:**
1. Push your code to a GitHub repository.
2. Sign up for Vercel and click **Add New Project**.
3. Import your GitHub repository.
4. Set the **Framework Preset** to `Vite`.
5. Set the **Root Directory** to `frontend`.
6. Add the following Environment Variable:
   - `VITE_API_BASE`: `https://your-backend-url.onrender.com/api` (You will get this URL in Step 2).
7. Click **Deploy**.

---

## 2. Backend (Django REST Framework)
**Recommended Host:** [Render](https://render.com)
**Cost:** $0/month (Free Web Service tier)

**How to deploy on Render:**
1. In your `backend` folder, ensure you have a `requirements.txt` and a `build.sh` script to run migrations.
2. Sign up for Render and create a new **Web Service**.
3. Connect your GitHub repository.
4. Set the **Root Directory** to `backend`.
5. Set the **Build Command** to: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
6. Set the **Start Command** to: `daphne -b 0.0.0.0 -p 10000 auralink.asgi:application` (Since AuraLink uses WebSockets, you must use Daphne/Uvicorn instead of Gunicorn).

*Note: Render's free tier spins down after 15 minutes of inactivity. The first request after a spin-down may take ~50 seconds to load.*

---

## 3. Database (PostgreSQL)
**Recommended Host:** [Neon.tech](https://neon.tech/) or [Supabase](https://supabase.com/)
**Cost:** $0/month

Django needs a production database. Render offers a free database, but it gets deleted after 90 days. For a permanent free database, use Neon:
1. Create a free project on Neon.tech.
2. Copy the Postgres connection string.
3. In your Render Backend settings, add the Environment Variable:
   - `DATABASE_URL`: `postgres://user:password@endpoint.neon.tech/dbname`
4. Make sure to update your `settings.py` to parse `dj_database_url`.

---

## 4. WebSockets / Redis (Django Channels)
**Recommended Host:** [Upstash](https://upstash.com/)
**Cost:** $0/month (Serverless Redis free tier limits)

AuraLink uses WebSockets for real-time device heartbeats and dashboard updates. This requires a Redis channel layer.
1. Sign up for Upstash and create a free Redis database.
2. Copy the Redis URL (make sure it starts with `rediss://` for secure connections).
3. In your Render Backend settings, add the Environment Variable:
   - `REDIS_URL`: `rediss://default:password@endpoint.upstash.io:port`
4. Ensure your `settings.py` points `CHANNEL_LAYERS` to this `REDIS_URL`.

---

## 5. Media Hosting (Videos & Images)
**Recommended Host:** [Cloudinary](https://cloudinary.com/) (Already integrated)
**Cost:** $0/month (Generous free tier for media storage & bandwidth)

Since AuraLink already uses Cloudinary, just make sure to add your credentials to the Render Backend Environment Variables:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Need Help Preparing the Code?
Before you can push to Render, you'll need to run a few preparation steps on your backend (like installing `dj-database-url`, `psycopg2-binary`, configuring `whitenoise` for static files, and creating a `build.sh` script). Let me know if you want me to write these deployment configurations for you!
