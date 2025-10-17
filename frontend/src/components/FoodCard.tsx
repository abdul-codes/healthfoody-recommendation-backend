import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FoodItem } from "@/types";
import { cn } from "@/lib/utils";

interface FoodCardProps {
  food: FoodItem;
  variant: "recommended" | "avoid";
}

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
      <CardContent>
        <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-md border border-gray-200">
          {food.reason}
        </p>
      </CardContent>
    </Card>
  );
}
