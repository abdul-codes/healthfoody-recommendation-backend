from typing import Any, cast
from google import genai
import httpx
import json
import asyncio
from app.models import FoodRecommendationResponse, FoodItem, DietaryPrinciple
import re
from app.config import USDA_API_KEY, GEMINI_API_KEY
from app.types import GeminiResponse, NutrientData
from collections.abc import Mapping

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


async def get_gemini_recommendations(condition: str) -> GeminiResponse:
    """
    Queries the Gemini API asynchronously for food recommendations.
    """
    prompt = f"""
    As a nutritionist, for a person with '{condition}', provide a list of 4 recommended foods and 4 foods to strictly avoid.
    For each food, give a brief reason. Also, provide 3 key dietary principles for this condition, with a brief explanation for each.
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
            model="gemini-2.5-flash", contents=prompt
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


async def get_usda_nutrition_data(food_name: str) -> NutrientData:
    """
    Queries the USDA FoodData Central API asynchronously for nutritional data.
    This is a two-step process: first search for the food's FDC ID, then get the data.
    """
    # Step 1: Search for the food to get its FDC ID
    search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    search_params = {"query": food_name, "api_key": USDA_API_KEY, "pageSize": 1}

    try:
        search_response = await HTTP_CLIENT.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data.get("foods"):
            return {
                "calories": None,
                "protein": None,
                "carbohydrates": None,
                "fat": None,
                "sugar": None,
                "sodium": None,
            }

        fdc_id = search_data["foods"][0]["fdcId"]

        # Step 2: Retrieve the food report using the FDC ID
        report_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
        report_params = {"api_key": USDA_API_KEY}
        report_response = await HTTP_CLIENT.get(report_url, params=report_params)
        report_response.raise_for_status()
        report_data = report_response.json()

        nutrients = _create_default_nutrients()

        # Nutrient names and their corresponding keys in our model
        nutrient_map: Mapping[str, str] = {
            "Energy": "calories",
            "Protein": "protein",
            "Carbohydrate, by difference": "carbohydrates",
            "Total lipid (fat)": "fat",
            "Sugars, total including NLEA": "sugar",
            "Sodium, Na": "sodium",
        }

        for nutrient in report_data.get("foodNutrients", []):
            nutrient_name = nutrient.get("nutrient", {}).get("name")
            if nutrient_name in nutrient_map:
                key = nutrient_map[nutrient_name]
                nutrients[key] = nutrient.get("amount", 0.0)

        return nutrients

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return {
            "calories": None,
            "protein": None,
            "carbohydrates": None,
            "fat": None,
            "sugar": None,
            "sodium": None,
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            "calories": None,
            "protein": None,
            "carbohydrates": None,
            "fat": None,
            "sugar": None,
            "sodium": None,
        }


async def get_recommendations(condition: str) -> FoodRecommendationResponse:
    """
    Orchestrates the process of getting food recommendations asynchronously with parallel processing.
    """
    # Get Gemini recommendations first
    gemini_data = await get_gemini_recommendations(condition)

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
