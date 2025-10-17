export type SearchType = "condition" | "goal" | "country";

export interface RecommendationRequest {
  search_type: SearchType;
  value: string;
  country?: string;
}

export interface FoodItem {
  name: string;
  reason: string;
}

export interface DietaryPrinciple {
  principle: string;
  explanation: string;
}

export interface FoodRecommendationResponse {
  recommended_foods: FoodItem[];
  foods_to_avoid: FoodItem[];
  dietary_principles: DietaryPrinciple[];
}
