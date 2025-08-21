from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from cachetools import TTLCache
from datetime import timedelta
import uuid
import logging
from .security import validate_url
from .ai_interpreter import parse_query
from .scraper import extract_data
from .crawler import crawl_website

@app.post("/crawl")
async def crawl_website_endpoint(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        query = data.get("query")
        max_pages = data.get("max_pages", 10)
        
        if not url or not query:
            raise HTTPException(400, "Missing required parameters: url or query")
        
        # Security validation
        if not validate_url(url):
            raise HTTPException(400, "URL failed security checks or is not publicly accessible")
        
        # Crawl the website
        crawled_data = crawl_website(url, query, max_pages)
        
        # Create API endpoint
        endpoint_id = str(uuid.uuid4())
        cache[endpoint_id] = {
            "data": crawled_data,
            "output_format": "JSON",
            "expires": timedelta(hours=24)
        }
        
        return JSONResponse({
            "api_endpoint": f"/api/{endpoint_id}",
            "sample_data": crawled_data[:3]  # Return first 3 pages as sample
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Crawling failed: {str(e)}")
        raise HTTPException(500, "Crawling failed")



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webtapi")

app = FastAPI(
    title="WebToAPI Converter",
    description="Convert websites to reusable API endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache configuration
cache = TTLCache(maxsize=1000, ttl=86400)  # Default 24-hour cache

@app.post("/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        query = data.get("query")
        output_format = data.get("output_format", "JSON")
        cache_hours = data.get("cache_hours", 24)
        
        # Validate inputs
        if not url or not query:
            raise HTTPException(400, "Missing required parameters: url or query")
        
        # Security validation
        if not validate_url(url):
            raise HTTPException(400, "URL failed security checks or is not publicly accessible")
        
        # Parse natural language query
        extraction_plan = parse_query(query)
        
        # Extract data from website
        extracted_data = extract_data(url, extraction_plan)
        
        # Create API endpoint
        endpoint_id = str(uuid.uuid4())
        cache[endpoint_id] = {
            "data": extracted_data,
            "output_format": output_format,
            "expires": timedelta(hours=cache_hours)
        }
        
        return JSONResponse({
            "api_endpoint": f"/api/{endpoint_id}",
            "sample_data": extracted_data
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(500, "Internal server error")

@app.get("/api/{endpoint_id}")
async def get_data(endpoint_id: str):
    data = cache.get(endpoint_id)
    if not data:
        raise HTTPException(404, "Endpoint expired or not found")
    return data["data"]

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}