import { FoodRecommendationResponse } from "@/types";
import { FoodCard } from "./FoodCard";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Separator } from "./ui/separator";

interface ResultsDisplayProps {
  data: FoodRecommendationResponse;
}

export function ResultsDisplay({ data }: ResultsDisplayProps) {
  return (
    <div className="mt-8 space-y-8">
      {/* Recommended Foods */}
      <div>
        <h2 className="text-2xl font-bold text-green-600">Recommended Foods</h2>
        <Separator className="my-4" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.recommended_foods.map((food) => (
            <FoodCard key={food.name} food={food} />
          ))}
        </div>
      </div>

      {/* Foods to Avoid */}
      <div>
        <h2 className="text-2xl font-bold text-red-600">Foods to Avoid</h2>
        <Separator className="my-4" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.foods_to_avoid.map((food) => (
            <FoodCard key={food.name} food={food} />
          ))}
        </div>
      </div>

      {/* Dietary Principles */}
      <div>
        <h2 className="text-2xl font-bold text-blue-600">Dietary Principles</h2>
        <Separator className="my-4" />
        <Accordion type="single" collapsible className="w-full">
          {data.dietary_principles.map((principle, index) => (
            <AccordionItem value={`item-${index}`} key={principle.principle}>
              <AccordionTrigger>{principle.principle}</AccordionTrigger>
              <AccordionContent>{principle.explanation}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  );
}
