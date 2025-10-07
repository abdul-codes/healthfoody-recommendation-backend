from pydantic import BaseModel
from typing import List, Optional


class HealthConditionRequest(BaseModel):
    condition: str


class FoodItem(BaseModel):
    name: str
    reason: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None


class DietaryPrinciple(BaseModel):
    principle: str
    explanation: str


class FoodRecommendationResponse(BaseModel):
    recommended_foods: List[FoodItem]
    foods_to_avoid: List[FoodItem]
    dietary_principles: List[DietaryPrinciple]
