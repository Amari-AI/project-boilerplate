import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class DataValidator:
    """Validates data formats returned by the API."""
    
    @staticmethod
    def validate_date_format(date_str: Optional[str]) -> Dict[str, Any]:
        """Validate date format. Expected: YYYY-MM-DD or MM/DD/YYYY."""
        if date_str is None:
            return {"valid": False, "error": "Date is null"}
        
        valid_formats = [
            (r'^\d{4}-\d{2}-\d{2}$', '%Y-%m-%d', 'YYYY-MM-DD'),
            (r'^\d{2}/\d{2}/\d{4}$', '%m/%d/%Y', 'MM/DD/YYYY'),
            (r'^\d{2}-\d{2}-\d{4}$', '%m-%d-%Y', 'MM-DD-YYYY'),
        ]
        
        for pattern, date_format, format_name in valid_formats:
            if re.match(pattern, date_str):
                try:
                    datetime.strptime(date_str, date_format)
                    return {"valid": True, "format": format_name}
                except ValueError:
                    return {"valid": False, "error": f"Invalid date values in format {format_name}"}
        
        return {"valid": False, "error": f"Date format not recognized: {date_str}"}
    
    @staticmethod
    def validate_bill_of_lading(bol: Optional[str]) -> Dict[str, Any]:
        """Validate bill of lading format."""
        if bol is None:
            return {"valid": False, "error": "Bill of lading is null"}
        
        # Common B/L patterns: alphanumeric, may contain hyphens
        if re.match(r'^[A-Z0-9\-]{8,20}$', bol.upper()):
            return {"valid": True}
        
        return {"valid": False, "error": f"Invalid B/L format: {bol}. Expected alphanumeric with optional hyphens."}
    
    @staticmethod
    def validate_container_number(container: Optional[str]) -> Dict[str, Any]:
        """Validate container number format (ISO 6346)."""
        if container is None:
            return {"valid": False, "error": "Container number is null"}
        
        # ISO 6346: 4 letters + 7 digits (last digit is check digit)
        if re.match(r'^[A-Z]{4}\d{7}$', container.upper()):
            return {"valid": True, "format": "ISO 6346"}
        
        return {"valid": False, "error": f"Invalid container format: {container}. Expected: 4 letters + 7 digits (e.g., MSCU1234567)"}
    
    @staticmethod
    def validate_weight_format(weight: Optional[str]) -> Dict[str, Any]:
        """Validate weight format. Expected: number with unit (KG, LBS, etc.)."""
        if weight is None:
            return {"valid": False, "error": "Weight is null"}
        
        # Pattern: number (with optional decimal) followed by unit
        match = re.match(r'^([\d,]+\.?\d*)\s*(KG|LBS|LB|POUNDS|KILOGRAMS|KGS|MT|TON|TONS)?$', str(weight).upper())
        if match:
            number, unit = match.groups()
            try:
                float(number.replace(',', ''))
                return {"valid": True, "value": number, "unit": unit or "UNKNOWN"}
            except ValueError:
                return {"valid": False, "error": f"Invalid number in weight: {number}"}
        
        return {"valid": False, "error": f"Invalid weight format: {weight}. Expected: number with unit (e.g., 194.85 KG)"}
    
    @staticmethod
    def validate_price_format(price: Optional[str]) -> Dict[str, Any]:
        """Validate price format. Expected: currency symbol/code with amount."""
        if price is None:
            return {"valid": False, "error": "Price is null"}
        
        # Pattern: currency symbol/code with amount
        patterns = [
            (r'^\$?([\d,]+\.?\d*)\s*(USD|US\$|US)?$', 'USD'),
            (r'^€?([\d,]+\.?\d*)\s*(EUR|EURO)?$', 'EUR'),
            (r'^£?([\d,]+\.?\d*)\s*(GBP)?$', 'GBP'),
            (r'^([\d,]+\.?\d*)\s*(USD|EUR|GBP|CAD|AUD|CNY|JPY)$', 'CURRENCY_CODE'),
        ]
        
        price_upper = str(price).upper()
        for pattern, currency_type in patterns:
            match = re.match(pattern, price_upper)
            if match:
                amount = match.group(1)
                try:
                    float(amount.replace(',', ''))
                    return {"valid": True, "format": currency_type, "amount": amount}
                except ValueError:
                    return {"valid": False, "error": f"Invalid amount in price: {amount}"}
        
        return {"valid": False, "error": f"Invalid price format: {price}. Expected: currency with amount (e.g., $1289.51 USD)"}
    
    @staticmethod
    def validate_address_format(address: Optional[str]) -> Dict[str, Any]:
        """Validate address format."""
        if address is None:
            return {"valid": False, "error": "Address is null"}
        
        # Basic validation: should contain street, city, state/country, postal code
        address_upper = address.upper()
        
        # Check for minimum components
        has_numbers = bool(re.search(r'\d', address))
        has_street_keywords = any(keyword in address_upper for keyword in ['ST', 'STREET', 'AVE', 'AVENUE', 'RD', 'ROAD', 'BLVD', 'DRIVE', 'DR', 'LANE', 'LN'])
        has_postal_code = bool(re.search(r'\b\d{5}(-\d{4})?\b', address))  # US ZIP
        has_country_or_state = bool(re.search(r'\b[A-Z]{2}\b', address))  # State abbreviation or country code
        
        if len(address) < 20:
            return {"valid": False, "error": "Address too short"}
        
        components_found = sum([has_numbers, has_postal_code, has_country_or_state])
        if components_found >= 2:
            return {"valid": True, "components": {
                "has_numbers": has_numbers,
                "has_street_keywords": has_street_keywords,
                "has_postal_code": has_postal_code,
                "has_country_or_state": has_country_or_state
            }}
        
        return {"valid": False, "error": "Address missing key components (street number, postal code, or state/country)"}


