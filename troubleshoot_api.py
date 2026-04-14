#!/usr/bin/env python3
"""
Troubleshoot API issues step by step
"""

import requests
import time

def check_billing_and_quotas():
    """Check if billing is enabled and quotas are set"""
    
    API_KEY = "AIzaSyD_wYs5Mc-xDa9-k57AgcgQHE5sOFQD9ps"
    
    print("🔍 TROUBLESHOOTING STEPS:")
    print("="*50)
    
    print("\n1. ✅ API is enabled (you confirmed this)")
    print("2. ✅ Search engine is created")
    print("3. ✅ API key exists")
    
    print("\n4. 🔍 Checking possible issues...")
    
    # Check if it's a billing issue
    print("\n📊 BILLING CHECK:")
    print("- Go to Google Cloud Console")
    print("- Check 'Billing' in the left menu")
    print("- Make sure billing is enabled for this project")
    print("- Custom Search API requires billing even for free tier")
    
    print("\n⏱️ TIMING CHECK:")
    print("- APIs can take 5-10 minutes to fully activate")
    print("- Try waiting a few more minutes")
    
    print("\n🔑 API KEY CHECK:")
    print("- Make sure API key is from the SAME project")
    print("- Try creating a NEW API key")
    
    return True

def try_alternative_approach():
    """Suggest alternative approaches while API is being fixed"""
    
    print("\n🔄 ALTERNATIVE APPROACHES:")
    print("="*40)
    
    print("\n1. 💰 SerpAPI (Paid but reliable):")
    print("   - Sign up at serpapi.com")
    print("   - $50/month for 5000 searches")
    print("   - Handles all Google anti-bot for you")
    
    print("\n2. 🦆 DuckDuckGo Search (Free):")
    print("   - More scraping-friendly than Google")
    print("   - Can implement right now")
    print("   - Good product coverage")
    
    print("\n3. 🛒 Direct Retailer Search (Most reliable):")
    print("   - Search Amazon, Walmart, Target directly")
    print("   - Skip search engines entirely")
    print("   - Most likely to work")
    
    print("\n4. ⏳ Wait and retry Google API:")
    print("   - Sometimes takes up to 24 hours")
    print("   - Check billing is enabled")
    print("   - Try new API key")

def create_fallback_plan():
    """Create a plan to move forward"""
    
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("="*40)
    
    print("\n🥇 OPTION 1: Fix Google API (Best long-term)")
    print("   1. Enable billing in Google Cloud Console")
    print("   2. Wait 10-15 minutes")
    print("   3. Try creating a new API key")
    print("   4. Test again")
    
    print("\n🥈 OPTION 2: Use DuckDuckGo (Quick solution)")
    print("   1. Implement DuckDuckGo search")
    print("   2. Filter for shopping sites")
    print("   3. Get working system today")
    print("   4. Switch to Google API later")
    
    print("\n🥉 OPTION 3: Direct retailer search")
    print("   1. Search Amazon/Walmart/Target directly")
    print("   2. Most reliable approach")
    print("   3. No search engine dependencies")
    
    print("\n💡 MY RECOMMENDATION:")
    print("   - Try Option 1 (fix Google API) for 30 minutes")
    print("   - If still not working, go with Option 2 (DuckDuckGo)")
    print("   - This gets you a working system today")

if __name__ == "__main__":
    check_billing_and_quotas()
    try_alternative_approach() 
    create_fallback_plan()
    
    print(f"\n🤔 WHAT DO YOU WANT TO DO?")
    print("A) Keep trying to fix Google API")
    print("B) Switch to DuckDuckGo search (faster)")
    print("C) Use direct retailer search (most reliable)")