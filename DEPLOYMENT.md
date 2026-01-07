# BuildForge - Deployment to Render.com

Complete guide for deploying your Django BuildForge application to Render.com with full data preservation.

---

## 📋 Prerequisites

- ✅ All local data exported to JSON files (completed)
- ✅ GitHub account
- ✅ Git repository for your project
- ✅ Render.com account (free tier available)

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Push Code to GitHub

1. **Commit all changes:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment with PostgreSQL support"
   git push origin main
   ```

### Step 2: Create Render Account and PostgreSQL Database

1. Go to [https://render.com](https://render.com) and sign up (free)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database:
   - **Name**: `buildforge-db`
   - **Database**: `buildforge_db` 
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: **Free** (100MB storage, expires after 90 days but sufficient for testing)
4. Click **"Create Database"**
5. **SAVE THESE CREDENTIALS** (you'll need them):
   - Internal Database URL
   - External Database URL
   - Hostname
   - Port
   - Database name
   - Username
   - Password

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `buildforge`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: (leave blank)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn buildforge_project.wsgi:application`
   - **Plan**: **Free**

4. Click **"Advanced"** and add environment variables:

   ```
   SECRET_KEY=<generate-random-50-character-string>
   DEBUG=False
   ALLOWED_HOSTS=buildforge.onrender.com
   
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=buildforge_db
   DB_USER=<from-step-2>
   DB_PASSWORD=<from-step-2>
   DB_HOST=<from-step-2>
   DB_PORT=5432
   
   PYTHON_VERSION=3.11.0
   ```

   > **To generate SECRET_KEY**, run locally:
   > ```python
   > python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   > ```

5. Click **"Create Web Service"**

### Step 4: Wait for Initial Deployment

- Render will build and deploy your app (takes 5-10 minutes)
- Watch the logs for any errors
- Once deployed, you'll see ✅ **"Live"** status

### Step 5: Import Your Data

**Option A: Using Render Shell (Recommended)**

1. In your Render dashboard, go to your web service
2. Click **"Shell"** tab on the left
3. Run these commands one by one:

   ```bash
   # Upload your JSON files first (see Option B for file upload)
   python manage.py loaddata users_data.json
   python manage.py loaddata catalog_data.json
   python manage.py loaddata builds_data.json
   python manage.py loaddata marketplace_data.json
   ```

**Option B: Using Render CLI**

1. Install Render CLI locally:
   ```bash
   pip install render-cli
   render login
   ```

2. Upload data files:
   ```bash
   render services list
   # Note your service ID
   
   # Upload JSON files
   render files upload <service-id> users_data.json
   render files upload <service-id> catalog_data.json
   render files upload <service-id> builds_data.json
   render files upload <service-id> marketplace_data.json
   ```

3. Import data via shell:
   ```bash
   render shell <service-id>
   python manage.py loaddata users_data.json
   python manage.py loaddata catalog_data.json
   python manage.py loaddata builds_data.json
   python manage.py loaddata marketplace_data.json
   ```

### Step 6: Upload Media Files

If you have user-uploaded images in the `media/` folder:

**Using Render Dashboard:**
1. Go to your service → **"Environment"**
2. Add a persistent disk:
   - **Mount Path**: `/opt/render/project/src/media`
   - **Size**: 1GB (costs $0.25/month)
3. Upload files via SFTP or Render CLI

**Note**: Free tier doesn't include persistent storage for media files. Consider using:
- **Cloudinary** (free tier: 25GB storage, 25GB bandwidth)
- **AWS S3** (free tier: 5GB storage)
- **Backblaze B2** (10GB free)

### Step 7: Create Superuser (Admin Access)

```bash
# In Render Shell
python manage.py createsuperuser
```

### Step 8: Verify Deployment

Visit your live site: `https://buildforge.onrender.com`

Check:
- ✅ Homepage loads
- ✅ All builds/catalog items visible
- ✅ User login works
- ✅ Marketplace listings display
- ✅ Static files (CSS/JS) load correctly
- ✅ Admin panel accessible at `/admin`

---

## 🔧 Troubleshooting

### Database Connection Errors
- Verify all `DB_*` environment variables are correct
- Check that Internal Database URL is used (not External)
- Ensure PostgreSQL service is running

### Static Files Not Loading
```bash
# In Render Shell
python manage.py collectstatic --noinput --clear
```

### Migration Errors
```bash
# In Render Shell
python manage.py makemigrations
python manage.py migrate
```

### Data Import Errors
- Check JSON files for syntax errors
- Import in correct order (users → catalog → builds → marketplace)
- Clear existing data if needed: `python manage.py flush`

---

## 📊 Free Tier Limitations

**Render.com Free Tier:**
- ✅ 512MB RAM
- ✅ Shared CPU
- ✅ Automatic SSL
- ⚠️ Sleeps after 15 minutes of inactivity (cold start: 30-60 seconds)
- ⚠️ PostgreSQL expires after 90 days
- ❌ No persistent disk storage (media files)

**Upgrade Options:**
- **Starter Plan** ($7/month): Always-on, 512MB RAM
- **PostgreSQL** ($7/month): Persistent, 1GB storage
- **Disk Storage** ($0.25/GB/month): For media files

---

## 🔄 Updating Your Deployment

After making code changes:

```bash
git add .
git commit -m "Update description"
git push origin main
```

Render automatically redeploys on push!

---

## 🎯 Production Best Practices

1. **Secret Key**: Use strong, unique SECRET_KEY
2. **Debug Mode**: Always set `DEBUG=False` in production
3. **Allowed Hosts**: Restrict to your domain only
4. **Database Backups**: Export data regularly with `dumpdata`
5. **Environment Variables**: Never commit `.env` file
6. **Media Storage**: Use cloud storage (Cloudinary/S3) for production
7. **Monitoring**: Enable Render notifications for downtime alerts

---

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.2/howto/deployment/
- Community: https://community.render.com/

---

**Your live site will be at**: `https://buildforge.onrender.com` 🎉