class DocumentExtractionEvaluator:
    """Evaluates document extraction accuracy against ground truth data."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.validator = DataValidator()
        self.ground_truth = {
            "bill_of_lading_number": "ZMLU34110002",
            "container_number": "MSCU1234567",
            "consignee_name": "KABOFER TRADING INC",
            "consignee_address": "66-89 MAIN ST 6GH 643, FLUSHING, NY, 94089 US",
            "date": "2019-08-22",
            "line_items_count": 18,
            "average_gross_weight": "162.38 KG",
            "average_price": "$1289.51 USD"
        }
        
    def validate_api_response_format(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the format of data returned by the API."""
        validation_results = {}
        
        # Check if shipment_data exists
        if "shipment_data" not in response_data:
            return {"valid": False, "error": "Missing shipment_data in response"}
        
        shipment_data = response_data["shipment_data"]
        
        # Validate each field format
        validation_results["bill_of_lading_number"] = self.validator.validate_bill_of_lading(
            shipment_data.get("bill_of_lading_number")
        )
        
        validation_results["container_number"] = self.validator.validate_container_number(
            shipment_data.get("container_number")
        )
        
        validation_results["date"] = self.validator.validate_date_format(
            shipment_data.get("date")
        )
        
        validation_results["average_gross_weight"] = self.validator.validate_weight_format(
            shipment_data.get("average_gross_weight")
        )
        
        validation_results["average_price"] = self.validator.validate_price_format(
            shipment_data.get("average_price")
        )
        
        validation_results["consignee_address"] = self.validator.validate_address_format(
            shipment_data.get("consignee_address")
        )
        
        # Validate line_items_count (should be integer)
        line_items = shipment_data.get("line_items_count")
        if line_items is None:
            validation_results["line_items_count"] = {"valid": False, "error": "Line items count is null"}
        elif not isinstance(line_items, int):
            validation_results["line_items_count"] = {"valid": False, "error": f"Expected integer, got {type(line_items).__name__}"}
        elif line_items <= 0:
            validation_results["line_items_count"] = {"valid": False, "error": f"Invalid count: {line_items}"}
        else:
            validation_results["line_items_count"] = {"valid": True}
        
        # Validate consignee_name (basic string validation)
        consignee_name = shipment_data.get("consignee_name")
        if consignee_name is None:
            validation_results["consignee_name"] = {"valid": False, "error": "Consignee name is null"}
        elif len(str(consignee_name).strip()) < 3:
            validation_results["consignee_name"] = {"valid": False, "error": "Consignee name too short"}
        else:
            validation_results["consignee_name"] = {"valid": True}
        
        # Overall validation status
        all_valid = all(result.get("valid", False) for result in validation_results.values())
        
        return {
            "valid": all_valid,
            "field_validations": validation_results,
            "invalid_fields": [field for field, result in validation_results.items() if not result.get("valid", False)]
        }
    
    def normalize_string(self, value: Optional[str]) -> str:
        """Normalize string for comparison."""
        if value is None:
            return ""
        return " ".join(str(value).upper().strip().split())
    
    def normalize_number(self, value: Any) -> Optional[float]:
        """Extract numeric value from string."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r'[\d,]+\.?\d*', str(value).replace(',', ''))
        return float(match.group()) if match else None
    
    def fuzzy_match(self, expected: str, actual: str, threshold: float = 0.85) -> bool:
        """Perform fuzzy matching for strings."""
        expected = self.normalize_string(expected)
        actual = self.normalize_string(actual)
        
        if expected == actual:
            return True
            
        if not expected or not actual:
            return False
            
        expected_parts = expected.split()
        actual_text = actual
        
        matched_parts = sum(1 for part in expected_parts if part in actual_text)
        similarity = matched_parts / len(expected_parts)
        
        return similarity >= threshold
    
    def evaluate_field(self, field_name: str, expected: Any, actual: Any) -> Dict[str, Any]:
        """Evaluate a single field extraction."""
        result = {
            "field": field_name,
            "expected": expected,
            "actual": actual,
            "extracted": actual is not None,
            "correct": False,
            "partial_match": False,
            "error_type": None
        }
        
        if actual is None:
            result["error_type"] = "not_extracted"
            return result
        
        # Different evaluation logic based on field type
        if field_name in ["line_items_count"]:
            expected_num = self.normalize_number(expected)
            actual_num = self.normalize_number(actual)
            
            if expected_num and actual_num:
                result["correct"] = expected_num == actual_num
                if not result["correct"]:
                    tolerance = abs(expected_num - actual_num) / expected_num
                    result["partial_match"] = tolerance <= 0.1
                    result["error_type"] = "incorrect_value"
            else:
                result["error_type"] = "parse_error"
                
        elif field_name in ["average_gross_weight", "average_price"]:
            expected_num = self.normalize_number(expected)
            actual_num = self.normalize_number(actual)
            
            if expected_num and actual_num:
                tolerance = abs(expected_num - actual_num) / expected_num
                result["correct"] = tolerance <= 0.05
                result["partial_match"] = tolerance <= 0.1
                if not result["correct"]:
                    result["error_type"] = "incorrect_value"
            else:
                result["error_type"] = "parse_error"
                
        elif field_name == "date":
            try:
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                    try:
                        expected_date = datetime.strptime(expected, fmt).date()
                        break
                    except:
                        continue
                        
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                    try:
                        actual_date = datetime.strptime(actual, fmt).date()
                        break
                    except:
                        continue
                        
                result["correct"] = expected_date == actual_date
                if not result["correct"]:
                    result["error_type"] = "incorrect_value"
            except:
                result["correct"] = self.fuzzy_match(expected, actual)
                if not result["correct"]:
                    result["error_type"] = "parse_error"
                    
        else:
            result["correct"] = self.fuzzy_match(expected, actual, threshold=0.9)
            if not result["correct"]:
                result["partial_match"] = self.fuzzy_match(expected, actual, threshold=0.7)
                result["error_type"] = "incorrect_value"
        
        return result
    
    def calculate_metrics(self, field_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall metrics from field results."""
        total_fields = len(field_results)
        
        tp = sum(1 for r in field_results if r["correct"])
        fp = sum(1 for r in field_results if r["extracted"] and not r["correct"])
        fn = sum(1 for r in field_results if not r["extracted"])
        partial = sum(1 for r in field_results if r["partial_match"] and not r["correct"])
        
        accuracy = tp / total_fields if total_fields > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        extraction_rate = sum(1 for r in field_results if r["extracted"]) / total_fields
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "extraction_rate": extraction_rate,
            "correct_extractions": tp,
            "incorrect_extractions": fp,
            "missing_extractions": fn,
            "partial_matches": partial,
            "total_fields": total_fields
        }
    
    def test_document_extraction(self, pdf_path: str, xlsx_path: str) -> Dict[str, Any]:
        """Test the API with actual documents."""
        files = []
        
        if Path(pdf_path).exists():
            files.append(('files', (Path(pdf_path).name, open(pdf_path, 'rb'), 'application/pdf')))
        else:
            print(f"Warning: PDF file not found: {pdf_path}")
            
        if Path(xlsx_path).exists():
            files.append(('files', (Path(xlsx_path).name, open(xlsx_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')))
        else:
            print(f"Warning: Excel file not found: {xlsx_path}")
        
        if not files:
            return {"error": "No files found for testing"}
        
        try:
            response = requests.post(f"{self.api_url}/process-documents", files=files)
            
            for _, file_tuple in files:
                file_tuple[1].close()
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def evaluate(self, pdf_path: str = "BL-COSU534343282.pdf", 
                 xlsx_path: str = "Demo-Invoice-PackingList_1 (1).xlsx") -> Dict[str, Any]:
        """Run full evaluation."""
        print("="*60)
        print("Document Extraction Evaluation")
        print("="*60)
        
        # Test extraction
        print("\n1. Testing document extraction...")
        result = self.test_document_extraction(pdf_path, xlsx_path)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return result
        
        # Validate response format
        print("\n2. Validating API response format...")
        format_validation = self.validate_api_response_format(result)
        
        # Extract shipment data from result
        extracted_data = result.get("shipment_data", {})
        
        # Evaluate each field
        print("\n3. Evaluating extraction accuracy...")
        field_results = []
        
        for field_name, expected_value in self.ground_truth.items():
            actual_value = extracted_data.get(field_name)
            field_result = self.evaluate_field(field_name, expected_value, actual_value)
            field_results.append(field_result)
        
        # Calculate overall metrics
        metrics = self.calculate_metrics(field_results)
        
        # Prepare detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "documents": {
                "pdf": pdf_path,
                "xlsx": xlsx_path
            },
            "format_validation": format_validation,
            "ground_truth": self.ground_truth,
            "extracted_data": extracted_data,
            "field_evaluations": field_results,
            "overall_metrics": metrics,
            "summary": {
                "total_fields": metrics["total_fields"],
                "correctly_extracted": metrics["correct_extractions"],
                "incorrectly_extracted": metrics["incorrect_extractions"],
                "not_extracted": metrics["missing_extractions"],
                "partial_matches": metrics["partial_matches"],
                "format_valid": format_validation["valid"],
                "invalid_formats": format_validation.get("invalid_fields", [])
            }
        }
        
        # Print results
        self.print_results(report)
        
        # Save detailed report
        report_path = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")
        
        return report
    
    def print_results(self, report: Dict[str, Any]):
        """Print evaluation results in a readable format."""
        print("\n" + "="*60)
        print("DATA FORMAT VALIDATION")
        print("="*60)
        
        format_validation = report["format_validation"]
        if format_validation["valid"]:
            print("\n✓ All fields have valid formats")
        else:
            print(f"\n✗ {len(format_validation['invalid_fields'])} fields have invalid formats:")
            for field in format_validation["invalid_fields"]:
                field_validation = format_validation["field_validations"][field]
                print(f"  - {field}: {field_validation.get('error', 'Invalid format')}")
        
        # Detailed format validation
        print("\nField Format Details:")
        print("-"*60)
        for field, validation in format_validation["field_validations"].items():
            status = "✓" if validation["valid"] else "✗"
            print(f"{status} {field}: ", end="")
            if validation["valid"]:
                if "format" in validation:
                    print(f"Valid ({validation.get('format', 'OK')})")
                else:
                    print("Valid")
            else:
                print(f"{validation.get('error', 'Invalid')}")
        
        print("\n" + "="*60)
        print("EXTRACTION ACCURACY EVALUATION")
        print("="*60)
        
        # Field-by-field results
        print("\nField-by-Field Evaluation:")
        print("-"*60)
        
        for field_eval in report["field_evaluations"]:
            status = "✓" if field_eval["correct"] else "✗"
            partial = " (partial match)" if field_eval["partial_match"] and not field_eval["correct"] else ""
            
            print(f"\n{field_eval['field']}:")
            print(f"  Expected: {field_eval['expected']}")
            print(f"  Actual:   {field_eval['actual']}")
            print(f"  Status:   {status} {field_eval['error_type'] or 'correct'}{partial}")
        
        # Overall metrics
        metrics = report["overall_metrics"]
        print("\n" + "="*60)
        print("OVERALL METRICS")
        print("="*60)
        
        print(f"\nAccuracy:        {metrics['accuracy']:.2%}")
        print(f"Precision:       {metrics['precision']:.2%}")
        print(f"Recall:          {metrics['recall']:.2%}")
        print(f"F1 Score:        {metrics['f1_score']:.2%}")
        print(f"Extraction Rate: {metrics['extraction_rate']:.2%}")
        
        print(f"\nCorrect Extractions:   {metrics['correct_extractions']}/{metrics['total_fields']}")
        print(f"Incorrect Extractions: {metrics['incorrect_extractions']}/{metrics['total_fields']}")
        print(f"Missing Extractions:   {metrics['missing_extractions']}/{metrics['total_fields']}")
        print(f"Partial Matches:       {metrics['partial_matches']}")
        
        # Summary assessment
        print("\n" + "="*60)
        print("ROBUSTNESS ASSESSMENT")
        print("="*60)
        
        # Overall assessment based on both format validation and accuracy
        format_score = 1.0 if format_validation["valid"] else 0.8
        combined_score = metrics['f1_score'] * format_score
        
        if combined_score >= 0.9:
            assessment = "Excellent - System is highly robust with valid data formats"
        elif combined_score >= 0.8:
            assessment = "Good - System performs well with minor issues"
        elif combined_score >= 0.7:
            assessment = "Fair - System needs improvement"
        else:
            assessment = "Poor - System requires significant improvements"
            
        print(f"\n{assessment}")
        print(f"F1 Score: {metrics['f1_score']:.2%}")
        print(f"Format Validation: {'PASS' if format_validation['valid'] else 'FAIL'}")
        print(f"Combined Score: {combined_score:.2%}")


def evaluate_results(expected_data, actual_data):
    """
    Calculate accuracy metrics.
    Args:
    expected_data: Dictionary with expected values
    actual_data: Dictionary with actual values
    Returns:
    dict: Metrics
    """
    evaluator = DocumentExtractionEvaluator()
    
    # Evaluate each field
    field_results = []
    for field_name, expected_value in expected_data.items():
        actual_value = actual_data.get(field_name)
        field_result = evaluator.evaluate_field(field_name, expected_value, actual_value)
        field_results.append(field_result)
    
    # Calculate and return metrics
    return evaluator.calculate_metrics(field_results)


def main():
    """Main evaluation function."""
    # Check if API is running
    evaluator = DocumentExtractionEvaluator()
    
    # Check for custom API URL
    if len(sys.argv) > 1:
        evaluator.api_url = sys.argv[1]
    
    print(f"Using API URL: {evaluator.api_url}")
    
    # Check if API is accessible
    try:
        response = requests.get(f"{evaluator.api_url}/health")
        if response.status_code != 200:
            print(f"Warning: API health check failed with status {response.status_code}")
    except:
        print("Warning: Could not connect to API. Make sure the server is running.")
        print("Start the server with: python -m uvicorn app.main:app --reload")
        return
    
    # Run evaluation
    evaluator.evaluate()


if __name__ == "__main__":
    main()