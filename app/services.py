from typing import Any, cast
from google import genai
import httpx
import json
from app.models import FoodRecommendationResponse, FoodItem, DietaryPrinciple
import re
from app.config import USDA_API_KEY, GEMINI_API_KEY
from app.types import GeminiResponse, NutrientData
from collections.abc import Mapping

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
    As a nutritionist, for a person with '{condition}', provide a list of 5 recommended foods and 5 foods to strictly avoid.
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
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        if not response.text:
            return {"recommended_foods": [], "foods_to_avoid": [], "dietary_principles": []}    
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
    async with httpx.AsyncClient() as client:
        # Step 1: Search for the food to get its FDC ID
        search_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        search_params = {"query": food_name, "api_key": USDA_API_KEY, "pageSize": 1}

        try:
            search_response = await client.get(search_url, params=search_params)
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
            report_response = await client.get(report_url, params=report_params)
            report_response.raise_for_status()
            report_data = report_response.json()
            
            nutrients = _create_default_nutrients()

            for nutrient in report_data.get("foodNutrients", []):
                # Nutrient names and their corresponding keys in our model
                nutrient_map: Mapping[str, str] = {                    "Energy": "calories",
                    "Protein": "protein",
                    "Carbohydrate, by difference": "carbohydrates",
                    "Total lipid (fat)": "fat",
                    "Sugars, total including NLEA": "sugar",
                    "Sodium, Na": "sodium",
                }
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
    Orchestrates the process of getting food recommendations asynchronously.
    """
    gemini_data = await get_gemini_recommendations(condition)

    recommended_foods: list[FoodItem]  = []
    for item in gemini_data.get("recommended_foods", []):
        nutrition_data = await get_usda_nutrition_data(item["name"])
        food_item = FoodItem(
            name=item["name"],
            reason=item["reason"],
            **nutrition_data)
        recommended_foods.append(food_item)

    foods_to_avoid = []
    for item in gemini_data.get("foods_to_avoid", []):
        nutrition_data = await get_usda_nutrition_data(item["name"])
        food_item = FoodItem(
            name=item["name"],
            reason=item["reason"],
            **nutrition_data
        )
        foods_to_avoid.append(food_item)

    dietary_principles = [
        DietaryPrinciple( 
            principle=item["principle"],
            explanation=item["explanation"]) for item in gemini_data.get("dietary_principles", [])
    ]

    return FoodRecommendationResponse(
        recommended_foods=recommended_foods,
        foods_to_avoid=foods_to_avoid,
        dietary_principles=dietary_principles,
    )
