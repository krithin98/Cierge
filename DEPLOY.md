# 🚀 Deployment Guide

## Option 1: Render (Recommended - Free)

**Steps:**
1. **Create GitHub repo** (if you haven't already)
   ```bash
   cd /Users/krith/Documents/CS\ Learning/New\ Enterprises/cierge-v3
   git init
   git add .
   git commit -m "Initial commit - Cierge AI Product Comparison"
   ```

2. **Push to GitHub**
   - Create new repo on GitHub.com
   - Follow GitHub's instructions to push your code

3. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Environment Variables**: 
       - `TAVILY_API_KEY` = `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`

4. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Get your live URL: `https://your-app-name.onrender.com`

---

## Option 2: Railway (Also Free)

**Steps:**
1. **Same GitHub setup as above**

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repo
   - Add environment variable:
     - `TAVILY_API_KEY` = `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`
   - Deploy automatically

---

## Option 3: Vercel (Free)

**Steps:**
1. **Same GitHub setup**

2. **Create vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

3. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import GitHub repo
   - Add environment variable: `TAVILY_API_KEY`

---

## Option 4: Heroku (Paid)

**Steps:**
1. **Install Heroku CLI**
2. **Login and create app**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set environment variable**
   ```bash
   heroku config:set TAVILY_API_KEY=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
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

---

## 🎯 Recommended: Render

**Why Render?**
- ✅ **Free tier**: 750 hours/month
- ✅ **Auto-deploy**: Updates when you push to GitHub
- ✅ **Custom domains**: Add your own domain later
- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Easy setup**: No complex configuration

**Your app will be live at:**
`https://cierge-ai.onrender.com` (or similar)

## 🔧 Quick Deploy Commands

```bash
# Navigate to your project
cd "/Users/krith/Documents/CS Learning/New Enterprises/cierge-v3"

# Initialize git (if not already done)
git init
git add .
git commit -m "Deploy Cierge AI Product Comparison"

# Create GitHub repo and push
# (Follow GitHub's instructions)

# Then deploy on Render using the web interface
```

## 🌐 After Deployment

Your app will be accessible at a public URL like:
- `https://your-app-name.onrender.com`
- `https://your-app-name.railway.app`
- `https://your-app-name.vercel.app`

Share this URL with anyone! 🎉