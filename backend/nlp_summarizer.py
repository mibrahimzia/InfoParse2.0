import logging
import re

logger = logging.getLogger("webtapi.nlp")

def generate_natural_language_summary(data, query):
    """
    Generate a natural language summary from extracted data
    """
    try:
        summary_parts = []
        
        # Extract metadata
        if "metadata" in data:
            url = data["metadata"].get("url", "the website")
            summary_parts.append(f"Based on the content extracted from {url}:")
        
        # Handle different content types
        if "content" in data:
            content = data["content"]
            
            # Article content
            if "article" in content:
                article = content["article"]
                title = article.get("title", "the content")
                summary_parts.append(f"The article '{title}' discusses: {article.get('content', '')[:200]}...")
            
            # Images
            if "images" in content and content["images"]:
                image_count = len(content["images"])
                summary_parts.append(f"Found {image_count} images on the page.")
            
            # Tables
            if "tables" in content and content["tables"]:
                table_count = len(content["tables"])
                summary_parts.append(f"Extracted {table_count} tables with structured data.")
            
            # Links
            if "links" in content and content["links"]:
                link_count = len(content["links"])
                summary_parts.append(f"Found {link_count} links on the page.")
            
            # Custom extracted data
            for key, value in content.items():
                if key not in ["article", "images", "tables", "links"] and value:
                    if isinstance(value, list):
                        summary_parts.append(f"Found {len(value)} {key} items.")
                    else:
                        summary_parts.append(f"Extracted {key} information.")
        
        # If no specific content was extracted, provide a generic summary
        if len(summary_parts) <= 1:  # Only has the URL part
            summary_parts.append("The content has been successfully extracted and is available in structured format.")
        
        return " ".join(summary_parts)
    
    except Exception as e:
        logger.error(f"Natural language generation failed: {str(e)}")
        return "The content has been extracted and is available in structured format below."