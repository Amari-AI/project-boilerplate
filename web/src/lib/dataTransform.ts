import { ExtractedData, DocumentFormData } from '@/types';

export function transformApiDataToFormData(apiData: ExtractedData): DocumentFormData {
  return {
    billOfLadingNumber: apiData.bill_of_lading_number || '',
    containerNumber: apiData.container_number || '',
    consigneeName: apiData.consignee_name || '',
    consigneeAddress: apiData.consignee || '', // Using consignee field as address
    date: apiData.date ? apiData.date.split('T')[0] : '', // Convert ISO date to YYYY-MM-DD
    lineItemsCount: apiData.line_items_count?.toString() || '',
    averageGrossWeight: apiData.average_gross_weight?.toString() || '',
    averagePrice: apiData.average_price?.toString() || '',
  };
}

export function transformFormDataToApiData(formData: DocumentFormData): ExtractedData {
  return {
    bill_of_lading_number: formData.billOfLadingNumber || null,
    container_number: formData.containerNumber || null,
    consignee_name: formData.consigneeName || null,
    consignee: formData.consigneeAddress || null,
    date: formData.date || null,
    line_items_count: formData.lineItemsCount ? parseInt(formData.lineItemsCount) : null,
    average_gross_weight: formData.averageGrossWeight ? parseFloat(formData.averageGrossWeight) : null,
    average_price: formData.averagePrice ? parseFloat(formData.averagePrice) : null,
  };
}

export function aggregateExtractedData(extractedDataArray: (ExtractedData | null)[]): DocumentFormData {
  // Filter out null values
  const validData = extractedDataArray.filter(data => data !== null) as ExtractedData[];
  
  if (validData.length === 0) {
    return {
      billOfLadingNumber: '',
      containerNumber: '',
      consigneeName: '',
      consigneeAddress: '',
      date: '',
      lineItemsCount: '',
      averageGrossWeight: '',
      averagePrice: '',
    };
  }

  // Use the first non-empty value for each field, or combine/calculate as needed
  const aggregated: DocumentFormData = {
    billOfLadingNumber: '',
    containerNumber: '',
    consigneeName: '',
    consigneeAddress: '',
    date: '',
    lineItemsCount: '',
    averageGrossWeight: '',
    averagePrice: '',
  };

  // Take first non-empty value for text fields
  for (const data of validData) {
    if (!aggregated.billOfLadingNumber && data.bill_of_lading_number) {
      aggregated.billOfLadingNumber = data.bill_of_lading_number;
    }
    if (!aggregated.containerNumber && data.container_number) {
      aggregated.containerNumber = data.container_number;
    }
    if (!aggregated.consigneeName && data.consignee_name) {
      aggregated.consigneeName = data.consignee_name;
    }
    if (!aggregated.consigneeAddress && data.consignee) {
      aggregated.consigneeAddress = data.consignee;
    }
    if (!aggregated.date && data.date) {
      aggregated.date = data.date.split('T')[0]; // Convert to YYYY-MM-DD
    }
  }

  // Calculate totals/averages for numeric fields
  let totalLineItems = 0;
  let totalWeight = 0;
  let totalPrice = 0;
  let countLineItems = 0;
  let countWeight = 0;
  let countPrice = 0;

  for (const data of validData) {
    if (data.line_items_count !== null && data.line_items_count !== undefined) {
      totalLineItems += data.line_items_count;
      countLineItems++;
    }
    if (data.average_gross_weight !== null && data.average_gross_weight !== undefined) {
      totalWeight += data.average_gross_weight;
      countWeight++;
    }
    if (data.average_price !== null && data.average_price !== undefined) {
      totalPrice += data.average_price;
      countPrice++;
    }
  }

  // Set aggregated numeric values
  if (countLineItems > 0) {
    aggregated.lineItemsCount = totalLineItems.toString();
  }
  if (countWeight > 0) {
    aggregated.averageGrossWeight = (totalWeight / countWeight).toFixed(2);
  }
  if (countPrice > 0) {
    aggregated.averagePrice = (totalPrice / countPrice).toFixed(2);
  }

  return aggregated;
}
