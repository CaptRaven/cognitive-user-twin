from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routers import simulate, recommend, review, timeline, analytics
from apps.api.config import settings
import logging
import random
from typing import List, Dict, Any
from core.retrieval.embedding_service import EmbeddingService
from core.retrieval.chroma_store import ChromaStore

logger = logging.getLogger(__name__)

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

def generate_synthetic_businesses() -> List[Dict[str, Any]]:
    """Generates a diverse set of 100+ synthetic businesses for the simulation."""
    categories = [
        # --- NIGERIAN / LOCAL ARCHETYPES ---
        ("Mama Put Express", "Nigerian, Fast Food, Quick Service", 15.0, 4.2, 500, "busy", "affordable", "spicy, local, quick"),
        ("The Place", "Nigerian, Fast Food, Popular", 18.0, 4.1, 2000, "crowded", "budget", "variety, local, reliable"),
        ("Glover Court Suya", "Nigerian, Street Food, Famous", 12.0, 4.8, 1200, "authentic", "budget", "suya, local, spicy"),
        ("Yellow Chilli", "Nigerian, Modern, Restaurant", 55.0, 4.5, 400, "modern", "mid-range", "jollof, gourmet, upscale"),
        ("Terra Kulture", "Nigerian, Cultural, Cafe", 40.0, 4.6, 350, "cultural", "mid-range", "art, local, quiet"),
        ("Nok by Alara", "African, Fine Dining, Upscale", 150.0, 4.8, 120, "sophisticated", "luxury", "artistic, authentic, expensive"),
        ("Iya Eba", "Traditional, Nigerian, Bukka", 10.0, 4.4, 800, "local", "budget", "swallow, authentic, loud"),
        ("Bukly", "Nigerian, Fast Food, Modern", 25.0, 3.8, 150, "clean", "affordable", "jollof, chicken, quick"),
        
        # --- CAFE / COMFORT / WORK SPOTS ---
        ("The Tea Room VI", "Cafe, Bakery, Comfort Food", 45.0, 4.5, 200, "relaxing", "mid-range", "dessert, cozy, floral"),
        ("Eric Kayser", "Bakery, French, Cafe", 35.0, 4.4, 400, "chic", "mid-range", "pastries, coffee, bread"),
        ("Art Cafe", "Cafe, Artistic, Breakfast", 30.0, 4.5, 300, "bohemian", "mid-range", "coffee, art, chill"),
        ("Vestar Coffee", "Specialty Coffee, Workspace, Cafe", 25.0, 4.7, 150, "minimalist", "affordable", "coffee, wifi, work"),
        ("Mai Shayi Coffee", "Hausa, Coffee, Traditional", 15.0, 4.3, 100, "simple", "budget", "coffee, spicy, unique"),
        ("Ice Cream Factory", "Dessert, Ice Cream, Sweet", 20.0, 4.7, 900, "cheerful", "affordable", "sweets, kids, treats"),
        ("HSE Gourmet", "Comfort Food, Fusion, Bistro", 65.0, 4.6, 250, "elegant", "premium", "pasta, comfort, upscale"),

        # --- INTERNATIONAL / UPSCALE / FUSION ---
        ("Burger King Ikeja", "Fast Food, International, Reliable", 25.0, 3.9, 1500, "standard", "affordable", "burgers, quick, chain"),
        ("Zen Garden", "Chinese, Restaurant, Family", 60.0, 4.3, 300, "quiet", "mid-range", "dim sum, oriental, traditional"),
        ("Hard Rock Cafe", "International, Bar, Entertainment", 90.0, 4.4, 600, "loud", "premium", "music, cocktails, burgers"),
        ("Bungalow Restaurant", "Sushi, Mexican, Variety", 75.0, 4.3, 450, "trendy", "premium", "fusion, sushi, cocktails"),
        ("Shiro Lagos", "Pan-Asian, Upscale, Fine Dining", 180.0, 4.7, 250, "luxury", "luxury", "sushi, teppanyaki, lounge"),
        ("RSVP Lagos", "International, Modern, Bar", 110.0, 4.6, 300, "exclusive", "luxury", "pool, lounge, fine-dining"),
        ("Ocean Basket", "Seafood, Chain, Family", 50.0, 4.0, 700, "casual", "mid-range", "prawns, fish, platters"),
        ("Talindo Steak House", "Steakhouse, Fine Dining, Classic", 130.0, 4.5, 180, "classic", "luxury", "steak, wine, formal"),
        ("Izumi", "Japanese, Sushi, Quiet", 95.0, 4.4, 120, "serene", "premium", "sushi, authentic, quiet"),

        # --- LATE NIGHT / BARS / VIBRANT ---
        ("Sailor's Lounge", "Seafood, Waterfront, Bar", 85.0, 4.2, 550, "scenic", "premium", "cocktails, view, breeze"),
        ("Late Night Suya Spot", "Street Food, Nigerian, Late Night", 10.0, 4.6, 800, "vibrant", "budget", "suya, night-out, local"),
        ("Cactus Restaurant", "International, View, Family", 70.0, 4.3, 800, "lively", "premium", "view, terrace, variety"),
        ("W Bar", "Lounge, Bar, Nightlife", 120.0, 4.1, 400, "energetic", "luxury", "music, cocktails, elite"),
        ("Zaza Lagos", "Lounge, Mediterranean, Party", 140.0, 4.3, 200, "opulent", "luxury", "party, dinner-show, exotic"),
        ("The Backyard", "Grill, Bar, Casual", 50.0, 4.2, 450, "outdoor", "mid-range", "burgers, beer, garden"),
        
        # --- NEW DIVERSE ARCHETYPES ---
        ("Wellness Bowl", "Healthy, Salad, Vegetarian", 45.0, 4.5, 100, "zen", "mid-range", "healthy, vegan, fresh"),
        ("The Grid Lagos", "Grill, Modern, Casual", 40.0, 4.2, 180, "industrial", "mid-range", "ribs, wings, chill"),
        ("Flowershop Cafe", "Cafe, Flower Shop, Brunch", 55.0, 4.6, 220, "floral", "premium", "brunch, coffee, aesthetic"),
        ("Danfo Bistro", "Nigerian, Fusion, Trendy", 35.0, 4.4, 320, "urban", "mid-range", "local, fusion, quirky"),
        ("Indigo", "Indian, Authentic, Family", 50.0, 4.3, 280, "warm", "mid-range", "curry, naan, traditional")
    ]
    
    # Generate 100+ variations
    businesses = []
    for i in range(4): # Create 4 variations of each to reach ~140 items
        for name, cats, price, stars, reviews, ambiance, friendliness, tags in categories:
            # Add some randomness to metrics for variation
            v_stars = max(1.0, min(5.0, stars + random.uniform(-0.3, 0.3)))
            v_price = price * random.uniform(0.9, 1.1)
            
            biz_id = f"biz_{name.lower().replace(' ', '_')}_{i}"
            businesses.append({
                "business_id": biz_id,
                "name": f"{name} {'' if i==0 else f'({i+1})'}",
                "categories": cats,
                "stars": v_stars,
                "review_count": int(reviews * random.uniform(0.8, 1.2)),
                "price": v_price,
                "ambiance": ambiance,
                "budget_friendliness": friendliness,
                "cuisine_tags": tags,
                "delivery_speed": 0.8 if "Fast Food" in cats or "Quick" in cats else 0.4,
                "popularity": reviews / 2000.0,
                "late_night": "Late Night" in cats or "Bar" in cats or "Lounge" in cats,
                "stress_comfort_score": 0.9 if any(x in cats for x in ["Comfort", "Bakery", "Dessert", "Nigerian"]) else 0.4
            })
    return businesses

