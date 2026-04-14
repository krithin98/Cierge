# 🚀 SUPER QUICK DEPLOY GUIDE

## Step 1: Create GitHub Repo (2 minutes)

1. **Go to**: https://github.com/new
2. **Repository name**: `cierge-ai`
3. **Make it Public**
4. **DON'T check any boxes** (README, .gitignore, license)
5. **Click "Create repository"**

## Step 2: Push Code (1 minute)

Run this in your terminal:

```bash
cd "/Users/krith/Documents/CS Learning/New Enterprises/cierge-v3"
./deploy.sh
```

The script will ask for your GitHub username and push everything automatically.

## Step 3: Deploy on Render (3 minutes)

1. **Go to**: https://render.com
2. **Sign up with GitHub** (use same account)
3. **Click "New +"** → **"Web Service"**
4. **Select your `cierge-ai` repository**
5. **Fill in**:
   - **Name**: `cierge-ai`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. **Add Environment Variable**:
   - **Key**: `TAVILY_API_KEY`
   - **Value**: `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`
7. **Click "Create Web Service"**

## Step 4: Get Your Link! 🎉

In 2-3 minutes you'll have a live URL like:
**`https://cierge-ai.onrender.com`**

Share this link with anyone!

---

## 🆘 Need Help?

**If GitHub push fails:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

**If Render deployment fails:**
- Check that environment variable `TAVILY_API_KEY` is set correctly
- Make sure build command is: `pip install -r requirements.txt`
- Make sure start command is: `python app.py`

**Total time: ~6 minutes** ⏱️