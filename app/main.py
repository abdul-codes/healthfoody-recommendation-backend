from fastapi import FastAPI, HTTPException
from app.models import HealthConditionRequest, FoodRecommendationResponse
from app.services import get_recommendations
from dotenv import load_dotenv
import os

load_dotenv() 

app = FastAPI(
    title="Healthy Food Recommender API",
    description="An AI-powered API to recommend healthy foods for various health conditions.",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Healthy Food Recommender API"}


@app.post("/recommendations", response_model=FoodRecommendationResponse)
async def get_food_recommendations(request: HealthConditionRequest):
    """
    Get food recommendations for a given health condition.
    """
    if not request.condition:
        raise HTTPException(status_code=400, detail="Health condition cannot be empty.")

    try:
        recommendations = await get_recommendations(request.condition)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
