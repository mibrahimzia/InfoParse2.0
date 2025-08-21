import logging
import re
import json

logger = logging.getLogger("webtapi.ai")

def pattern_based_interpreter(query: str) -> dict:
    """
    Enhanced pattern-based interpreter with better query understanding
    """
    query_lower = query.lower()
    
    # Price and product detection
    if any(word in query_lower for word in ['price', 'cost', '$', 'buy', 'purchase', 'product']):
        return {
            "elements": ["text"],
            "filters": {
                "include_selectors": [".price", ".cost", "[class*='price']", "[class*='cost']", 
                                     "[itemprop*='price']", ".product-price", ".amount"],
                "exclude_selectors": [".header", ".footer", ".nav", ".menu", ".ad"],
                "content_patterns": [r'\$\d+\.?\d*', r'\d+\.?\d*\s*(USD|EUR|GBP)']
            },
            "structured_format": "list"
        }
    
    # Image detection
    elif any(word in query_lower for word in ['image', 'picture', 'photo', 'img', 'gallery']):
        return {
            "elements": ["images"],
            "filters": {
                "include_selectors": ["img", "[class*='image']", "[class*='photo']", "[class*='gallery']"],
                "exclude_selectors": [".icon", ".logo", ".avatar", "[width<20]", "[height<20]"]
            },
            "structured_format": "list"
        }
    
    # Table detection
    elif any(word in query_lower for word in ['table', 'chart', 'data', 'statistics', 'figure']):
        return {
            "elements": ["tables"],
            "filters": {
                "include_selectors": ["table", "[class*='table']", "[class*='data']", "[class*='chart']"]
            },
            "structured_format": "table"
        }
    
    # Contact information
    elif any(word in query_lower for word in ['contact', 'email', 'phone', 'address', 'tel']):
        return {
            "elements": ["text", "links"],
            "filters": {
                "include_selectors": ["[href*='mailto:']", "[href*='tel:']", "[class*='contact']", 
                                    "[class*='address']", "[class*='phone']"],
                "content_patterns": [
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                    r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
                ]
            },
            "structured_format": "list"
        }
    
    # News/articles
    elif any(word in query_lower for word in ['news', 'article', 'blog', 'post', 'headline']):
        return {
            "elements": ["text", "links"],
            "filters": {
                "include_selectors": [".article", ".post", ".blog", ".news", "h1", "h2", "h3", "p",
                                     "[class*='title']", "[class*='headline']", "[class*='content']"],
                "exclude_selectors": [".nav", ".menu", ".sidebar", ".ad", ".comment", ".footer"]
            },
            "structured_format": "list"
        }
    
    # Social media elements
    elif any(word in query_lower for word in ['comment', 'like', 'share', 'follower', 'social']):
        return {
            "elements": ["text"],
            "filters": {
                "include_selectors": [".comment", ".like", ".share", ".follower", ".social",
                                     "[class*='reaction']", "[class*='engagement']"],
                "exclude_selectors": [".ad", ".promoted", ".sponsored"]
            },
            "structured_format": "list"
        }
    
    # Default extraction - more focused
    else:
        return {
            "elements": ["text"],
            "filters": {
                "include_selectors": ["h1", "h2", "h3", "p", "ul", "ol"],
                "exclude_selectors": [".nav", ".menu", ".sidebar", ".ad", ".header", ".footer",
                                     ".comment", ".social", ".share"]
            },
            "structured_format": "list"
        }

def parse_query(query: str) -> dict:
    """
    Convert natural language query to extraction instructions
    Using enhanced pattern matching instead of AI model
    """
    logger.info(f"Parsing query: {query}")
    result = enhanced_pattern_interpreter(query)
    logger.info(f"Extraction plan: {result}")
    return result