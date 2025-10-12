from typing import TypedDict, Any


class NutrientData(TypedDict):
    """Type-safe structure for nutrition data from USDA API."""
    calories: float | None
    protein: float | None
    carbohydrates: float | None
    fat: float | None
    sugar: float | None
    sodium: float | None


class GeminiResponse(TypedDict):
    """Type-safe structure for Gemini API response."""
    recommended_foods: list[dict[str, str]]
    foods_to_avoid: list[dict[str, str]]
    dietary_principles: list[dict[str, str]]


class FoodItemDict(TypedDict):
    """Type-safe structure for individual food items from Gemini."""
    name: str
    reason: str
