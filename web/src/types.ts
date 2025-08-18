// API Response types (matches backend model)
export interface ExtractedData {
  bill_of_lading_number?: string | null;
  container_number?: string | null;
  consignee_name?: string | null;
  consignee?: string | null;
  date?: string | null;
  line_items_count?: number | null;
  average_gross_weight?: number | null;
  average_price?: number | null;
}

// Form data types (for UI)
export interface DocumentFormData {
  billOfLadingNumber: string;
  containerNumber: string;
  consigneeName: string;
  consigneeAddress: string;
  date: string;
  lineItemsCount: string;
  averageGrossWeight: string;
  averagePrice: string;
}

export interface FileStats {
  size: number;
  lastModified: Date;
  type: string;
  fingerprint: string; // For deduplication (name + size + lastModified)
  pages?: number; // For PDFs
  sheets?: number; // For Excel files
  rows?: number; // For Excel files (total across all sheets)
}

export interface DocumentData {
  id: string;
  file: File;
  stats: FileStats;
  rawApiData: ExtractedData | null;
  documentUrl: string;
  isProcessed: boolean;
}

export interface DocumentProcessingState {
  documents: DocumentData[];
  currentIndex: number;
  isProcessing: boolean;
  aggregatedFormData: DocumentFormData | null;
}
