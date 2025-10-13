import axios from "axios";
import { FoodRecommendationResponse, RecommendationRequest } from "./types";

const API_URL = "http://localhost:8000"; // The address of our Python backend

export async function getFoodRecommendations(
  request: RecommendationRequest,
): Promise<FoodRecommendationResponse> {
  const response = await axios.post<FoodRecommendationResponse>(
    `${API_URL}/recommendations`,
    request,
  );
  return response.data;
}
