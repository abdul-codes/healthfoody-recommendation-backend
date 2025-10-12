import { useState } from "react";
import { SearchForm } from "@/components/SearchForm";
import { getFoodRecommendations } from "./api";
import { FoodRecommendationResponse } from "./types";
import { ResultsDisplay } from "./components/ResultsDisplay";

function App() {
  const [recommendations, setRecommendations] =
    useState<FoodRecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (condition: string) => {
    setIsLoading(true);
    setError(null);
    setRecommendations(null);
    try {
      const data = await getFoodRecommendations(condition);
      setRecommendations(data);
    } catch (err) {
      setError("Failed to fetch recommendations. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center p-8">Loading...</div>;
    }

    if (error) {
      return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    if (recommendations) {
      return <ResultsDisplay data={recommendations} />;
    }

    return (
      <div className="text-center p-8 text-gray-500">
        <p>Enter a health condition above to get started.</p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <div className="max-w-3xl mx-auto">
          <header className="text-center my-8">
            <h1 className="text-4xl font-bold text-green-700">
              Healthy Food Recommender
            </h1>
            <p className="text-lg text-gray-600 mt-2">
              Get AI-powered food recommendations for your health conditions.
            </p>
          </header>

          <section className="bg-white p-6 rounded-lg shadow-md">
            <SearchForm onSubmit={handleSearch} isLoading={isLoading} />
          </section>

          <section className="mt-8">{renderContent()}</section>

          <footer className="text-center mt-8 text-gray-500">
            <p>Powered by Gemini & USDA FoodData Central</p>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
