from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running on Render!"}

@app.get("/scrape")
def scrape(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return JSONResponse(content={"extracted_text": text[:500]})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
