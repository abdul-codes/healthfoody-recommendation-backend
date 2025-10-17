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
from app.config import GEMINI_API_KEY
from app.types import GeminiResponse
from async_lru import alru_cache

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


async def get_recommendations(
    request: RecommendationRequest,
) -> FoodRecommendationResponse:
    """
    Orchestrates the process of getting food recommendations asynchronously.
    """
    gemini_data = await get_gemini_recommendations(
        request.search_type, request.value, request.country
    )

    # Process recommended foods
    recommended_foods: list[FoodItem] = []
    for item in gemini_data.get("recommended_foods", []):
        if isinstance(item, dict) and "name" in item and "reason" in item:
            food_item = FoodItem(
                name=item["name"],
                reason=item["reason"],
            )
            recommended_foods.append(food_item)

    # Process foods to avoid
    foods_to_avoid: list[FoodItem] = []
    for item in gemini_data.get("foods_to_avoid", []):
        if isinstance(item, dict) and "name" in item and "reason" in item:
            food_item = FoodItem(
                name=item["name"],
                reason=item["reason"],
            )
            foods_to_avoid.append(food_item)

    # Process dietary principles
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
