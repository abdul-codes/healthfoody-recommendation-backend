from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.models import RecommendationRequest, FoodRecommendationResponse
from app.services import get_recommendations
from dotenv import load_dotenv
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Healthy Food Recommender API",
    description="An AI-powered API to recommend healthy foods for various health conditions.",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Healthy Food Recommender API"}


@app.post("/recommendations", response_model=FoodRecommendationResponse)
async def get_food_recommendations(request: RecommendationRequest):

    logger.info(f"Received recommendation request: {request.model_dump_json()}")

    if not request.value:
        raise HTTPException(
            status_code=400, detail="The 'value' field cannot be empty."
        )

    try:
        recommendations = await get_recommendations(request)
        return recommendations
    except Exception as e:
        logger.error(
            "An error occurred in the recommendations endpoint:", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
