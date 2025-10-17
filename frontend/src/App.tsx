import { useState } from "react";
import axios from "axios";
import { SearchForm } from "@/components/SearchForm";
import { getFoodRecommendations } from "./api";
import { FoodRecommendationResponse, SearchType } from "./types";
import { ResultsDisplay } from "./components/ResultsDisplay";
import { LoadingSpinner } from "./components/LoadingSpinner";
import { AlertCircle, RefreshCw, Leaf, Sparkles } from "lucide-react";

function App() {
  const [recommendations, setRecommendations] =
    useState<FoodRecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchedValue, setSearchedValue] = useState<string>("");

  const [lastRequest, setLastRequest] = useState<{
    searchType: SearchType;
    value: string;
    country: string;
  } | null>(null);

  const handleSearch = async (
    searchType: SearchType,
    value: string,
    country: string,
  ) => {
    setIsLoading(true);
    setError(null);
    setSearchedValue(value);
    setLastRequest({ searchType, value, country });

    try {
      const response = await getFoodRecommendations({
        search_type: searchType,
        value,
        country,
      });
      setRecommendations(response);
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
      let errorMessage = "An unexpected error occurred. Please try again.";
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        errorMessage = `An error occurred: ${err.response.data.detail}`;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (lastRequest) {
      handleSearch(
        lastRequest.searchType,
        lastRequest.value,
        lastRequest.country,
      );
    }
  };

  const handleReload = () => {
    window.location.reload();
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
          <div className="flex justify-center gap-4">
            <button
              onClick={handleRetry}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Try Again
            </button>
            <button
              onClick={handleReload}
              className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    if (recommendations) {
      return (
        <div className="space-y-8">
          <div className="flex items-start gap-3 p-4 bg-green-50 border-l-4 border-green-500 rounded-r-lg">
            <Sparkles className="w-5 h-5 text-green-700 mt-0.5 flex-shrink-0" />
            <p className="font-medium text-green-900">
              Here are your personalized recommendations for{" "}
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
          recommendations powered by AI.
        </p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <header className="text-center mb-10">
            <div className="inline-block p-3 bg-green-100 rounded-full mb-4">
              <Leaf className="w-10 h-10 text-green-700" />
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-3">
              Eat Right, Live Well
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              AI-powered food recommendations tailored to your health needs.
            </p>
          </header>

          <section className="bg-white p-6 sm:p-8 rounded-xl border border-gray-200 mb-8">
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
