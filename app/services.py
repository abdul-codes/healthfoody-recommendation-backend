from typing import Any, cast
from google import genai
import httpx
import json
import asyncio
from app.models import (
    FoodRecommendationResponse,
    FoodItem,
    DietaryPrinciple,
    RecommendationRequest,
    SearchType,
)
import re
from app.config import USDA_API_KEY, GEMINI_API_KEY
from app.types import GeminiResponse, NutrientData
from collections.abc import Mapping
from async_lru import alru_cache
from app.db import AsyncSessionLocal, NutritionCache
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from datetime import datetime, timedelta

HTTP_CLIENT = httpx.AsyncClient(
    timeout=httpx.Timeout(15.0),
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
)


def clean_json_response(text: str) -> str:
    # Use regex to find and extract the content within the first set of ```json ... ``` block
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()  # Fallback


@alru_cache(maxsize=128)
async def get_gemini_recommendations(
    search_type: SearchType, value: str, country: str | None
) -> GeminiResponse:
    """
    Queries the Gemini API asynchronously for food recommendations based on the search parameters.
    Results are cached to avoid repeated API calls for the same query.
    """
    # Dynamically build the prompt based on the request
    base_prompt = "As a nutritionist,"

    if search_type == SearchType.GOAL:
        prompt_core = f" for a person whose goal is '{value}',"
    elif search_type == SearchType.COUNTRY:
        prompt_core = (
            f" list healthy foods and foods to avoid that are common in '{value}'."
        )
    else:  # Default to CONDITION
        prompt_core = f" for a person with '{value}',"

    # Add the country constraint if provided
    if country:
        country_constraint = (
            f" The recommendations should be foods commonly found in '{country}'."
        )
    else:
        country_constraint = ""
    # Combine the parts into a full prompt
    full_prompt = f"""
    {base_prompt}{prompt_core} provide a list of 4 recommended foods and 4 foods to strictly avoid.
    For each food, give a brief reason. Also, provide 3 key dietary principles relevant to the query.{country_constraint}
    Output in the following JSON format:
    {{
      "recommended_foods": [
        {{"name": "Food Name", "reason": "Reason"}},
        ...
      ],
      "foods_to_avoid": [
        {{"name": "Food Name", "reason": "Reason"}},
        ...
      ],
      "dietary_principles": [
        {{"principle": "Principle", "explanation": "Explanation"}},
        ...
      ]
    }}
    """

    try:
        client = (
            genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else genai.Client()
        )
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash", contents=full_prompt
        )
        if not response.text:
            return {
                "recommended_foods": [],
                "foods_to_avoid": [],
                "dietary_principles": [],
            }
        # Clean the response to remove markdown and parse JSON
        cleaned_json = clean_json_response(response.text)
        parsed_data = json.loads(cleaned_json)
        return cast(GeminiResponse, parsed_data)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error processing Gemini response: {e}")
        return {"recommended_foods": [], "foods_to_avoid": [], "dietary_principles": []}


def _create_default_nutrients() -> NutrientData:
    """Create default nutrient data with proper types."""
    return {
        "calories": None,
        "protein": None,
        "carbohydrates": None,
        "fat": None,
        "sugar": None,
        "sodium": None,
    }


def _extract_nutrient_value(nutrient_data: dict[str, Any]) -> float | None:
    """Safely extract nutrient value from USDA API response."""
    amount = nutrient_data.get("amount")
    if amount is None:
        return None

    # Handle both numeric values and strings
    try:
        return float(amount) if amount else None
    except (ValueError, TypeError):
        return None


NUTRITION_CACHE_TTL_DAYS = 30  # Re-fetch every 30 days


