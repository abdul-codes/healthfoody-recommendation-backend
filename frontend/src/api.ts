import axios from "axios";
import { FoodRecommendationResponse } from "./types";

const API_URL = "http://localhost:8000"; // The address of our Python backend

export async function getFoodRecommendations(
  condition: string,
): Promise<FoodRecommendationResponse> {
  const response = await axios.post<FoodRecommendationResponse>(
    `${API_URL}/recommendations`,
    { condition },
  );
  return response.data;
}
