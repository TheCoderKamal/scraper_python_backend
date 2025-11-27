import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import social_router, article_router, image_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="Recipe Scraper API",
    description="Extract recipes from social media, articles, and images",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(social_router)
app.include_router(article_router)
app.include_router(image_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Recipe Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "social": "/scrape/social",
            "article": "/scrape/article",
            "image": "/scrape/image"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)