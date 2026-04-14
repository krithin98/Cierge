#!/usr/bin/env python3
"""
Product Comparison System using Tavily Best Practices
Built following Tavily's recommended patterns for production systems
"""

from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import time


@dataclass
class ProductMatch:
    title: str
    price: Optional[str]
    retailer: str
    url: str
    content_snippet: str
    relevance_score: float
    verified: bool = False


class TavilyProductComparison:
    """
    Production-ready product comparison using Tavily best practices
    """
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def find_product_alternatives(self, product_url: str) -> List[ProductMatch]:
        """
        Find alternative products using Tavily search
        Following Tavily best practices for product discovery
        """
        print(f"🔍 Finding alternatives for: {product_url}")
        
        # Step 1: Extract product information
        product_info = self._extract_product_info(product_url)
        if not product_info:
            return []
        
        print(f"✅ Product: {product_info['name']}")
        
        # Step 2: Use Tavily search with optimized queries
        search_results = self._search_for_alternatives(product_info)
        
        # Step 3: Filter and rank results
        product_matches = self._process_search_results(search_results, product_info)
        
        # Step 4: Verify URLs and enhance data
        verified_matches = self._verify_and_enhance(product_matches)
        
        print(f"🎯 Found {len(verified_matches)} verified alternatives")
        return verified_matches[:5]  # Return top 5
    
    def _extract_product_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract product information from URL using multiple strategies"""
        
        # Strategy 1: Extract from URL structure
        domain = urlparse(url).netloc.lower()
        product_name = None
        
        if 'amazon.com' in domain:
            # Amazon URL pattern: /Product-Name-With-Dashes/dp/B123456789/
            parts = url.split('/')
            for part in parts:
                if '-' in part and len(part) > 10 and 'dp' not in part and not part.startswith('B0'):
                    product_name = part.replace('-', ' ').title()
                    if len(product_name.split()) >= 3:
                        break
        
        elif 'walmart.com' in domain:
            # Walmart URL pattern: /Product-Name-With-Dashes/12345678
            parts = url.split('/')
            for part in parts:
                if '-' in part and len(part) > 15 and not part.isdigit():
                    product_name = part.replace('-', ' ').title()
                    if len(product_name.split()) >= 3:
                        break
        
        if not product_name:
            return None
        
        # Strategy 2: Use Tavily extract to get more details (if needed)
        try:
            extract_response = self.client.extract(urls=[url])
            if extract_response and 'results' in extract_response:
                extracted_content = extract_response['results'][0].get('raw_content', '')
                # Could enhance product info with extracted content
        except:
            pass  # Fallback to URL-based extraction
        
        return {
            'name': product_name,
            'original_url': url,
            'domain': domain,
            'search_terms': product_name.lower().split()[:5]  # Top 5 words for searching
        }
    
    def _search_for_alternatives(self, product_info: Dict[str, Any]) -> List[Dict]:
        """
        Search for product alternatives using Tavily best practices
        """
        product_name = product_info['name']
        exclude_domain = product_info['domain']
        
        # Create multiple search strategies following Tavily best practices
        search_queries = [
            f'"{product_name}" buy online store',  # Exact match search
            f'{product_name} price comparison shopping',  # Comparison search
            f'{" ".join(product_info["search_terms"])} purchase retailer'  # Keyword search
        ]
        
        all_results = []
        
        for query in search_queries:
            print(f"🔍 Searching: '{query}'")
            
            try:
                # Use Tavily search with optimal parameters
                response = self.client.search(
                    query=query,
                    search_depth="basic",  # Fast but comprehensive
                    max_results=10,
                    exclude_domains=[exclude_domain] if exclude_domain else None,
                    include_raw_content=True  # Get full content for better analysis
                )
                
                if 'results' in response:
                    all_results.extend(response['results'])
                    print(f"   ✅ Found {len(response['results'])} results")
                
                # Rate limiting - be respectful
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                continue
        
        print(f"📊 Total search results: {len(all_results)}")
        return all_results
    
    def _process_search_results(self, results: List[Dict], product_info: Dict[str, Any]) -> List[ProductMatch]:
        """
        Process and filter search results to find actual product matches
        """
        product_matches = []
        
        # Known shopping domains (comprehensive list)
        shopping_domains = {
            'amazon.com', 'walmart.com', 'target.com', 'bestbuy.com', 'ebay.com',
            'newegg.com', 'wayfair.com', 'overstock.com', 'homedepot.com', 'lowes.com',
            'costco.com', 'macys.com', 'kohls.com', 'etsy.com', 'alibaba.com',
            'aliexpress.com', 'shopify.com', 'bigcommerce.com', 'woocommerce.com'
        }
        
        for result in results:
            try:
                url = result.get('url', '')
                title = result.get('title', '')
                content = result.get('content', '')
                score = result.get('score', 0.0)
                
                if not url or not title:
                    continue
                
                # Check if it's a shopping site
                domain = urlparse(url).netloc.lower().replace('www.', '')
                is_shopping_site = any(shop_domain in domain for shop_domain in shopping_domains)
                
                # Also check for shopping indicators in domain
                if not is_shopping_site:
                    shopping_indicators = ['shop', 'store', 'buy', 'market', 'mall', 'commerce']
                    is_shopping_site = any(indicator in domain for indicator in shopping_indicators)
                
                if not is_shopping_site:
                    continue
                
                # Check if it's likely a product page
                if not self._is_product_page(url, title, content):
                    continue
                
                # Calculate relevance to original product
                relevance = self._calculate_relevance(product_info['name'], title, content)
                if relevance < 0.1:  # Minimum 10% relevance
                    continue
                
                # Extract retailer name
                retailer = self._get_retailer_name(domain)
                
                # Extract price if available
                price = self._extract_price(title + ' ' + content)
                
                product_matches.append(ProductMatch(
                    title=title,
                    price=price,
                    retailer=retailer,
                    url=url,
                    content_snippet=content[:200],  # First 200 chars
                    relevance_score=relevance
                ))
                
            except Exception as e:
                continue
        
        # Sort by relevance score
        product_matches.sort(key=lambda x: x.relevance_score, reverse=True)
        
        print(f"🛒 Product matches found: {len(product_matches)}")
        return product_matches
    
    def _verify_and_enhance(self, matches: List[ProductMatch]) -> List[ProductMatch]:
        """
        Verify URLs work and enhance with additional data
        """
        verified_matches = []
        
        for match in matches:
            try:
                # Verify URL is accessible
                response = self.session.head(match.url, timeout=5, allow_redirects=True)
                
                if response.status_code in [200, 301, 302]:
                    match.verified = True
                    verified_matches.append(match)
                    print(f"✅ Verified: {match.retailer}")
                else:
                    print(f"❌ Failed: {match.retailer} (HTTP {response.status_code})")
                
                # Rate limiting
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Verification failed: {match.retailer} - {e}")
                continue
        
        return verified_matches
    
    def _is_product_page(self, url: str, title: str, content: str) -> bool:
        """Check if this is likely a product page"""
        
        # URL patterns that indicate product pages
        product_url_patterns = [
            r'/p/', r'/dp/', r'/item/', r'/product/', r'/buy/', r'-p-', r'/ip/'
        ]
        
        for pattern in product_url_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Content indicators
        combined_text = (title + ' ' + content).lower()
        product_indicators = ['price', 'buy', 'add to cart', 'shipping', 'reviews', 'rating', '$']
        
        indicator_count = sum(1 for indicator in product_indicators if indicator in combined_text)
        return indicator_count >= 2
    
    def _calculate_relevance(self, original_name: str, title: str, content: str) -> float:
        """Calculate how relevant this result is to the original product"""
        
        # Normalize text
        original_words = set(re.findall(r'\b\w+\b', original_name.lower()))
        candidate_words = set(re.findall(r'\b\w+\b', (title + ' ' + content).lower()))
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'with', 'for', 'buy', 'online', 'store'}
        original_words -= stop_words
        candidate_words -= stop_words
        
        if not original_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(original_words.intersection(candidate_words))
        union = len(original_words.union(candidate_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_retailer_name(self, domain: str) -> str:
        """Get clean retailer name from domain"""
        
        retailer_names = {
            'amazon.com': 'Amazon',
            'walmart.com': 'Walmart',
            'target.com': 'Target',
            'bestbuy.com': 'Best Buy',
            'ebay.com': 'eBay',
            'newegg.com': 'Newegg',
            'wayfair.com': 'Wayfair',
            'overstock.com': 'Overstock',
            'homedepot.com': 'Home Depot',
            'lowes.com': "Lowe's",
            'costco.com': 'Costco',
            'macys.com': "Macy's",
            'kohls.com': "Kohl's",
            'etsy.com': 'Etsy'
        }
        
        for known_domain, name in retailer_names.items():
            if known_domain in domain:
                return name
        
        # Fallback: extract from domain
        domain_parts = domain.split('.')
        if domain_parts:
            return domain_parts[0].replace('-', ' ').title()
        
        return 'Online Store'
    
    def _extract_price(self, text: str) -> Optional[str]:
        """Extract price from text"""
        if not text:
            return None
        
        # Price patterns
        price_patterns = [
            r'\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*dollars?'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return f"${matches[0]}"
        
        return None


def test_tavily_product_comparison():
    """Test the Tavily product comparison system"""
    
    API_KEY = "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"
    
    print("🧪 TESTING TAVILY PRODUCT COMPARISON")
    print("="*60)
    
    # Create comparison engine
    engine = TavilyProductComparison(api_key=API_KEY)
    
    # Test with mushroom lamp
    test_url = "https://www.amazon.com/Dawnwake-Mushroom-Nightstand-Dimmable-Aesthetic/dp/B0D1FRDFFX/"
    
    try:
        alternatives = engine.find_product_alternatives(test_url)
        
        if alternatives:
            print(f"\n🎯 FOUND {len(alternatives)} VERIFIED ALTERNATIVES:")
            
            for i, alt in enumerate(alternatives, 1):
                print(f"\n#{i} - {alt.retailer}")
                print(f"   Product: {alt.title}")
                print(f"   Price: {alt.price or 'Not available'}")
                print(f"   Relevance: {alt.relevance_score:.1%}")
                print(f"   Verified: {'✅' if alt.verified else '❌'}")
                print(f"   🔗 Link: {alt.url}")
        else:
            print("❌ No alternatives found")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_tavily_product_comparison()