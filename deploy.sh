#!/bin/bash

echo "🚀 Cierge AI Deployment Helper"
echo "==============================="
echo ""

echo "📋 What you need to do manually:"
echo ""
echo "1. CREATE GITHUB REPO:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: cierge-ai"
echo "   - Make it public"
echo "   - DON'T add README, .gitignore, or license (we have them)"
echo "   - Click 'Create repository'"
echo ""

echo "2. GET YOUR GITHUB URL:"
read -p "   Enter your GitHub username: " username
read -p "   Enter your repository name (or press enter for 'cierge-ai'): " reponame

if [ -z "$reponame" ]; then
    reponame="cierge-ai"
fi

github_url="https://github.com/$username/$reponame.git"

echo ""
echo "📤 PUSHING TO GITHUB..."
echo "Running commands:"

echo "git remote add origin $github_url"
git remote add origin $github_url

echo "git branch -M main"
git branch -M main

echo "git push -u origin main"
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo ""
    echo "🌐 NEXT STEPS - DEPLOY ON RENDER:"
    echo "================================="
    echo ""
    echo "1. Go to: https://render.com"
    echo "2. Sign up/login with GitHub"
    echo "3. Click 'New +' → 'Web Service'"
    echo "4. Connect this repo: $github_url"
    echo "5. Settings:"
    echo "   - Name: cierge-ai"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: python app.py"
    echo "   - Add Environment Variable:"
    echo "     Key: TAVILY_API_KEY"
    echo "     Value: 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"
    echo "6. Click 'Create Web Service'"
    echo ""
    echo "🎉 You'll get a live URL in 2-3 minutes!"
    echo "   Example: https://cierge-ai.onrender.com"
else
    echo ""
    echo "❌ Push failed. Make sure you:"
    echo "1. Created the GitHub repo first"
    echo "2. Entered the correct username"
    echo "3. Have git configured with your credentials"
    echo ""
    echo "Run: git config --global user.name 'Your Name'"
    echo "Run: git config --global user.email 'your@email.com'"
fi