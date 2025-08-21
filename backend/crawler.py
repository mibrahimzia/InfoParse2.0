import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import time
import re
from collections import deque
from .scraper import extract_data
from .ai_interpreter import parse_query

logger = logging.getLogger("webtapi.crawler")

class WebsiteCrawler:
    def __init__(self, delay=1, max_pages=50, max_depth=3):
        self.delay = delay
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_domain(self, url):
        """Extract domain from URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def is_same_domain(self, url, base_url):
        """Check if URL belongs to the same domain"""
        return self.get_domain(url) == self.get_domain(base_url)
    
    def get_links(self, url, html_content):
        """Extract all links from HTML content"""
        soup = BeautifulSoup(html_content, 'lxml')
        links = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Resolve relative URLs
            full_url = urljoin(url, href)
            
            # Only include links from the same domain
            if self.is_same_domain(full_url, url):
                # Normalize URL by removing fragments
                normalized_url = full_url.split('#')[0]
                links.add(normalized_url)
        
        return list(links)
    
    def fetch_page(self, url):
        """Fetch a page with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text, True
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None, False
    
    def crawl(self, start_url, query, extraction_plan):
        """
        Crawl a website and extract data from multiple pages
        """
        domain = self.get_domain(start_url)
        queue = deque([(start_url, 0)])  # (url, depth)
        results = []
        page_count = 0
        
        while queue and page_count < self.max_pages:
            url, depth = queue.popleft()
            
            if url in self.visited or depth > self.max_depth:
                continue
                
            self.visited.add(url)
            logger.info(f"Crawling: {url} (depth: {depth})")
            
            # Fetch the page
            html_content, success = self.fetch_page(url)
            if not success:
                continue
                
            # Extract data from the page
            try:
                page_data = extract_data(url, extraction_plan)
                page_data["url"] = url
                page_data["depth"] = depth
                results.append(page_data)
                page_count += 1
            except Exception as e:
                logger.error(f"Failed to extract data from {url}: {str(e)}")
            
            # Get links from this page for further crawling
            if depth < self.max_depth:
                links = self.get_links(url, html_content)
                for link in links:
                    if link not in self.visited and link not in [u for u, d in queue]:
                        queue.append((link, depth + 1))
            
            # Respectful delay
            time.sleep(self.delay)
        
        return results

def crawl_website(start_url, query, max_pages=50, max_depth=3):
    """Main function to crawl a website"""
    extraction_plan = parse_query(query)
    crawler = WebsiteCrawler(max_pages=max_pages, max_depth=max_depth)
    return crawler.crawl(start_url, query, extraction_plan)