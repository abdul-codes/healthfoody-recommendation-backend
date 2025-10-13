import { useState } from "react";
import { SearchForm } from "@/components/SearchForm";
import { getFoodRecommendations } from "./api";
import { FoodRecommendationResponse, SearchType } from "./types";
import { ResultsDisplay } from "./components/ResultsDisplay";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { AlertCircle, RefreshCw } from "lucide-react";

function App() {
  const [recommendations, setRecommendations] =
    useState<FoodRecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchedValue, setSearchedValue] = useState<string>("");

  const handleSearch = async (
    searchType: SearchType,
    value: string,
    country: string,
  ) => {
    setIsLoading(true);
    setError(null);
    setSearchedValue(value); // Store the primary search term
    try {
      const response = await getFoodRecommendations({
        search_type: searchType,
        value,
        country,
      });
      setRecommendations(response);
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      setError("Failed to fetch recommendations. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    // This is a simplified retry. A full implementation would store the entire last request.
    if (searchedValue) {
      // A default searchType is assumed for retry for simplicity.
      handleSearch("condition", searchedValue, "");
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <LoadingSpinner
          message={`Finding recommendations for ${searchedValue}...`}
        />
      );
    }

    if (error) {
      return (
        <div className="text-center p-8 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
          <h3 className="text-lg font-medium text-red-800 mb-2">
            Oops! Something went wrong
          </h3>
          <p className="text-red-600 mb-4">{error}</p>
          {searchedValue && (
            <button
              onClick={handleRetry}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>
          )}
        </div>
      );
    }

    if (recommendations) {
      return (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium">
              ✨ Here are your personalized recommendations for{" "}
              <span className="font-bold">{searchedValue}</span>
            </p>
          </div>
          <ResultsDisplay data={recommendations} />
        </div>
      );
    }

    return (
      <div className="text-center p-12 space-y-4">
        <div className="text-6xl mb-4">🥗</div>
        <h3 className="text-xl font-medium text-gray-700">
          Ready to get started?
        </h3>
        <p className="text-gray-500 max-w-md mx-auto">
          Enter your health condition above to receive personalized food
          recommendations powered by AI and backed by USDA nutritional data.
        </p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <main className="container mx-auto px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <header className="text-center mb-12">
            <div className="mb-4">
              <span className="text-5xl mb-4 block">🍎</span>
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-800 mb-4">
              Healthy Food <span className="text-green-600">Recommender</span>
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get AI-powered, personalized food recommendations tailored to your
              health conditions. Backed by scientific data from USDA FoodData
              Central.
            </p>
          </header>

          <section className="bg-white p-6 sm:p-8 rounded-xl shadow-lg border border-gray-100 mb-8">
            <SearchForm onSubmit={handleSearch} isLoading={isLoading} />
          </section>

          <section className="transition-all duration-300 ease-in-out">
            {renderContent()}
          </section>

          <footer className="text-center mt-12 pt-8 border-t border-gray-200">
            <p className="text-gray-500"></p>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
