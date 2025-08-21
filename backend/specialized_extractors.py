"""
Domain-specific extraction rules for popular websites
"""
DOMAIN_RULES = {
    "amazon.com": {
        "product": {
            "selectors": [".product-title", "#productTitle", "[data-cy='title']"],
            "attributes": ["text"]
        },
        "price": {
            "selectors": [".price", ".a-price", "[data-cy='price']"],
            "attributes": ["text"]
        },
        "rating": {
            "selectors": [".ratings", ".reviewCount", "[data-cy='rating']"],
            "attributes": ["text"]
        },
        "images": {
            "selectors": [".product-image", "#landingImage", "[data-cy='image']"],
            "attributes": ["src", "data-src"]
        }
    },
    "github.com": {
        "repository": {
            "selectors": [".repo-name", "[itemprop='name']", "[data-cy='repo-name']"],
            "attributes": ["text"]
        },
        "description": {
            "selectors": [".repository-meta", "[itemprop='description']"],
            "attributes": ["text"]
        },
        "stars": {
            "selectors": [".social-count", "#repo-stars"],
            "attributes": ["text"]
        },
        "language": {
            "selectors": [".language-color", "[itemprop='programmingLanguage']"],
            "attributes": ["text"]
        }
    },
    "twitter.com": {
        "tweet": {
            "selectors": ["[data-testid='tweet']", ".tweet"],
            "attributes": ["text"]
        },
        "username": {
            "selectors": ["[data-testid='User-Name']", ".username"],
            "attributes": ["text"]
        },
        "timestamp": {
            "selectors": ["time"],
            "attributes": ["datetime"]
        },
        "metrics": {
            "selectors": ["[data-testid='like']", "[data-testid='retweet']", "[data-testid='reply']"],
            "attributes": ["text"]
        }
    },
    "reddit.com": {
        "post": {
            "selectors": ["[data-testid='post-container']", ".Post"],
            "attributes": ["text"]
        },
        "title": {
            "selectors": ["h1", "[data-testid='post-title']"],
            "attributes": ["text"]
        },
        "score": {
            "selectors": ["[data-testid='post-score']", ".score"],
            "attributes": ["text"]
        },
        "comments": {
            "selectors": ["[data-testid='comments']", ".comments"],
            "attributes": ["text"]
        }
    }
}

def get_domain_specific_rules(url):
    """
    Get extraction rules for a specific domain
    """
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    
    # Remove www prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Check for exact match
    if domain in DOMAIN_RULES:
        return DOMAIN_RULES[domain]
    
    # Check for partial match (subdomains)
    for site_domain in DOMAIN_RULES:
        if domain.endswith(site_domain):
            return DOMAIN_RULES[site_domain]
    
    return None