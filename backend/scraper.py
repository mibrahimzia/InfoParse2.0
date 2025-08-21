import requests
from bs4 import BeautifulSoup
import pandas as pd
from htmldate import find_date
import re
from urllib.parse import urljoin, urlparse
import logging
import random
from .specialized_extractors import get_domain_specific_rules

logger = logging.getLogger("webtapi.scraper")

def get_random_user_agent():
    """Return a random user agent to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
    return random.choice(user_agents)

def extract_with_selectors(soup, selectors, attributes=None):
    """
    Extract content using CSS selectors
    """
    results = []
    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            if attributes:
                for attr in attributes:
                    if attr == "text":
                        results.append(element.get_text(strip=True))
                    else:
                        results.append(element.get(attr, ""))
            else:
                results.append(element.get_text(strip=True))
    return results

def extract_article_content(html_content, url):
    """
    Extract article content using trafilatura
    """
    try:
        from trafilatura import extract
        article_text = extract(html_content, url=url)
        if article_text:
            # Extract title from the HTML
            soup = BeautifulSoup(html_content, 'lxml')
            title = soup.find('title')
            title_text = title.get_text() if title else "No title found"
            
            return {
                "title": title_text,
                "content": article_text
            }
    except Exception as e:
        logger.warning(f"Article extraction with trafilatura failed: {str(e)}")
    
    # Fallback: simple paragraph extraction
    soup = BeautifulSoup(html_content, 'lxml')
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    title = soup.find('title')
    title_text = title.get_text() if title else "No title found"
    
    return {
        "title": title_text,
        "content": "\n\n".join(paragraphs)
    }

def extract_data(url: str, plan: dict) -> dict:
    """Extract structured data based on AI-generated plan"""
    try:
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Check for domain-specific rules
        domain_rules = get_domain_specific_rules(url)
        
        results = {
            "metadata": {
                "url": url,
                "timestamp": find_date(response.text) or "Unknown",
                "status_code": response.status_code,
                "domain_rules_applied": domain_rules is not None
            },
            "content": {}
        }
        
        # Extract based on AI plan
        if "text" in plan["elements"]:
            article_content = extract_article_content(response.text, url)
            results["content"]["article"] = article_content
        
        # Apply domain-specific rules if available
        if domain_rules:
            for content_type, rules in domain_rules.items():
                if content_type in plan["elements"] or "all" in plan["elements"]:
                    extracted = extract_with_selectors(soup, rules["selectors"], rules.get("attributes"))
                    if extracted:
                        results["content"][content_type] = extracted
        
        # Generic extraction for elements not covered by domain rules
        if "images" in plan["elements"] and "images" not in results["content"]:
            images = []
            for img in soup.find_all("img"):
                src = img.get("src", "") or img.get("data-src", "")
                if not src:
                    continue
                    
                # Resolve relative URLs
                src = urljoin(url, src)
                
                images.append({
                    "src": src,
                    "alt": img.get("alt", "")[:100],
                    "width": img.get("width"),
                    "height": img.get("height")
                })
            results["content"]["images"] = images
        
        if "tables" in plan["elements"] and "tables" not in results["content"]:
            tables = []
            for i, table in enumerate(soup.find_all("table")):
                try:
                    df = pd.read_html(str(table))[0]
                    tables.append({
                        "table_index": i,
                        "html": str(table),
                        "markdown": df.to_markdown(),
                        "json": df.to_dict(orient="records")
                    })
                except Exception as e:
                    logger.debug(f"Table extraction failed: {str(e)}")
                    continue
            results["content"]["tables"] = tables
        
        if "links" in plan["elements"] and "links" not in results["content"]:
            links = []
            for a in soup.find_all("a"):
                href = a.get("href", "")
                if not href or href.startswith(("#", "javascript:")):
                    continue
                    
                # Resolve relative URLs
                href = urljoin(url, href)
                
                links.append({
                    "text": a.get_text(strip=True)[:200],
                    "href": href
                })
            results["content"]["links"] = links
        
        # Apply content pattern filters if specified
        if plan.get("filters", {}).get("content_patterns"):
            filtered_content = {}
            for content_type, content_data in results["content"].items():
                if isinstance(content_data, list):
                    filtered_items = []
                    for item in content_data:
                        if isinstance(item, str):
                            # Check if any pattern matches
                            for pattern in plan["filters"]["content_patterns"]:
                                if re.search(pattern, item, re.IGNORECASE):
                                    filtered_items.append(item)
                                    break
                        elif isinstance(item, dict):
                            # Check all string values in the dict
                            for key, value in item.items():
                                if isinstance(value, str):
                                    for pattern in plan["filters"]["content_patterns"]:
                                        if re.search(pattern, value, re.IGNORECASE):
                                            filtered_items.append(item)
                                            break
                                    if item in filtered_items:
                                        break
                    filtered_content[content_type] = filtered_items
                else:
                    filtered_content[content_type] = content_data
            results["content"] = filtered_content
        
        return results
        
    except requests.exceptions.RequestException as re:
        logger.error(f"Network error: {str(re)}")
        raise Exception("Network error occurred during scraping")
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise Exception("Data extraction failed")