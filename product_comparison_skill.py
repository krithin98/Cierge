#!/usr/bin/env python3
"""
Product Comparison Skill using Tavily API
Complete product comparison system that actually works
"""

from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, quote_plus
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import time
import random


@dataclass
class ProductResult:
    title: str
    price: Optional[str]
    retailer: str
    product_url: str
    snippet: str = ""
    similarity_score: float = 0.0
    verified: bool = False


class ProductComparisonEngine:
    """
    Complete product comparison engine using Tavily API
    """
    
    def __init__(self, tavily_api_key: str):
        self.tavily_client = TavilyClient(api_key=tavily_api_key)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
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
            'macys.com': "Macy's",
            'kohls.com': "Kohl's",
            'brightech.com': 'Brightech',
            'nordicnest.com': 'Nordic Nest',
            'ozarke.com': 'Ozarke'
        }
    
    def find_best_alternatives(self, product_url: str, max_results: int = 5) -> List[ProductResult]:
        """
        Main function: Find best alternative products for a given URL
        """
        print(f"🔍 Finding alternatives for: {product_url}")
        
        # Step 1: Analyze the original product
        product_info = self._analyze_product_url(product_url)
        if not product_info:
            print("❌ Could not analyze product")
            return []
        
        print(f"✅ Analyzed: {product_info['title']}")
        print(f"📂 Category: {product_info['category']}")
        
        # Step 2: Search web using Tavily
        search_results = self._search_with_tavily(product_info)
        
        # Step 3: Filter for shopping sites
        shopping_results = self._filter_shopping_results(search_results, product_info)
        
        # Step 4: Verify URLs and extract prices
        verified_results = self._verify_and_enhance_results(shopping_results)
        
        # Step 5: Rank results
        ranked_results = self._rank_results(verified_results)
        
        # Return top results
        final_results = ranked_results[:max_results]
        
        print(f"🎯 Found {len(final_results)} verified alternatives")
        return final_results
    
    def _analyze_product_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract product information from URL
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            product_info = {
                'original_url': url,
                'domain': domain,
                'title': None,
                'brand': None,
                'category': 'general',
                'search_terms': []
            }
            
            # Extract product name from URL structure
            if 'amazon.com' in domain:
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and len(part) > 10 and 'dp' not in part and not part.startswith('B0'):
                        title = part.replace('-', ' ').title()
                        if len(title.split()) >= 3:
                            product_info['title'] = title
                            break
            
            elif 'walmart.com' in domain:
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and len(part) > 15:
                        title = part.replace('-', ' ').title()
                        if len(title.split()) >= 3:
                            product_info['title'] = title
                            break
            
            else:
                # Generic extraction
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and len(part) > 8:
                        potential_title = part.replace('-', ' ').replace('_', ' ').title()
                        if len(potential_title.split()) >= 2:
                            product_info['title'] = potential_title
                            break
            
            # Enhance product info if we got a title
            if product_info['title']:
                title = product_info['title']
                words = title.split()
                
                # Extract brand (first word)
                product_info['brand'] = words[0] if words else None
                
                # Categorize product
                title_lower = title.lower()
                if any(word in title_lower for word in ['lamp', 'light', 'led', 'bulb']):
                    product_info['category'] = 'lighting'
                elif any(word in title_lower for word in ['iphone', 'phone', 'smartphone']):
                    product_info['category'] = 'electronics'
                elif any(word in title_lower for word in ['chair', 'table', 'furniture']):
                    product_info['category'] = 'furniture'
                
                # Generate search terms
                product_info['search_terms'] = [w.lower() for w in words if len(w) > 2][:6]
                
                return product_info
            
            return None
            
        except Exception as e:
            print(f"❌ Error analyzing product: {e}")
            return None
    
    def _search_with_tavily(self, product_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Search for similar products using Tavily API
        """
        try:
            title = product_info['title']
            category = product_info['category']
            exclude_domain = product_info['domain']
            
            # Create search queries
            queries = []
            
            # Query 1: Full title + "buy online"
            queries.append(f'"{title}" buy online')
            
            # Query 2: Category-specific search
            if category == 'lighting':
                queries.append(f'{" ".join(product_info["search_terms"][:3])} lamp light buy')
            elif category == 'electronics':
                queries.append(f'{" ".join(product_info["search_terms"][:3])} electronics buy')
            else:
                queries.append(f'{" ".join(product_info["search_terms"][:4])} buy online')
            
            all_results = []
            
            for query in queries[:2]:  # Use top 2 queries
                print(f"🔍 Tavily search: '{query}'")
                
                try:
                    # Use Tavily search
                    response = self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        max_results=10,
                        include_domains=None,
                        exclude_domains=[exclude_domain] if exclude_domain else None
                    )
                    
                    # Extract results
                    if 'results' in response:
                        for result in response['results']:
                            all_results.append({
                                'title': result.get('title', ''),
                                'url': result.get('url', ''),
                                'content': result.get('content', ''),
                                'score': result.get('score', 0.0)
                            })
                    
                    print(f"✅ Found {len(response.get('results', []))} results")
                    
                    # Small delay between queries
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Tavily search error: {e}")
                    continue
            
            print(f"🎯 Total Tavily results: {len(all_results)}")
            return all_results
            
        except Exception as e:
            print(f"❌ Tavily search failed: {e}")
            return []
    
    def _filter_shopping_results(self, results: List[Dict[str, str]], product_info: Dict[str, Any]) -> List[ProductResult]:
        """
        Filter results to only include shopping sites
        """
        shopping_results = []
        
        for result in results:
            try:
                url = result['url']
                title = result['title']
                content = result.get('content', '')
                
                # Check if it's a shopping site
                retailer = self._identify_retailer(url)
                if not retailer:
                    continue
                
                # Check if it's actually a product page
                if not self._is_product_page(url, title, content):
                    continue
                
                # Check similarity to original product (be more lenient)
                similarity = self._calculate_similarity(product_info['title'], title)
                if similarity < 0.1:  # 10% minimum similarity (more lenient)
                    continue
                
                # Extract price from title/content
                price = self._extract_price_from_text(title + " " + content)
                
                shopping_results.append(ProductResult(
                    title=title,
                    price=price,
                    retailer=retailer,
                    product_url=url,
                    snippet=content[:150],
                    similarity_score=similarity
                ))
            
            except Exception as e:
                continue
        
        print(f"🛒 Shopping results: {len(shopping_results)}")
        return shopping_results
    
    def _verify_and_enhance_results(self, results: List[ProductResult]) -> List[ProductResult]:
        """
        Verify URLs work and enhance with additional data
        """
        verified_results = []
        
        for result in results:
            try:
                # Verify URL works
                response = self.session.head(result.product_url, timeout=5, allow_redirects=True)
                
                if response.status_code in [200, 301, 302]:
                    result.verified = True
                    verified_results.append(result)
                    print(f"✅ Verified: {result.retailer} - {result.product_url[:50]}...")
                else:
                    print(f"❌ Failed: {result.retailer} - HTTP {response.status_code}")
                
                # Small delay between requests
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ Verification failed: {result.retailer} - {e}")
                continue
        
        print(f"✅ Verified results: {len(verified_results)}")
        return verified_results
    
    def _rank_results(self, results: List[ProductResult]) -> List[ProductResult]:
        """
        Rank results by price, similarity, and retailer trust
        """
        # Retailer trust scores (higher is better)
        retailer_trust = {
            'Amazon': 10, 'Walmart': 9, 'Target': 8, 'Best Buy': 8,
            'Costco': 7, 'Newegg': 6, 'Wayfair': 6, 'eBay': 5
        }
        
        def ranking_score(result):
            # Price score (lower price = higher score)
            price_score = 0
            if result.price:
                try:
                    price_val = float(result.price.replace('$', '').replace(',', ''))
                    price_score = 1000 / price_val  # Inverse relationship
                except:
                    price_score = 0
            
            # Similarity score (higher is better)
            similarity_score = result.similarity_score * 100
            
            # Trust score (higher is better)
            trust_score = retailer_trust.get(result.retailer, 3)
            
            # Combined score
            total_score = (price_score * 0.4) + (similarity_score * 0.4) + (trust_score * 0.2)
            return total_score
        
        # Sort by ranking score (highest first)
        results.sort(key=ranking_score, reverse=True)
        return results
    
    def _identify_retailer(self, url: str) -> Optional[str]:
        """Identify retailer from URL"""
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            
            # Check known shopping domains
            for shop_domain, retailer_name in self.shopping_domains.items():
                if shop_domain in domain:
                    return retailer_name
            
            # Check for generic shopping indicators
            shopping_indicators = ['shop', 'store', 'buy', 'commerce', 'market']
            if any(indicator in domain for indicator in shopping_indicators):
                # Extract store name from domain
                domain_parts = domain.split('.')
                if domain_parts:
                    store_name = domain_parts[0].replace('-', ' ').title()
                    return f"{store_name} Store"
            
            return None
            
        except Exception:
            return None
    
    def _is_product_page(self, url: str, title: str, content: str) -> bool:
        """Check if URL is a product page"""
        # URL patterns that indicate product pages
        product_patterns = [r'/p/', r'/dp/', r'/item/', r'/product/', r'-p-', r'/ip/']
        
        for pattern in product_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Content indicators
        product_indicators = ['price', 'buy', 'cart', 'shipping', 'reviews', 'rating']
        combined_text = (title + " " + content).lower()
        
        indicator_count = sum(1 for indicator in product_indicators if indicator in combined_text)
        return indicator_count >= 2
    
    def _calculate_similarity(self, original: str, candidate: str) -> float:
        """Calculate similarity between product titles"""
        if not original or not candidate:
            return 0.0
        
        # Normalize and split
        orig_words = set(re.findall(r'\b\w+\b', original.lower()))
        cand_words = set(re.findall(r'\b\w+\b', candidate.lower()))
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'with', 'for', 'buy', 'online'}
        orig_words -= stop_words
        cand_words -= stop_words
        
        if not orig_words:
            return 0.0
        
        # Jaccard similarity
        intersection = len(orig_words.intersection(cand_words))
        union = len(orig_words.union(cand_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_price_from_text(self, text: str) -> Optional[str]:
        """Extract price from text"""
        if not text:
            return None
        
        price_patterns = [
            r'\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*dollars?'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return f"${matches[0]}"
        
        return None


def test_product_comparison_skill():
    """Test the product comparison skill"""
    
    # Your Tavily API key
    API_KEY = "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"
    
    print("🧪 TESTING PRODUCT COMPARISON SKILL")
    print("="*60)
    
    # Create engine
    engine = ProductComparisonEngine(tavily_api_key=API_KEY)
    
    # Test with mushroom lamp
    test_url = "https://www.amazon.com/Dawnwake-Mushroom-Nightstand-Dimmable-Aesthetic/dp/B0D1FRDFFX/"
    
    print(f"🔍 Testing with: {test_url}")
    
    try:
        results = engine.find_best_alternatives(test_url, max_results=5)
        
        if results:
            print(f"\n🎯 FOUND {len(results)} BEST ALTERNATIVES:")
            
            for i, result in enumerate(results, 1):
                print(f"\n#{i} - {result.retailer}")
                print(f"   Product: {result.title}")
                print(f"   Price: {result.price or 'Not available'}")
                print(f"   Similarity: {result.similarity_score:.1%}")
                print(f"   Verified: {'✅' if result.verified else '❌'}")
                print(f"   🔗 Link: {result.product_url}")
        else:
            print("❌ No alternatives found")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_product_comparison_skill()