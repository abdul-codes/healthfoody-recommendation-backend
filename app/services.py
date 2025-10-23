import hashlib
import json
import re
from typing import Any, cast
from datetime import datetime, timedelta, timezone

from google import genai
from sqlalchemy.future import select

from app.config import GEMINI_API_KEY
from app.db import AsyncSessionLocal, NutritionCache
from app.models import (
    DietaryPrinciple,
    FoodItem,  
    FoodRecommendationResponse,
    RecommendationRequest,
    SearchType,
)
from app.schemas import GeminiResponse

NUTRITION_CACHE_TTL_DAYS = 30


def _get_request_hash(request: RecommendationRequest) -> str:
    # Use model_dump_json to get a consistent JSON string representation
    request_string = request.model_dump_json(sort_keys=True)
    return hashlib.sha256(request_string.encode()).hexdigest()


def _clean_json_response(text: str) -> str:
    """Extracts the JSON content from a Gemini response that might include markdown."""
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


async def get_recommendations(
    request: RecommendationRequest,
) -> FoodRecommendationResponse:
    """
     getting food recommendations, using a database cache to avoid
    repeated Gemini API calls.
    """
    request_hash = _get_request_hash(request)
    gemini_data: GeminiResponse | None = None

    # 1. Check the database cache first
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(NutritionCache).where(NutritionCache.request_hash == request_hash)
            )
            cached = result.scalar_one_or_none()

            if cached and cached.last_updated > datetime.now(timezone.utc) - timedelta(
                days=NUTRITION_CACHE_TTL_DAYS
            ):
                print(f"Cache HIT for hash: {request_hash}")
                gemini_data = cast(GeminiResponse, cached.response)
        except Exception as e:
            print(f"Database cache read error: {e}")

    # 2. If not in cache or expired, call the Gemini API
    if gemini_data is None:
        print(f"Cache MISS for hash: {request_hash}. Calling Gemini API.")
        base_prompt = "As a nutritionist,"
        if request.search_type == SearchType.GOAL:
            prompt_core = f" for a person whose goal is '{request.value}',"
        elif request.search_type == SearchType.COUNTRY:
            prompt_core = f" list healthy foods and foods to avoid that are common in '{request.value}'."
        else:
            prompt_core = f" for a person with '{request.value}',"

        country_constraint = (
            f" The recommendations should be foods commonly found in '{request.country}'."
            if request.country
            else ""
        )

        full_prompt = f"""
        {base_prompt}{prompt_core} provide a list of 4 recommended foods and 4 foods to strictly avoid.
        For each food, give a brief reason. Also, provide 3 key dietary principles relevant to the query.{country_constraint}
        Output in the following JSON format:
        {{
          "recommended_foods": [{{"name": "Food Name", "reason": "Reason"}}],
          "foods_to_avoid": [{{"name": "Food Name", "reason": "Reason"}}],
          "dietary_principles": [{{"principle": "Principle", "explanation": "Explanation"}}]
        }}
        """

        try:
            client = (
                genai.Client(api_key=GEMINI_API_KEY)
                if GEMINI_API_KEY
                else genai.Client()
            )
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash", contents=full_prompt
            )
            if response.text:
                cleaned_json = _clean_json_response(response.text)
                gemini_data = cast(GeminiResponse, json.loads(cleaned_json))

                # 3. Save the new response to the cache
                async with AsyncSessionLocal() as db:
                    try:
                        existing = await db.get(NutritionCache, request_hash)
                        if existing:
                            existing.response = gemini_data
                            existing.last_updated = datetime.now(timezone.utc)
                        else:
                            new_cache_entry = NutritionCache(
                                request_hash=request_hash,
                                response=gemini_data,
                                last_updated=datetime.now(timezone.utc),
                            )
                            db.add(new_cache_entry)
                        await db.commit()
                    except Exception as e:
                        print(f"Database cache write error: {e}")
                        await db.rollback()

        except (json.JSONDecodeError, AttributeError, Exception) as e:
            print(f"Error processing Gemini response: {e}")

    # If Gemini call fails or returns no data, provide a default empty response
    if gemini_data is None:
        gemini_data = {
            "recommended_foods": [],
            "foods_to_avoid": [],
            "dietary_principles": [],
        }

    # 4. Process the final data into the response model
    recommended_foods = [
        FoodItem(name=item["name"], reason=item["reason"])
        for item in gemini_data.get("recommended_foods", [])
        if isinstance(item, dict) and "name" in item and "reason" in item
    ]
    foods_to_avoid = [
        FoodItem(name=item["name"], reason=item["reason"])
        for item in gemini_data.get("foods_to_avoid", [])
        if isinstance(item, dict) and "name" in item and "reason" in item
    ]
    dietary_principles = [
        DietaryPrinciple(principle=item["principle"], explanation=item["explanation"])
        for item in gemini_data.get("dietary_principles", [])
        if isinstance(item, dict) and "principle" in item and "explanation" in item
    ]

    return FoodRecommendationResponse(
        recommended_foods=recommended_foods,
        foods_to_avoid=foods_to_avoid,
        dietary_principles=dietary_principles,
    )
