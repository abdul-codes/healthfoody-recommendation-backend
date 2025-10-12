import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface SearchFormProps {
  onSubmit: (condition: string) => void;
  isLoading: boolean;
}

export function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const condition = formData.get("condition") as string;
    onSubmit(condition);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-4">
      <Input
        name="condition"
        placeholder="e.g., High Cholesterol, Diabetes"
        className="flex-grow"
        disabled={isLoading}
        required
      />
      <Button type="submit" disabled={isLoading}>
        {isLoading ? "Getting Recommendations..." : "Get Recommendations"}
      </Button>
    </form>
  );
}
