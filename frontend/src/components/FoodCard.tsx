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

export function FoodCard({ food }: FoodCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{food.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-4">{food.reason}</p>
        <Separator />
        <div className="grid grid-cols-2 gap-2 mt-4 text-sm">
          <p>
            <strong>Calories:</strong> {food.calories?.toFixed(0) ?? "N/A"}
          </p>
          <p>
            <strong>Protein:</strong> {food.protein?.toFixed(1) ?? "N/A"}g
          </p>
          <p>
            <strong>Fat:</strong> {food.fat?.toFixed(1) ?? "N/A"}g
          </p>
          <p>
            <strong>Carbs:</strong> {food.carbohydrates?.toFixed(1) ?? "N/A"}g
          </p>
          <p>
            <strong>Sugar:</strong> {food.sugar?.toFixed(1) ?? "N/A"}g
          </p>
          <p>
            <strong>Sodium:</strong> {food.sodium?.toFixed(0) ?? "N/A"}mg
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
