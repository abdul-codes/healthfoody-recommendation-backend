import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import { SearchType } from "@/types";

interface SearchFormProps {
  onSubmit: (searchType: SearchType, value: string, country: string) => void;
  isLoading: boolean;
}

const SEARCH_PLACEHOLDERS: Record<SearchType, string> = {
  condition: "e.g., High Blood Pressure, Diabetes",
  goal: "e.g., Weight Loss, Build Muscle",
  country: "e.g., Nigeria, Japan, Brazil",
};

export function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const [searchType, setSearchType] = useState<SearchType>("condition");
  const [inputValue, setInputValue] = useState("");
  const [country, setCountry] = useState("");

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (inputValue.trim()) {
      onSubmit(searchType, inputValue.trim(), country.trim());
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end p-6 bg-white rounded-xl shadow-lg"
    >
      <div className="md:col-span-1">
        <label
          htmlFor="search-type"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Search Type
        </label>
        <Select
          value={searchType}
          onValueChange={(value) => setSearchType(value as SearchType)}
          disabled={isLoading}
        >
          <SelectTrigger
            id="search-type"
            className="w-full border-gray-300 rounded-lg"
          >
            <SelectValue placeholder="Select a type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="condition">Health Condition</SelectItem>
            <SelectItem value="goal">Health Goal</SelectItem>
            <SelectItem value="country">Foods by Country</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="md:col-span-2">
        <label
          htmlFor="search-value"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {searchType === "country"
            ? "Country Name"
            : searchType.charAt(0).toUpperCase() + searchType.slice(1)}
        </label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <Input
            id="search-value"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={SEARCH_PLACEHOLDERS[searchType]}
            className="pl-10 w-full border-gray-300 rounded-lg"
            disabled={isLoading}
            required
          />
        </div>
      </div>

      <div className="md:col-span-1">
        <label
          htmlFor="country-constraint"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Optional: Your Country
        </label>
        <Input
          id="country-constraint"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          placeholder="e.g., USA, India"
          className="w-full border-gray-300 rounded-lg"
          disabled={isLoading}
        />
      </div>

      <div className="md:col-span-4 flex justify-end">
        <Button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="w-full md:w-auto px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-transform transform hover:scale-105 disabled:opacity-60"
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Searching...</span>
            </div>
          ) : (
            "Get Recommendations"
          )}
        </Button>
      </div>
    </form>
  );
}
