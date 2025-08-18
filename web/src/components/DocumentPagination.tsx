import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DocumentPaginationProps {
  currentIndex: number;
  totalDocuments: number;
  onPrevious: () => void;
  onNext: () => void;
  disabled?: boolean;
}

export function DocumentPagination({
  currentIndex,
  totalDocuments,
  onPrevious,
  onNext,
  disabled = false,
}: DocumentPaginationProps) {
  if (totalDocuments <= 1) return null;

  const canGoPrevious = currentIndex > 0;
  const canGoNext = currentIndex < totalDocuments - 1;

  return (
    <div className="flex items-center gap-4">
      <Button
        variant="ghost"
        size="sm"
        onClick={onPrevious}
        disabled={!canGoPrevious || disabled}
      >
        <ChevronLeft className="h-4 w-4 mr-1" />
        Previous
      </Button>
      
      <span className="text-sm font-medium">
        {currentIndex + 1}/{totalDocuments}
      </span>
      
      <Button
        variant="ghost"
        size="sm"
        onClick={onNext}
        disabled={!canGoNext || disabled}
      >
        Next
        <ChevronRight className="h-4 w-4 ml-1" />
      </Button>
    </div>
  );
}