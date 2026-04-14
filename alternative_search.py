#!/usr/bin/env python3
"""
Alternative Search Approaches
If Google Custom Search API isn't working, try other methods
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus


def try_serpapi_alternative():
    """
    SerpAPI is a paid service that handles Google scraping
    They have a free tier for testing
    """
    print("🔍 Testing SerpAPI alternative...")
    
    # SerpAPI free tier - you'd need to sign up at serpapi.com
    # This is just to show the concept
    serpapi_url = "https://serpapi.com/search.json"
    
    params = {
        'engine': 'google',
        'q': 'mushroom table lamp buy',
        'api_key': 'demo',  # Replace with real key from serpapi.com
        'num': 5
    }
    
    try:
        response = requests.get(serpapi_url, params=params, timeout=10)
        print(f"SerpAPI Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            organic_results = data.get('organic_results', [])
            print(f"✅ SerpAPI found {len(organic_results)} results")
            
            for i, result in enumerate(organic_results[:3], 1):
                print(f"#{i}: {result.get('title', 'No title')}")
                print(f"    {result.get('link', 'No link')}")
        else:
            print("❌ SerpAPI demo key doesn't work (expected)")
    
    except Exception as e:
        print(f"❌ SerpAPI error: {e}")


def try_duckduckgo_search():
    """
    DuckDuckGo is more scraping-friendly than Google
    """
    print("\n🔍 Testing DuckDuckGo search...")
    
    query = "mushroom table lamp buy online"
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"DuckDuckGo Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.select('.result')
            
            print(f"✅ DuckDuckGo found {len(results)} results")
            
            shopping_results = []
            
            for result in results[:10]:
                try:
                    title_elem = result.select_one('.result__title a')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        url = title_elem.get('href')
                        
                        # Check if it's a shopping site
                        shopping_domains = ['amazon.com', 'walmart.com', 'target.com', 'bestbuy.com', 'wayfair.com']
                        if any(domain in url for domain in shopping_domains):
                            shopping_results.append({
                                'title': title,
                                'url': url
                            })
                except:
                    continue
            
            print(f"🛒 Found {len(shopping_results)} shopping results:")
            for i, result in enumerate(shopping_results[:5], 1):
                print(f"#{i}: {result['title'][:60]}...")
                print(f"    {result['url']}")
        
        else:
            print("❌ DuckDuckGo request failed")
    
    except Exception as e:
        print(f"❌ DuckDuckGo error: {e}")


def try_direct_retailer_search():
    """
    Search retailers directly instead of using search engines
    """
    print("\n🔍 Testing direct retailer search...")
    
    retailers = [
        {
            'name': 'Amazon',
            'search_url': 'https://www.amazon.com/s?k={query}',
            'result_selector': '[data-component-type="s-search-result"]'
        },
        {
            'name': 'Walmart',
            'search_url': 'https://www.walmart.com/search?q={query}',
            'result_selector': '[data-testid="item-stack"]'
        }
    ]
    
    query = "mushroom table lamp"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for retailer in retailers:
        try:
            search_url = retailer['search_url'].format(query=quote_plus(query))
            print(f"\n🔍 Searching {retailer['name']}: {search_url}")
            
            response = requests.get(search_url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = soup.select(retailer['result_selector'])
                print(f"   ✅ Found {len(results)} product containers")
                
                if len(results) > 0:
                    print(f"   🎯 {retailer['name']} search is working!")
                else:
                    print(f"   ⚠️ No products found (might need different selectors)")
            else:
                print(f"   ❌ {retailer['name']} blocked the request")
            
            # Be respectful
            time.sleep(2)
        
        except Exception as e:
            print(f"   ❌ {retailer['name']} error: {e}")


def main():
    """Test all alternative search methods"""
    
    print("🧪 TESTING ALTERNATIVE SEARCH METHODS")
    print("="*60)
    print("Since Google Custom Search API isn't working, let's try alternatives...")
    
    # Test 1: SerpAPI (paid service)
    try_serpapi_alternative()
    
    # Test 2: DuckDuckGo (free, more scraping-friendly)
    try_duckduckgo_search()
    
    # Test 3: Direct retailer search (most reliable)
    try_direct_retailer_search()
    
    print("\n" + "="*60)
    print("🎯 RECOMMENDATIONS:")
    print("1. DuckDuckGo search - Free and works well")
    print("2. Direct retailer search - Most reliable")
    print("3. SerpAPI - Paid but professional (serpapi.com)")
    print("4. Keep trying Google Custom Search API (might work later)")


if __name__ == "__main__":
    main()