import { FoodRecommendationResponse } from "@/types";
import { FoodCard } from "./FoodCard";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { ThumbsUp, ClipboardList, Ban } from "lucide-react";

interface ResultsDisplayProps {
  data: FoodRecommendationResponse;
}

export function ResultsDisplay({ data }: ResultsDisplayProps) {
  return (
    <div className="space-y-8">
      {/* Recommended Foods */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-green-100 p-2 rounded-full">
            <ThumbsUp className="h-6 w-6 text-green-700" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">
            Recommended Foods
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.recommended_foods.map((food) => (
            <FoodCard key={food.name} food={food} variant="recommended" />
          ))}
        </div>
      </section>

      {/* Dietary Principles */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-blue-100 p-2 rounded-full">
            <ClipboardList className="h-6 w-6 text-blue-700" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">
            Dietary Principles
          </h2>
        </div>
        <Accordion type="single" collapsible className="w-full">
          {data.dietary_principles.map((principle, index) => (
            <AccordionItem
              key={index}
              value={`item-${index}`}
              className="bg-white border border-gray-200 rounded-lg mb-2 px-4"
            >
              <AccordionTrigger className="text-lg font-medium text-gray-700 hover:no-underline">
                {principle.principle}
              </AccordionTrigger>
              <AccordionContent className="text-base text-gray-600 pt-2 pb-4">
                {principle.explanation}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </section>

      {/* Foods to Avoid */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-red-100 p-2 rounded-full">
            <Ban className="h-6 w-6 text-red-700" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Foods to Avoid</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.foods_to_avoid.map((food) => (
            <FoodCard key={food.name} food={food} variant="avoid" />
          ))}
        </div>
      </section>
    </div>
  );
}
