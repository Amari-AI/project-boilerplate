from typing import Dict, Any, List, Optional
import difflib
from datetime import datetime
import re


class AccuracyCalculator:
    """Utility class for calculating accuracy of document processing results."""
    
    def __init__(self):
        self.field_weights = {
            'bill_of_lading_number': 1.0,
            'shipper_name': 0.8,
            'consignee_name': 0.8,
            'vessel_name': 0.6,
            'voyage_number': 0.6,
            'port_of_loading': 0.7,
            'port_of_discharge': 0.7,
            'date_of_shipment': 0.9,
            'cargo_description': 0.5,
            'container_numbers': 0.8,
        }
    
    def calculate_field_accuracy(self, extracted_value: Any, ground_truth_value: Any, field_name: str) -> float:
        """Calculate accuracy for a single field."""
        if extracted_value is None and ground_truth_value is None:
            return 1.0
        
        if extracted_value is None or ground_truth_value is None:
            return 0.0
        
        # Convert to strings for comparison
        extracted_str = str(extracted_value).strip().lower()
        ground_truth_str = str(ground_truth_value).strip().lower()
        
        if extracted_str == ground_truth_str:
            return 1.0
        
        # Special handling for different field types
        if field_name in ['bill_of_lading_number', 'voyage_number', 'container_numbers']:
            return self._calculate_alphanumeric_accuracy(extracted_str, ground_truth_str)
        
        elif field_name == 'date_of_shipment':
            return self._calculate_date_accuracy(extracted_str, ground_truth_str)
        
        elif field_name in ['shipper_name', 'consignee_name', 'vessel_name', 'port_of_loading', 'port_of_discharge']:
            return self._calculate_text_similarity(extracted_str, ground_truth_str)
        
        else:
            # Default text similarity
            return self._calculate_text_similarity(extracted_str, ground_truth_str)
    
    def _calculate_alphanumeric_accuracy(self, extracted: str, ground_truth: str) -> float:
        """Calculate accuracy for alphanumeric fields like BOL numbers."""
        # Remove common separators and spaces
        extracted_clean = re.sub(r'[^\w]', '', extracted)
        ground_truth_clean = re.sub(r'[^\w]', '', ground_truth)
        
        if extracted_clean == ground_truth_clean:
            return 1.0
        
        # Use sequence matching for partial accuracy
        matcher = difflib.SequenceMatcher(None, extracted_clean, ground_truth_clean)
        return matcher.ratio()
    
    def _calculate_date_accuracy(self, extracted: str, ground_truth: str) -> float:
        """Calculate accuracy for date fields."""
        # Try to parse dates and compare
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}[-/]\d{2}[-/]\d{4}',  # MM/DD/YYYY or MM-DD-YYYY
            r'\d{2}[-/]\d{2}[-/]\d{2}',  # MM/DD/YY or MM-DD-YY
        ]
        
        extracted_dates = []
        ground_truth_dates = []
        
        for pattern in date_patterns:
            extracted_dates.extend(re.findall(pattern, extracted))
            ground_truth_dates.extend(re.findall(pattern, ground_truth))
        
        if extracted_dates and ground_truth_dates:
            # If we found date patterns, compare the first ones
            return 1.0 if extracted_dates[0] == ground_truth_dates[0] else 0.7
        
        # Fall back to text similarity
        return self._calculate_text_similarity(extracted, ground_truth)
    
    def _calculate_text_similarity(self, extracted: str, ground_truth: str) -> float:
        """Calculate similarity between text fields using sequence matching."""
        matcher = difflib.SequenceMatcher(None, extracted, ground_truth)
        similarity = matcher.ratio()
        
        # Apply threshold - if similarity is very low, consider it completely wrong
        return similarity if similarity > 0.3 else 0.0
    
    def calculate_document_accuracy(self, extracted_data: Dict[str, Any], ground_truth_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall accuracy for a document."""
        field_accuracies = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        all_fields = set(extracted_data.keys()) | set(ground_truth_data.keys())
        
        for field in all_fields:
            extracted_value = extracted_data.get(field)
            ground_truth_value = ground_truth_data.get(field)
            
            field_accuracy = self.calculate_field_accuracy(extracted_value, ground_truth_value, field)
            field_accuracies[field] = field_accuracy
            
            # Apply weight
            weight = self.field_weights.get(field, 0.5)  # Default weight for unknown fields
            weighted_sum += field_accuracy * weight
            total_weight += weight
        
        overall_accuracy = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        return {
            'overall_accuracy': overall_accuracy,
            'field_accuracies': field_accuracies,
            'total_fields': len(all_fields),
            'perfect_matches': sum(1 for acc in field_accuracies.values() if acc == 1.0)
        }
    
    def calculate_batch_accuracy(self, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate accuracy metrics for a batch of documents."""
        if not results:
            return {'batch_accuracy': 0.0, 'field_breakdown': {}, 'total_documents': 0}
        
        total_accuracy = 0.0
        field_accuracies = {}
        
        for result in results:
            doc_accuracy = result['overall_accuracy']
            total_accuracy += doc_accuracy
            
            # Aggregate field accuracies
            for field, accuracy in result['field_accuracies'].items():
                if field not in field_accuracies:
                    field_accuracies[field] = []
                field_accuracies[field].append(accuracy)
        
        # Calculate averages
        batch_accuracy = total_accuracy / len(results)
        field_breakdown = {
            field: sum(accuracies) / len(accuracies) 
            for field, accuracies in field_accuracies.items()
        }
        
        return {
            'batch_accuracy': batch_accuracy,
            'field_breakdown': field_breakdown,
            'total_documents': len(results),
            'documents_with_perfect_score': sum(1 for r in results if r['overall_accuracy'] == 1.0)
        }
    
    def generate_accuracy_report(self, extracted_data: Dict[str, Any], ground_truth_data: Dict[str, Any]) -> str:
        """Generate a human-readable accuracy report."""
        accuracy_result = self.calculate_document_accuracy(extracted_data, ground_truth_data)
        
        report = f"Document Processing Accuracy Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"Overall Accuracy: {accuracy_result['overall_accuracy']:.2%}\n"
        report += f"Perfect Matches: {accuracy_result['perfect_matches']}/{accuracy_result['total_fields']}\n\n"
        
        report += "Field-by-field Breakdown:\n"
        for field, accuracy in accuracy_result['field_accuracies'].items():
            status = "✓" if accuracy == 1.0 else "✗" if accuracy == 0.0 else "~"
            report += f"  {status} {field}: {accuracy:.2%}\n"
        
        return report