async def populate_vector_store():
    """Populates ChromaDB with synthetic businesses only if not already populated."""
    logger.info("Checking ChromaDB state...")
    
    # 1. Initialize services
    chroma_store = ChromaStore(persist_directory=settings.chroma_dir)
    
    # Check if businesses collection already exists and has data
    try:
        count = chroma_store.business_coll.count()
        if count > 0:
            logger.info(f"ChromaDB already has {count} businesses - skipping population.")
            return
    except Exception as e:
        logger.warning(f"Could not check collection count: {e}")
    
    logger.info("Starting Vector Store Population...")
    
    # 2. Initialize embedding service
    embedding_service = EmbeddingService()
    
    # 3. Get synthetic data
    businesses = generate_synthetic_businesses()
    logger.info(f"Generated {len(businesses)} synthetic businesses.")
    
    # 4. Process and embed
    ids = []
    embeddings = []
    metadatas = []
    
    for biz in businesses:
        # Create a rich summary for embedding
        summary = (
            f"Business: {biz['name']}. Categories: {biz['categories']}. "
            f"Ambiance: {biz['ambiance']}. Price: {biz['budget_friendliness']}. "
            f"Tags: {biz['cuisine_tags']}. Rating: {biz['stars']:.1f} stars. "
            f"Keywords: {biz['cuisine_tags']}, {biz['ambiance']}, {biz['budget_friendliness']}."
        )
        
        emb = embedding_service.embed_text(summary).tolist()
        
        ids.append(biz['business_id'])
        embeddings.append(emb)
        metadatas.append({
            "name": biz['name'],
            "categories": biz['categories'],
            "stars": biz['stars'],
            "review_count": biz['review_count'],
            "price": biz['price'],
            "ambiance": biz['ambiance'],
            "budget_friendliness": biz['budget_friendliness'],
            "cuisine_tags": biz['cuisine_tags'],
            "delivery_speed": biz['delivery_speed'],
            "popularity": biz['popularity'],
            "late_night": int(biz['late_night']),
            "stress_comfort_score": biz['stress_comfort_score']
        })
        
    # 5. Add to Chroma
    logger.info(f"Adding {len(ids)} businesses to ChromaDB...")
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        chroma_store.add_businesses(ids[i:end], embeddings[i:end], metadatas[i:end])
        logger.info(f"Inserted batch {i//batch_size + 1}")
    
    count = chroma_store.business_coll.count()
    logger.info(f"Successfully populated vector store. Total businesses in collection: {count}")

@app.on_event("startup")
async def startup_event():
    import asyncio
    # Run population in background to avoid blocking server startup
    asyncio.create_task(populate_vector_store())

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