async def get_usda_nutrition_data(food_name: str) -> NutrientData:
    """Check cache first, then USDA API with proper async operations."""

    # Check cache first
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(NutritionCache).where(NutritionCache.food_name == food_name)
            )
            # Explicitly type cached as a NutritionCache instance to aid type checking
            cached: NutritionCache | None = result.scalar_one_or_none()

            if (
                cached is not None
                and cached.last_updated
                > datetime.now(timezone.utc) - timedelta(days=NUTRITION_CACHE_TTL_DAYS) # Fix: Use timezone.utc and now()
            ):
                # Fix: Explicitly cast attribute values to float | None for NutrientData return type
                return {
                    "calories": cast(float | None, cached.calories),
                    "protein": cast(float | None, cached.protein),
                    "carbohydrates": cast(float | None, cached.carbohydrates),
                    "fat": cast(float | None, cached.fat),
                    "sugar": cast(float | None, cached.sugar),
                    "sodium": cast(float | None, cached.sodium),
                }
        except Exception as e:
            print(f"Cache read error: {e}")

    # If not in cache or expired, call USDA API
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    search_params = {
        "query": food_name,
        "api_key": USDA_API_KEY,
        "pageSize": 1,
        "dataType": "Foundation,SR Legacy",  # Prioritize high-quality data
    }

    try:
        search_response = await HTTP_CLIENT.get(search_url, params=search_params)
        # Fix: Assign to '_' to indicate the return value is intentionally not used
        _ = search_response.raise_for_status()
        # Fix: Cast to provide a more specific type than 'Any' for search_data
        search_data = cast(dict[str, Any], search_response.json())

        if not search_data.get("foods"):
            return _create_default_nutrients()

        # The search result itself contains the nutrient data. No need for a second call.
        # Fix: Cast to provide a more specific type than 'Any' for food_details
        food_details = cast(dict[str, Any], search_data["foods"][0])
        nutrients_result = _create_default_nutrients() # Renamed to avoid conflict if 'nutrients' was a general concept

        nutrient_map: Mapping[str, str] = {
            "Energy": "calories",
            "Protein": "protein",
            "Carbohydrate, by difference": "carbohydrates",
            "Total lipid (fat)": "fat",
            "Sugars, total including NLEA": "sugar",
            "Sodium, Na": "sodium",
        }

        # Fix: Cast nutrient_item_raw and use _extract_nutrient_value for safe parsing
        for nutrient_item_raw in food_details.get("foodNutrients", []):
            nutrient_item = cast(dict[str, Any], nutrient_item_raw)
            nutrient_name = nutrient_item.get("nutrientName")
            if nutrient_name in nutrient_map:
                key = nutrient_map[nutrient_name]
                nutrients_result[key] = _extract_nutrient_value(nutrient_item)

        # Save to cache with proper async operations
        async with AsyncSessionLocal() as db:
            try:
                # Check if record exists and update, or create new
                result = await db.execute(
                    select(NutritionCache).where(NutritionCache.food_name == food_name)
                )
                # Explicitly type existing as a NutritionCache instance to aid type checking
                existing: NutritionCache | None = result.scalar_one_or_none()

                if existing:
                    # Update existing record
                    # Assuming NutritionCache attributes are correctly typed (e.g., Mapped[Optional[float]])
                    existing.calories = nutrients_result.get("calories")
                    existing.protein = nutrients_result.get("protein")
                    existing.carbohydrates = nutrients_result.get("carbohydrates")
                    existing.fat = nutrients_result.get("fat")
                    existing.sugar = nutrients_result.get("sugar")
                    existing.sodium = nutrients_result.get("sodium")
                    existing.last_updated = datetime.now(timezone.utc) # Fix: Use timezone.utc and now()
                else:
                    # Create new record
                    new_cache = NutritionCache(
                        food_name=food_name,
                        calories=nutrients_result.get("calories"),
                        protein=nutrients_result.get("protein"),
                        carbohydrates=nutrients_result.get("carbohydrates"),
                        fat=nutrients_result.get("fat"),
                        sugar=nutrients_result.get("sugar"),
                        sodium=nutrients_result.get("sodium"),
                        last_updated=datetime.now(timezone.utc), # Fix: Use timezone.utc and now()
                    )
                    db.add(new_cache)

                await db.commit()
            except Exception as e:
                await db.rollback()
                print(f"Cache save error: {e}")

        return nutrients_result

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return _create_default_nutrients()
    except Exception as e:
        print(f"An error occurred: {e}")
        return _create_default_nutrients()


async def get_recommendations(
    request: RecommendationRequest,
) -> FoodRecommendationResponse:
    """
    Orchestrates the process of getting food recommendations asynchronously with parallel processing.
    """
    # Get Gemini recommendations first
    gemini_data = await get_gemini_recommendations(
        request.search_type, request.value, request.country
    )

    # Collect all food names for parallel nutrition API calls
    food_names = []
    for item in gemini_data.get("recommended_foods", []):
        if isinstance(item, dict) and "name" in item:
            food_names.append(item["name"])

    for item in gemini_data.get("foods_to_avoid", []):
        if isinstance(item, dict) and "name" in item:
            food_names.append(item["name"])

    # Fetch all nutrition data in parallel (MUCH FASTER!)
    nutrition_tasks = [get_usda_nutrition_data(name) for name in food_names]
    nutrition_results = await asyncio.gather(*nutrition_tasks, return_exceptions=True)

    # Process recommended foods
    recommended_foods: list[FoodItem] = []
    recommended_items = gemini_data.get("recommended_foods", [])

    for i, item in enumerate(recommended_items):
        if isinstance(item, dict) and "name" in item and "reason" in item:
            # Get corresponding nutrition data safely
            nutrition_data_raw = (
                nutrition_results[i] if i < len(nutrition_results) else None
            )

            if isinstance(nutrition_data_raw, dict):
                nutrition_data = nutrition_data_raw
            else:
                # This branch handles cases where the API call failed (it's an exception)
                # or the index was out of bounds.
                nutrition_data = _create_default_nutrients()

            food_item = FoodItem(
                name=item["name"],
                reason=item["reason"],
                calories=nutrition_data.get("calories"),
                protein=nutrition_data.get("protein"),
                carbohydrates=nutrition_data.get("carbohydrates"),
                fat=nutrition_data.get("fat"),
                sugar=nutrition_data.get("sugar"),
                sodium=nutrition_data.get("sodium"),
            )
            recommended_foods.append(food_item)

    # Process foods to avoid
    foods_to_avoid: list[FoodItem] = []
    avoid_items = gemini_data.get("foods_to_avoid", [])
    start_index = len(recommended_items)

    for i, item in enumerate(avoid_items):
        if isinstance(item, dict) and "name" in item and "reason" in item:
            # Get corresponding nutrition data safely
            result_index = start_index + i
            nutrition_data_raw = (
                nutrition_results[result_index]
                if result_index < len(nutrition_results)
                else None
            )

            if isinstance(nutrition_data_raw, dict):
                nutrition_data = nutrition_data_raw
            else:
                # This branch handles cases where the API call failed (it's an exception)
                # or the index was out of bounds.
                nutrition_data = _create_default_nutrients()

            food_item = FoodItem(
                name=item["name"],
                reason=item["reason"],
                calories=nutrition_data.get("calories"),
                protein=nutrition_data.get("protein"),
                carbohydrates=nutrition_data.get("carbohydrates"),
                fat=nutrition_data.get("fat"),
                sugar=nutrition_data.get("sugar"),
                sodium=nutrition_data.get("sodium"),
            )
            foods_to_avoid.append(food_item)

    # Process dietary principles (unchanged)
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
