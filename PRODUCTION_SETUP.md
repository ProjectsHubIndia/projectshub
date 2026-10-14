# 🚀 Production Deployment Setup Guide

## ⚠️ CRITICAL: Set SECRET_KEY Before Deploying

Your production deployment is currently **failing** because SECRET_KEY is not properly configured.

---

## 🔐 Step 1: Generate a Secure SECRET_KEY

Run this command locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example output:**
```
qj%+3lq)w6c%%0+kn2*lnuxspckl$j$gdpyaf@f4#nhtszf656
```

⚠️ **IMPORTANT:** 
- Generate your own unique key
- Never use example keys from documentation
- Never commit SECRET_KEY to Git
- Use different keys for dev/staging/production

---

## 🌐 Step 2: Set Environment Variables in Your Platform

### If Using **Railway:**

1. Go to https://railway.app/dashboard
2. Select your project
3. Click **Variables** tab
4. Add these variables:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=projectshub.co.in,www.projectshub.co.in,.railway.app
```

5. Click **Deploy** or wait for auto-redeploy

---

### If Using **Vercel:**

1. Go to https://vercel.com/dashboard
2. Select your project → **Settings** → **Environment Variables**
3. Add these variables for **Production**:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
```

4. Redeploy: **Deployments** → Latest → **Redeploy**

---

### If Using **Heroku:**

```bash
heroku config:set SECRET_KEY="your-generated-secret-key-here" -a your-app-name
heroku config:set DEBUG=False -a your-app-name
```

---

### If Using **Render:**

1. Dashboard → Your Service → **Environment**
2. Add:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
```

3. Service will auto-redeploy

---

## ✅ Step 3: Verify Deployment

After setting variables:

1. **Check deployment logs** - Should see "Starting server" instead of SECRET_KEY errors
2. **Visit your production URL** - Site should load with CSS
3. **Test key pages:**
   - Homepage
   - Projects page
   - Contact form
   - Admin panel

---

## 🗃️ Step 4: Database Setup (Optional but Recommended)

For production, use PostgreSQL instead of SQLite:

### Option A: Neon (Free PostgreSQL)

1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string
4. Add to environment variables:

```
DATABASE_URL=postgres://user:password@ep-...neon.tech/neondb?sslmode=require
```

### Option B: Supabase (Free PostgreSQL)

1. Sign up at https://supabase.com
2. Create project
3. Get connection string from Settings → Database
4. Add to environment variables:

```
DATABASE_URL=postgres://postgres:[YOUR-PASSWORD]@db....supabase.co:5432/postgres
```

---

## 📧 Step 5: Email Configuration (Optional)

For contact forms and notifications:

### Using Gmail:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Note:** Use [App Passwords](https://myaccount.google.com/apppasswords) for Gmail, not your regular password.

---

## 🔍 Troubleshooting

### Still seeing SECRET_KEY error?

**Check:**
1. Variable name is exactly `SECRET_KEY` (case-sensitive)
2. Value doesn't start with `django-insecure-`
3. Value is at least 50 characters long
4. Platform has redeployed after setting variable

**Debug:**
- Check deployment logs for the actual error
- Verify environment variables are set in platform dashboard
- Try manual redeploy

### Site loads but CSS missing?

**Check:**
1. Run `python manage.py collectstatic` locally
2. Commit staticfiles to Git (if platform requires it)
3. Verify `STATIC_URL` and `STATIC_ROOT` in settings.py

### Database errors?

**If using SQLite in production:**
- SQLite may not persist on serverless platforms (Vercel, Railway)
- Switch to PostgreSQL (see Step 4)

**If using PostgreSQL:**
- Run migrations: `python manage.py migrate`
- Check DATABASE_URL format
- Verify SSL mode is correct

---

## 📋 Complete Environment Variables Checklist

For production, set these variables:

### Required:
- ✅ `SECRET_KEY` - Your unique secret key
- ✅ `DEBUG` - Set to `False`

### Recommended:
- ✅ `DATABASE_URL` - PostgreSQL connection string
- ✅ `ALLOWED_HOSTS` - Your domain(s)
- ✅ `EMAIL_HOST_USER` - For notifications
- ✅ `EMAIL_HOST_PASSWORD` - Email password/token

### Optional:
- `CSRF_TRUSTED_ORIGINS` - Additional domains
- `CHAT_NOTIFY_EMAILS` - Live chat notifications
- `GOOGLE_ANALYTICS_ID` - GA4 tracking
- `SITE_URL` - Override auto-detected URL

---

## 🚨 Security Checklist

Before going live:

- [ ] SECRET_KEY is unique and secure (not from examples)
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS is properly configured
- [ ] Database uses SSL (PostgreSQL)
- [ ] Email uses TLS/SSL
- [ ] No sensitive data committed to Git
- [ ] .gitignore includes .env files
- [ ] HTTPS is enabled (your platform handles this)

---

## 📚 Additional Resources

- Django Production Checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
- SECRET_KEY Generator: https://djecrety.ir/
- Neon PostgreSQL: https://neon.tech/docs/get-started-with-neon/signing-up
- Railway Docs: https://docs.railway.app/
- Vercel Django Guide: https://vercel.com/guides/deploying-django-with-vercel

---

## 🆘 Need Help?

If deployment issues persist:

1. Check platform-specific logs
2. Verify all environment variables are set
3. Review Django settings.py configuration
4. Test locally with production settings: `DEBUG=False python manage.py runserver`

---

**Last Updated:** October 14, 2026
**Django Version:** 4.2.30
**Python Version:** 3.12
