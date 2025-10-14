import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { FoodItem } from "@/types";
import { cn } from "@/lib/utils";

interface FoodCardProps {
  food: FoodItem;
  variant: "recommended" | "avoid";
}

const formatNutrientValue = (
  value: number | null | undefined,
  unit: string = "",
): string => {
  if (value === null || value === undefined) {
    return "N/A";
  }
  // Show one decimal place only if it's not a whole number
  return `${parseFloat(value.toFixed(1))}${unit}`;
};

export function FoodCard({ food, variant }: FoodCardProps) {
  const cardClasses = cn(
    "h-full transition-shadow duration-200 hover:shadow-xl border-l-4",
    {
      "border-green-500": variant === "recommended",
      "border-red-500": variant === "avoid",
    },
  );

  return (
    <Card className={cardClasses}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold text-gray-800">
          {food.name}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md border border-gray-200">
          {food.reason}
        </p>

        <Separator />

        <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <NutrientRow
            label="Calories"
            value={formatNutrientValue(food.calories)}
          />
          <NutrientRow
            label="Protein"
            value={formatNutrientValue(food.protein, "g")}
          />
          <NutrientRow
            label="Carbs"
            value={formatNutrientValue(food.carbohydrates, "g")}
          />
          <NutrientRow label="Fat" value={formatNutrientValue(food.fat, "g")} />
          <NutrientRow
            label="Sugar"
            value={formatNutrientValue(food.sugar, "g")}
          />
          <NutrientRow
            label="Sodium"
            value={formatNutrientValue(food.sodium, "mg")}
          />
        </div>
      </CardContent>
    </Card>
  );
}

// Helper component for consistent nutrient display
const NutrientRow = ({ label, value }: { label: string; value: string }) => (
  <div className="flex justify-between">
    <span className="font-medium text-gray-600">{label}:</span>
    <span className="font-semibold text-gray-900">{value}</span>
  </div>
);
