import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, ChevronDown } from "lucide-react";

interface SearchFormProps {
  onSubmit: (condition: string) => void;
  isLoading: boolean;
}

const HEALTH_CONDITIONS = [
  "High Blood Pressure",
  "Diabetes Type 2", 
  "High Cholesterol",
  "Heart Disease",
  "Obesity",
  "Acid Reflux",
  "Kidney Disease",
  "Arthritis",
  "Osteoporosis",
  "Anemia",
  "Thyroid Issues",
  "Celiac Disease",
  "Lactose Intolerance",
  "IBS (Irritable Bowel Syndrome)",
  "PCOS",
  "Pregnancy",
  "Menopause",
  "Fatty Liver",
  "Gout",
  "Depression"
];

export function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const [inputValue, setInputValue] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (inputValue.trim().length > 0) {
      const filtered = HEALTH_CONDITIONS.filter(condition =>
        condition.toLowerCase().includes(inputValue.toLowerCase())
      );
      setFilteredSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setShowSuggestions(false);
      setFilteredSuggestions([]);
    }
  }, [inputValue]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (inputValue.trim()) {
      onSubmit(inputValue.trim());
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    setShowSuggestions(false);
    onSubmit(suggestion);
  };

  const handleInputFocus = () => {
    if (inputValue.trim().length > 0 && filteredSuggestions.length > 0) {
      setShowSuggestions(true);
    }
  };

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="relative flex-grow">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onFocus={handleInputFocus}
              placeholder="Search health conditions (e.g., High Blood Pressure, Diabetes)"
              className="pl-10 pr-4 py-3 text-base border-2 border-gray-200 focus:border-green-500 focus:ring-green-500 rounded-lg transition-all duration-200"
              disabled={isLoading}
              required
            />
            {inputValue && (
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            )}
          </div>
          
          {showSuggestions && filteredSuggestions.length > 0 && (
            <div 
              ref={suggestionsRef}
              className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto"
            >
              {filteredSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 hover:bg-green-50 hover:text-green-700 border-b border-gray-100 last:border-b-0 transition-colors duration-150"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
        
        <Button 
          type="submit" 
          disabled={isLoading || !inputValue.trim()}
          className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed min-w-[140px]"
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Searching...
            </div>
          ) : (
            "Get Recommendations"
          )}
        </Button>
      </form>
    </div>
  );
}
