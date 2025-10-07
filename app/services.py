from google import genai
import httpx
import json
from app.config import EDAMAM_APP_ID, EDAMAM_APP_KEY
from app.models import FoodRecommendationResponse, FoodItem, DietaryPrinciple
import re

def clean_json_response(text: str) -> str:
    # Use regex to find and extract the content within the first set of ```json ... ``` block
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip() # Fallback

async def get_gemini_recommendations(condition: str) -> dict:
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
        # The client automatically uses the GEMINI_API_KEY from the .env file
        client = genai.Client()
        response = await client.models.generate_content_async( # <-- CORRECT METHOD
            model="gemini-2.5-flash", contents=prompt
        )
        # Clean the response to remove markdown and parse JSON
        cleaned_json = clean_json_response(response.text) 
        return json.loads(cleaned_json)
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error processing Gemini response: {e}")
        return {"recommended_foods": [], "foods_to_avoid": [], "dietary_principles": []}


async def get_edamam_nutrition_data(food_name: str) -> dict:
    """
    Queries the Edamam API asynchronously for nutritional data for a given food.
    """

    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {"ingr": food_name, "app_id": EDAMAM_APP_ID, "app_key": EDAMAM_APP_KEY}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get("parsed"):
            nutrients = data["parsed"][0]["food"]["nutrients"]
            return {
                "calories": nutrients.get("ENERC_KCAL"),
                "protein": nutrients.get("PROCNT"),
                "carbohydrates": nutrients.get("CHOCDF"),
                "fat": nutrients.get("FAT"),
                "sugar": nutrients.get("SUGAR"),
                "sodium": nutrients.get("NA"),
            }
    return {}


async def get_recommendations(condition: str) -> FoodRecommendationResponse:
    """
    Orchestrates the process of getting food recommendations asynchronously.
    """
    gemini_data = await get_gemini_recommendations(condition)

    recommended_foods = []
    for item in gemini_data.get("recommended_foods", []):
        nutrition_data = await get_edamam_nutrition_data(item["name"])
        food_item = FoodItem(**item, **nutrition_data)
        recommended_foods.append(food_item)

    foods_to_avoid = []
    for item in gemini_data.get("foods_to_avoid", []):
        nutrition_data = await get_edamam_nutrition_data(item["name"])
        food_item = FoodItem(**item, **nutrition_data)
        foods_to_avoid.append(food_item)

    dietary_principles = [
        DietaryPrinciple(**item) for item in gemini_data.get("dietary_principles", [])
    ]

    return FoodRecommendationResponse(
        recommended_foods=recommended_foods,
        foods_to_avoid=foods_to_avoid,
        dietary_principles=dietary_principles,
    )
