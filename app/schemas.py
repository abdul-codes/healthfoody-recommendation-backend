from typing import TypedDict, Any


class NutrientData(TypedDict):
    calories: float | None
    protein: float | None
    carbohydrates: float | None
    fat: float | None
    sugar: float | None
    sodium: float | None


class GeminiResponse(TypedDict):
    recommended_foods: list[dict[str, str]]
    foods_to_avoid: list[dict[str, str]]
    dietary_principles: list[dict[str, str]]


class FoodItemDict(TypedDict):
    name: str
    reason: str
