#!/usr/bin/env python3
"""
Google Custom Search API Engine
Real Google search using official API - no anti-bot issues!
"""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
import time


@dataclass
class GoogleSearchResult:
    title: str
    url: str
    snippet: str
    display_link: str


class GoogleCustomSearchEngine:
    """
    Google Custom Search API - Official Google API for search results
    No Selenium, no anti-bot detection, just clean API calls
    """
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.session = requests.Session()
    
    def search(self, query: str, exclude_site: str = None, num_results: int = 10) -> List[GoogleSearchResult]:
        """
        Search Google using the Custom Search API
        """
        print(f"🔍 Google API search: '{query}'")
        
        # Modify query to exclude original site
        if exclude_site:
            query += f" -site:{exclude_site}"
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10),  # API max is 10 per request
            'safe': 'off',  # Don't filter results
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_search_results(data)
                print(f"✅ Found {len(results)} search results")
                return results
            
            elif response.status_code == 429:
                print("❌ API quota exceeded - too many requests")
                return []
            
            else:
                print(f"❌ API error: {response.status_code}")
                print(f"Response: {response.text}")
                return []
        
        except Exception as e:
            print(f"❌ Search API error: {e}")
            return []
    
    def _parse_search_results(self, data: Dict) -> List[GoogleSearchResult]:
        """
        Parse Google API response into search results
        """
        results = []
        
        items = data.get('items', [])
        
        for item in items:
            try:
                result = GoogleSearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    display_link=item.get('displayLink', '')
                )
                
                # Only include results with valid data
                if result.title and result.url:
                    results.append(result)
            
            except Exception as e:
                continue  # Skip this result if parsing fails
        
        return results
    
    def search_products(self, product_info: Dict[str, any]) -> List[GoogleSearchResult]:
        """
        Search for products based on analyzed product information
        """
        title = product_info.get('title', '')
        brand = product_info.get('brand', '')
        category = product_info.get('category', 'general')
        search_terms = product_info.get('search_terms', [])
        exclude_domain = product_info.get('domain', '')
        
        # Generate multiple search queries
        queries = self._generate_product_queries(title, brand, category, search_terms)
        
        all_results = []
        
        for query in queries:
            results = self.search(query, exclude_site=exclude_domain, num_results=10)
            all_results.extend(results)
            
            # Add small delay to be respectful to API
            time.sleep(0.2)
            
            # Stop if we have enough results
            if len(all_results) >= 20:
                break
        
        # Remove duplicates
        unique_results = self._remove_duplicates(all_results)
        
        print(f"🎯 Total unique results: {len(unique_results)}")
        return unique_results
    
    def _generate_product_queries(self, title: str, brand: str, category: str, search_terms: List[str]) -> List[str]:
        """
        Generate effective search queries for products
        """
        queries = []
        
        # Query 1: Full title + "buy"
        if title:
            queries.append(f'"{title}" buy online')
        
        # Query 2: Brand + key terms + "shop"
        if brand and search_terms:
            key_terms = ' '.join(search_terms[:3])  # Top 3 terms
            queries.append(f'{brand} {key_terms} shop online')
        
        # Query 3: Category-specific search
        if category != 'general' and search_terms:
            if category == 'lighting':
                queries.append(f'{" ".join(search_terms[:2])} lamp light buy online')
            elif category == 'electronics':
                queries.append(f'{" ".join(search_terms[:2])} electronics buy online')
            elif category == 'furniture':
                queries.append(f'{" ".join(search_terms[:2])} furniture buy online')
            else:
                queries.append(f'{" ".join(search_terms[:3])} {category} buy online')
        
        # Query 4: Simple product search
        if search_terms:
            queries.append(f'{" ".join(search_terms[:4])} purchase online')
        
        return queries[:3]  # Return top 3 queries
    
    def _remove_duplicates(self, results: List[GoogleSearchResult]) -> List[GoogleSearchResult]:
        """
        Remove duplicate results based on URL
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def get_quota_info(self) -> Dict[str, any]:
        """
        Get information about API quota usage
        """
        # Make a simple test query to check quota
        try:
            response = self.session.get(
                self.base_url,
                params={
                    'key': self.api_key,
                    'cx': self.search_engine_id,
                    'q': 'test',
                    'num': 1
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return {'status': 'active', 'quota_available': True}
            elif response.status_code == 429:
                return {'status': 'quota_exceeded', 'quota_available': False}
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'API key restrictions or permissions issue')
                return {'status': 'permission_denied', 'quota_available': False, 'error': error_message, 'response': response.text}
            else:
                return {'status': 'error', 'quota_available': False, 'error': response.status_code, 'response': response.text}
        
        except Exception as e:
            return {'status': 'error', 'quota_available': False, 'error': str(e)}


def test_google_search_engine():
    """Test the Google Custom Search API"""
    
    # Your API credentials
    API_KEY = "AIzaSyD_wYs5Mc-xDa9-k57AgcgQHE5sOFQD9ps"
    SEARCH_ENGINE_ID = "008fd0355c4484a38"
    
    print("🧪 TESTING GOOGLE CUSTOM SEARCH API")
    print("="*50)
    
    # Create search engine
    search_engine = GoogleCustomSearchEngine(API_KEY, SEARCH_ENGINE_ID)
    
    # Test 1: Check quota
    print("\n📊 Checking API quota...")
    quota_info = search_engine.get_quota_info()
    print(f"Quota status: {quota_info}")
    
    if not quota_info.get('quota_available'):
        print("❌ API quota not available - cannot test")
        return
    
    # Test 2: Simple search
    print("\n🔍 Testing simple search...")
    results = search_engine.search("mushroom table lamp buy online")
    
    if results:
        print(f"\n🎯 FOUND {len(results)} SEARCH RESULTS:")
        
        for i, result in enumerate(results[:5], 1):
            print(f"\n#{i}")
            print(f"   Title: {result.title}")
            print(f"   Site: {result.display_link}")
            print(f"   URL: {result.url}")
            print(f"   Snippet: {result.snippet[:100]}...")
    else:
        print("❌ No search results found")
    
    # Test 3: Product search with mock product info
    print(f"\n🔍 Testing product search...")
    
    mock_product_info = {
        'title': 'Dawnwake Mushroom Nightstand Dimmable Aesthetic',
        'brand': 'Dawnwake',
        'category': 'lighting',
        'search_terms': ['dawnwake', 'mushroom', 'nightstand', 'dimmable', 'aesthetic'],
        'domain': 'amazon.com'
    }
    
    product_results = search_engine.search_products(mock_product_info)
    
    if product_results:
        print(f"\n🎯 FOUND {len(product_results)} PRODUCT RESULTS:")
        
        for i, result in enumerate(product_results[:5], 1):
            print(f"\n#{i}")
            print(f"   Title: {result.title}")
            print(f"   Site: {result.display_link}")
            print(f"   URL: {result.url}")
    else:
        print("❌ No product results found")


if __name__ == "__main__":
    test_google_search_engine()