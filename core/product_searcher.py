#!/usr/bin/env python3
"""
Product Searcher - Uses Selenium to find real products on Google
"""

from typing import List, Dict, Optional
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from .selenium_engine import SeleniumEngine


@dataclass
class SearchResult:
    title: str
    url: str
    retailer: str
    snippet: str = ""
    price: Optional[str] = None
    verified: bool = False


class ProductSearcher:
    """
    Searches for products using real Google search via Selenium
    """
    
    def __init__(self, use_proxy: bool = True):
        self.selenium_engine = SeleniumEngine(use_proxy=use_proxy)
        
        # Known shopping domains for filtering
        self.shopping_domains = {
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
            'bhphotovideo.com': 'B&H Photo',
            'etsy.com': 'Etsy',
            'aliexpress.com': 'AliExpress',
            'shopify.com': 'Shopify Store',
            'macys.com': "Macy's",
            'kohls.com': "Kohl's",
            'jcpenney.com': 'JCPenney',
            'sears.com': 'Sears',
            'nordstrom.com': 'Nordstrom',
            'zappos.com': 'Zappos'
        }
    
    def search_for_product(self, product_info: Dict[str, any], exclude_domain: str = None) -> List[SearchResult]:
        """
        Search Google for the same/similar product
        """
        print(f"🔍 Searching for product: {product_info['title']}")
        
        # Generate search queries
        search_queries = self._generate_search_queries(product_info, exclude_domain)
        
        all_results = []
        
        for query in search_queries:
            print(f"🔍 Query: '{query}'")
            
            # Use Selenium to search Google
            raw_results = self.selenium_engine.google_search(query)
            
            if raw_results:
                # Filter and process results
                shopping_results = self._filter_shopping_results(raw_results, product_info)
                all_results.extend(shopping_results)
                
                # Stop if we have enough results
                if len(all_results) >= 15:
                    break
        
        # Remove duplicates and rank
        unique_results = self._deduplicate_results(all_results)
        
        print(f"✅ Found {len(unique_results)} unique shopping results")
        return unique_results[:10]  # Return top 10
    
    def _generate_search_queries(self, product_info: Dict[str, any], exclude_domain: str = None) -> List[str]:
        """
        Generate effective Google search queries
        """
        title = product_info.get('title', '')
        brand = product_info.get('brand', '')
        category = product_info.get('category', 'general')
        search_terms = product_info.get('search_terms', [])
        
        queries = []
        
        # Query 1: Full title + "buy"
        if title:
            query = f'"{title}" buy online'
            if exclude_domain:
                query += f' -site:{exclude_domain}'
            queries.append(query)
        
        # Query 2: Brand + key terms + category
        if brand and search_terms:
            key_terms = ' '.join(search_terms[:3])  # Top 3 terms
            query = f'{brand} {key_terms} buy'
            if exclude_domain:
                query += f' -site:{exclude_domain}'
            queries.append(query)
        
        # Query 3: Category-specific search
        if category != 'general' and search_terms:
            if category == 'lighting':
                query = f'{" ".join(search_terms[:2])} lamp light buy'
            elif category == 'electronics':
                query = f'{" ".join(search_terms[:2])} electronics buy'
            elif category == 'furniture':
                query = f'{" ".join(search_terms[:2])} furniture buy'
            else:
                query = f'{" ".join(search_terms[:3])} {category} buy'
            
            if exclude_domain:
                query += f' -site:{exclude_domain}'
            queries.append(query)
        
        # Query 4: Simple product search
        if search_terms:
            query = f'{" ".join(search_terms[:4])} shop online'
            if exclude_domain:
                query += f' -site:{exclude_domain}'
            queries.append(query)
        
        return queries[:3]  # Use top 3 queries to avoid too many requests
    
    def _filter_shopping_results(self, raw_results: List[Dict[str, str]], product_info: Dict[str, any]) -> List[SearchResult]:
        """
        Filter raw Google results to find shopping/product pages
        """
        shopping_results = []
        
        for result in raw_results:
            try:
                url = result['url']
                title = result['title']
                snippet = result.get('snippet', '')
                
                # Check if it's from a shopping site
                retailer = self._identify_retailer(url)
                if not retailer:
                    continue
                
                # Check if it's actually a product page (not just homepage)
                if not self._is_product_page(url, title, snippet):
                    continue
                
                # Check if it's related to our original product
                if not self._is_related_product(product_info, title, snippet):
                    continue
                
                # Extract price if available in title/snippet
                price = self._extract_price_from_text(title + " " + snippet)
                
                shopping_results.append(SearchResult(
                    title=title,
                    url=url,
                    retailer=retailer,
                    snippet=snippet[:150],  # First 150 chars
                    price=price
                ))
            
            except Exception as e:
                continue  # Skip this result if processing fails
        
        return shopping_results
    
    def _identify_retailer(self, url: str) -> Optional[str]:
        """
        Identify retailer from URL
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            # Remove www. prefix
            domain = domain.replace('www.', '')
            
            # Check known shopping domains
            for shop_domain, retailer_name in self.shopping_domains.items():
                if shop_domain in domain:
                    return retailer_name
            
            # Check for common shopping patterns
            if any(pattern in domain for pattern in ['shop', 'store', 'buy', 'mall', 'market']):
                # Extract store name from domain
                domain_parts = domain.split('.')
                if domain_parts:
                    store_name = domain_parts[0].replace('-', ' ').title()
                    return f"{store_name} Store"
            
            return None
            
        except Exception:
            return None
    
    def _is_product_page(self, url: str, title: str, snippet: str) -> bool:
        """
        Check if URL is actually a product page
        """
        # URL patterns that indicate product pages
        product_url_patterns = [
            r'/p/',  # /p/product-name
            r'/dp/',  # /dp/B123456789 (Amazon)
            r'/item/',  # /item/123456
            r'/product/',  # /product/name
            r'/buy/',  # /buy/product
            r'-p-',  # product-name-p-123456
            r'/ip/',  # /ip/product (Walmart)
        ]
        
        # Check URL patterns
        for pattern in product_url_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Check title/snippet for product indicators
        product_indicators = [
            'buy', 'price', '$', 'sale', 'discount', 'order', 'cart', 'shipping',
            'reviews', 'rating', 'stars', 'specifications', 'features'
        ]
        
        combined_text = (title + " " + snippet).lower()
        product_score = sum(1 for indicator in product_indicators if indicator in combined_text)
        
        return product_score >= 2  # At least 2 product indicators
    
    def _is_related_product(self, original_product: Dict[str, any], title: str, snippet: str) -> bool:
        """
        Check if search result is related to original product
        """
        original_title = original_product.get('title', '').lower()
        category = original_product.get('category', 'general')
        search_terms = original_product.get('search_terms', [])
        
        combined_text = (title + " " + snippet).lower()
        
        # Category-specific matching
        if category == 'lighting':
            lighting_terms = ['lamp', 'light', 'led', 'bulb', 'fixture']
            if any(term in combined_text for term in lighting_terms):
                return True
        
        elif category == 'electronics':
            if original_product.get('brand'):
                brand = original_product['brand'].lower()
                if brand in combined_text:
                    return True
        
        # General similarity check using search terms
        if search_terms:
            # Count how many search terms appear in the result
            term_matches = sum(1 for term in search_terms if term.lower() in combined_text)
            similarity_ratio = term_matches / len(search_terms)
            
            return similarity_ratio >= 0.3  # At least 30% of terms match
        
        # Fallback: basic word overlap
        original_words = set(re.findall(r'\b\w+\b', original_title))
        result_words = set(re.findall(r'\b\w+\b', combined_text))
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'with', 'for', 'buy', 'online', 'shop'}
        original_words -= stop_words
        result_words -= stop_words
        
        if len(original_words) == 0:
            return False
        
        overlap = len(original_words.intersection(result_words))
        similarity = overlap / len(original_words)
        
        return similarity >= 0.25  # 25% word overlap
    
    def _extract_price_from_text(self, text: str) -> Optional[str]:
        """
        Extract price from text
        """
        if not text:
            return None
        
        price_patterns = [
            r'\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',
            r'Price:?\s*\$?(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return f"${matches[0]}"
        
        return None
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove duplicate results and sort by relevance
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Sort by retailer popularity (Amazon, Walmart, Target first)
        retailer_priority = {
            'Amazon': 1, 'Walmart': 2, 'Target': 3, 'Best Buy': 4, 'eBay': 5,
            'Newegg': 6, 'Wayfair': 7, 'Costco': 8, 'Home Depot': 9, "Lowe's": 10
        }
        
        def sort_key(result):
            priority = retailer_priority.get(result.retailer, 99)
            has_price = 0 if result.price else 1  # Prefer results with prices
            return (priority, has_price)
        
        unique_results.sort(key=sort_key)
        
        return unique_results
    
    def close(self):
        """Close the Selenium engine"""
        if self.selenium_engine:
            self.selenium_engine.close_session()


def test_product_searcher():
    """Test the product searcher"""
    
    # Mock product info (normally comes from ProductAnalyzer)
    product_info = {
        'title': 'Dawnwake Mushroom Nightstand Dimmable Aesthetic',
        'brand': 'Dawnwake',
        'category': 'lighting',
        'search_terms': ['dawnwake', 'mushroom', 'nightstand', 'dimmable', 'aesthetic']
    }
    
    print("🧪 TESTING PRODUCT SEARCHER")
    print("="*50)
    
    searcher = ProductSearcher(use_proxy=False)  # Start without proxy for testing
    
    try:
        results = searcher.search_for_product(product_info, exclude_domain='amazon.com')
        
        if results:
            print(f"\n🎯 FOUND {len(results)} PRODUCT RESULTS:")
            
            for i, result in enumerate(results[:5], 1):
                print(f"\n#{i} - {result.retailer}")
                print(f"   Title: {result.title}")
                print(f"   Price: {result.price or 'Not listed'}")
                print(f"   URL: {result.url}")
                if result.snippet:
                    print(f"   Info: {result.snippet[:80]}...")
        else:
            print("❌ No product results found")
    
    finally:
        searcher.close()


if __name__ == "__main__":
    test_product_searcher()