import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { FoodItem } from "@/types";

interface FoodCardProps {
  food: FoodItem;
}

const formatNutrientValue = (value: number | null, unit: string = ""): string => {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return `${value.toFixed(1)}${unit}`;
};

const formatCalories = (value: number | null): string => {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return Math.round(value).toString();
};

export function FoodCard({ food }: FoodCardProps) {
  return (
    <Card className="h-full hover:shadow-lg transition-shadow duration-200 border-l-4 border-l-emerald-500">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-gray-800 line-clamp-2">
          {food.name}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-md">
          {food.reason}
        </p>
        
        <Separator />
        
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Calories:</span>
              <span className="text-gray-900">{formatCalories(food.calories)}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Protein:</span>
              <span className="text-gray-900">{formatNutrientValue(food.protein, "g")}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Fat:</span>
              <span className="text-gray-900">{formatNutrientValue(food.fat, "g")}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Carbs:</span>
              <span className="text-gray-900">{formatNutrientValue(food.carbohydrates, "g")}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Sugar:</span>
              <span className="text-gray-900">{formatNutrientValue(food.sugar, "g")}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-gray-700">Sodium:</span>
              <span className="text-gray-900">{formatNutrientValue(food.sodium, "mg")}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
