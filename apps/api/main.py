from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routers import simulate, recommend, review, timeline, analytics
from apps.api.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade API for AI behavioral simulation and recommendation.",
    version=settings.APP_VERSION
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(simulate.router, prefix="/simulate", tags=["Simulation"])
app.include_router(recommend.router, prefix="/recommend", tags=["Recommendation"])
app.include_router(review.router, prefix="/review", tags=["Review Generation"])
app.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Cognitive User Twin API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
