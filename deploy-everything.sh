#!/bin/bash

echo "🚀 Complete Platform Deployment Script"
echo "======================================"
echo ""

echo "🎯 This will deploy your Financial Analytics Platform with:"
echo "✅ Real-time stock prices from 15+ APIs"
echo "✅ Live crypto data with multi-provider failover"
echo "✅ AI chat functionality with OpenRouter"
echo "✅ System monitoring with live metrics"
echo "✅ Stock search with 5000+ stocks"
echo "✅ XP-themed dashboard with full functionality"
echo ""

echo "📋 Prerequisites:"
echo "1. GitHub repository pushed (already done)"
echo "2. Railway account (free)"
echo "3. Vercel account (free)"
echo ""

echo "🚀 Step 1: Deploy Backend to Railway"
echo "------------------------------------"
echo "1. Go to: https://railway.app/"
echo "2. Sign up with GitHub"
echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
echo "4. Select: prasiddhnaik/PROJECT-PIE-REACT"
echo "5. Railway will automatically deploy your backend"
echo "6. Copy the URL (e.g., https://your-app.railway.app)"
echo ""

echo "🌐 Step 2: Deploy Frontend to Vercel"
echo "------------------------------------"
echo "1. Go to: https://vercel.com/"
echo "2. Sign up with GitHub"
echo "3. Click 'New Project' → Import your repo"
echo "4. Configure:"
echo "   - Framework Preset: Next.js"
echo "   - Root Directory: apps/web"
echo "   - Build Command: npm run build"
echo "5. Add Environment Variable:"
echo "   - Name: NEXT_PUBLIC_BACKEND_URL"
echo "   - Value: [Your Railway URL from Step 1]"
echo "6. Deploy!"
echo ""

echo "🔧 Step 3: Push Deployment Configs"
echo "----------------------------------"
echo "Pushing deployment configurations to GitHub..."
echo ""

# Push the deployment files
git add .
git commit -m "🚀 Add complete deployment configurations for full functionality"
git push origin main

echo "✅ Deployment files pushed!"
echo ""

echo "🌍 Your Platform URLs:"
echo "----------------------"
echo "Backend API: [Your Railway URL]"
echo "Frontend: [Your Vercel URL]"
echo ""

echo "📊 Test Your Deployment:"
echo "-----------------------"
echo "1. Test Backend:"
echo "   curl [Your Railway URL]/health"
echo "   curl [Your Railway URL]/api/data/market/overview"
echo ""
echo "2. Test Frontend:"
echo "   Visit [Your Vercel URL]"
echo "   Test all XP dashboard features"
echo ""

echo "🎉 Success! Your platform will have:"
echo "✅ Real-time stock prices"
echo "✅ Live crypto data"
echo "✅ AI chat functionality"
echo "✅ System monitoring"
echo "✅ Stock search"
echo "✅ XP-themed dashboard"
echo "✅ Mobile responsive"
echo "✅ Professional URLs"
echo "✅ Automatic updates"
echo ""

echo "💰 Cost: ~$3/month total"
echo "   - Railway (Backend): $2-3/month"
echo "   - Vercel (Frontend): FREE"
echo ""

echo "📱 Everyone can access your platform!"
echo "Share the URLs with friends and family!"
echo ""

echo "Press any key to open deployment guides..."
read -n 1 -s

# Open deployment guides
open "https://railway.app/"
open "https://vercel.com/" 