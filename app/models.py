from pydantic import BaseModel
from enum import Enum
from typing import Optional


class SearchType(str, Enum):
    CONDITION = "condition"
    GOAL = "goal"
    COUNTRY = "country"


class RecommendationRequest(BaseModel):
    search_type: SearchType
    value: str
    country: Optional[str] = None


class FoodItem(BaseModel):
    name: str
    reason: str
    calories: float | None = None
    protein: float | None = None
    carbohydrates: float | None = None
    fat: float | None = None
    sugar: float | None = None
    sodium: float | None = None


class DietaryPrinciple(BaseModel):
    principle: str
    explanation: str


class FoodRecommendationResponse(BaseModel):
    recommended_foods: list[FoodItem]
    foods_to_avoid: list[FoodItem]
    dietary_principles: list[DietaryPrinciple]
