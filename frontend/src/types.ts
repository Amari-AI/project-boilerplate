export interface ShipmentData {
  bill_of_lading_number?: string | null;
  container_number?: string | null;
  consignee_name?: string | null;
  consignee_address?: string | null;
  date?: string | null;
  line_items_count?: number | null;
  average_gross_weight?: string | null;
  average_price?: string | null;
}

export interface ProcessDocumentsResponse {
  status: string;
  shipment_data: ShipmentData;
  metadata: {
    total_files_processed: number;
    file_types: string[];
    pdf_file?: string;
    xlsx_file?: string;
    session_id: string;
  };
  document_ids: string[];
}