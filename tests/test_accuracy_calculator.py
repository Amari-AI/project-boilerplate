import pytest
from app.utils.accuracy_calculator import AccuracyCalculator


class TestAccuracyCalculator:
    """Test cases for accuracy calculation functionality."""
    
    def test_field_accuracy_exact_match(self):
        """Test accuracy calculation for exact field matches."""
        calculator = AccuracyCalculator()
        
        # Exact matches should return 1.0
        assert calculator.calculate_field_accuracy("TEST123", "TEST123", "bill_of_lading_number") == 1.0
        assert calculator.calculate_field_accuracy("ACME Corp", "ACME Corp", "shipper_name") == 1.0
        
    def test_field_accuracy_case_insensitive(self):
        """Test that field accuracy is case insensitive."""
        calculator = AccuracyCalculator()
        
        assert calculator.calculate_field_accuracy("TEST123", "test123", "bill_of_lading_number") == 1.0
        assert calculator.calculate_field_accuracy("ACME Corp", "acme corp", "shipper_name") == 1.0
        
    def test_field_accuracy_whitespace_handling(self):
        """Test that field accuracy handles whitespace correctly."""
        calculator = AccuracyCalculator()
        
        assert calculator.calculate_field_accuracy(" TEST123 ", "TEST123", "bill_of_lading_number") == 1.0
        assert calculator.calculate_field_accuracy("ACME Corp\n", "ACME Corp", "shipper_name") == 1.0
    
    def test_field_accuracy_null_values(self):
        """Test field accuracy with null values."""
        calculator = AccuracyCalculator()
        
        # Both null should be perfect match
        assert calculator.calculate_field_accuracy(None, None, "bill_of_lading_number") == 1.0
        
        # One null should be zero accuracy
        assert calculator.calculate_field_accuracy("TEST123", None, "bill_of_lading_number") == 0.0
        assert calculator.calculate_field_accuracy(None, "TEST123", "bill_of_lading_number") == 0.0
    
    def test_alphanumeric_accuracy(self):
        """Test accuracy calculation for alphanumeric fields."""
        calculator = AccuracyCalculator()
        
        # Test bill of lading numbers with different formats
        accuracy = calculator.calculate_field_accuracy("BOL-123-456", "BOL123456", "bill_of_lading_number")
        assert accuracy == 1.0  # Should ignore separators
        
        # Partial matches should have partial accuracy
        accuracy = calculator.calculate_field_accuracy("BOL123456", "BOL123789", "bill_of_lading_number")
        assert 0.5 < accuracy < 1.0
        
    def test_date_accuracy(self):
        """Test accuracy calculation for date fields."""
        calculator = AccuracyCalculator()
        
        # Same date in same format
        assert calculator.calculate_field_accuracy("2024-01-15", "2024-01-15", "date_of_shipment") == 1.0
        
        # Same date in different formats should still match
        accuracy = calculator.calculate_field_accuracy("01/15/2024", "2024-01-15", "date_of_shipment")
        assert accuracy >= 0.7  # Should get partial credit for date matching
        
    def test_text_similarity(self):
        """Test text similarity calculation."""
        calculator = AccuracyCalculator()
        
        # Similar company names
        accuracy = calculator.calculate_field_accuracy("ACME Corporation", "ACME Corp", "shipper_name")
        assert 0.5 < accuracy < 1.0
        
        # Completely different text should have very low accuracy
        accuracy = calculator.calculate_field_accuracy("ACME Corp", "XYZ Industries", "shipper_name")
        assert accuracy < 0.3
    
    def test_document_accuracy_calculation(self):
        """Test overall document accuracy calculation."""
        calculator = AccuracyCalculator()
        
        extracted_data = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corporation",
            "consignee_name": "XYZ Company",
            "date_of_shipment": "2024-01-15"
        }
        
        ground_truth = {
            "bill_of_lading_number": "BOL123456",  # Perfect match
            "shipper_name": "ACME Corp",  # Similar
            "consignee_name": "XYZ Company",  # Perfect match
            "date_of_shipment": "2024-01-15"  # Perfect match
        }
        
        result = calculator.calculate_document_accuracy(extracted_data, ground_truth)
        
        assert "overall_accuracy" in result
        assert "field_accuracies" in result
        assert "total_fields" in result
        assert "perfect_matches" in result
        
        assert result["total_fields"] == 4
        assert result["perfect_matches"] == 3
        assert 0.8 < result["overall_accuracy"] < 1.0
        
    def test_document_accuracy_with_missing_fields(self):
        """Test document accuracy when fields are missing."""
        calculator = AccuracyCalculator()
        
        extracted_data = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corp"
        }
        
        ground_truth = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corp",
            "consignee_name": "XYZ Company"  # Missing from extracted
        }
        
        result = calculator.calculate_document_accuracy(extracted_data, ground_truth)
        
        assert result["total_fields"] == 3
        assert result["perfect_matches"] == 2
        # Should be penalized for missing field
        assert result["overall_accuracy"] < 1.0
    
    def test_batch_accuracy_calculation(self):
        """Test batch accuracy calculation."""
        calculator = AccuracyCalculator()
        
        # Create some mock document results
        doc_results = [
            {
                "overall_accuracy": 1.0,
                "field_accuracies": {
                    "bill_of_lading_number": 1.0,
                    "shipper_name": 1.0
                }
            },
            {
                "overall_accuracy": 0.8,
                "field_accuracies": {
                    "bill_of_lading_number": 1.0,
                    "shipper_name": 0.6
                }
            },
            {
                "overall_accuracy": 0.9,
                "field_accuracies": {
                    "bill_of_lading_number": 0.8,
                    "shipper_name": 1.0
                }
            }
        ]
        
        batch_result = calculator.calculate_batch_accuracy(doc_results)
        
        assert "batch_accuracy" in batch_result
        assert "field_breakdown" in batch_result
        assert "total_documents" in batch_result
        
        assert batch_result["total_documents"] == 3
        assert batch_result["batch_accuracy"] == pytest.approx(0.9, rel=0.01)
        assert "bill_of_lading_number" in batch_result["field_breakdown"]
        assert "shipper_name" in batch_result["field_breakdown"]
    
    def test_accuracy_report_generation(self):
        """Test accuracy report generation."""
        calculator = AccuracyCalculator()
        
        extracted_data = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corp"
        }
        
        ground_truth = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corporation"
        }
        
        report = calculator.generate_accuracy_report(extracted_data, ground_truth)
        
        assert "Document Processing Accuracy Report" in report
        assert "Overall Accuracy:" in report
        assert "Perfect Matches:" in report
        assert "Field-by-field Breakdown:" in report
        assert "bill_of_lading_number" in report
        assert "shipper_name" in report


@pytest.fixture
def sample_ground_truth_data():
    """Sample ground truth data for testing."""
    return {
        "bill_of_lading_number": "BOL-2024-001-ABC",
        "shipper_name": "Global Shipping Solutions Inc.",
        "consignee_name": "International Import Export Ltd.",
        "vessel_name": "MV Ocean Pioneer",
        "voyage_number": "VOY-2024-025",
        "port_of_loading": "Port of Los Angeles, CA",
        "port_of_discharge": "Port of Hamburg, Germany",
        "date_of_shipment": "2024-01-15",
        "cargo_description": "Electronic Components - Computers and Accessories",
        "container_numbers": ["CONU1234567", "CONU2345678"]
    }


class TestAccuracyEvaluationScenarios:
    """Test realistic accuracy evaluation scenarios."""
    
    def test_high_accuracy_scenario(self, sample_ground_truth_data):
        """Test scenario with high accuracy extraction."""
        calculator = AccuracyCalculator()
        
        # Simulate nearly perfect extraction
        extracted_data = {
            "bill_of_lading_number": "BOL-2024-001-ABC",
            "shipper_name": "Global Shipping Solutions Inc",  # Minor difference
            "consignee_name": "International Import Export Ltd.",
            "vessel_name": "MV Ocean Pioneer",
            "voyage_number": "VOY-2024-025",
            "port_of_loading": "Port of Los Angeles, CA",
            "port_of_discharge": "Port of Hamburg, Germany",
            "date_of_shipment": "2024-01-15",
            "cargo_description": "Electronic Components - Computers and Accessories",
            "container_numbers": ["CONU1234567", "CONU2345678"]
        }
        
        result = calculator.calculate_document_accuracy(extracted_data, sample_ground_truth_data)
        
        assert result["overall_accuracy"] > 0.95
        assert result["perfect_matches"] >= 8
    
    def test_medium_accuracy_scenario(self, sample_ground_truth_data):
        """Test scenario with medium accuracy extraction."""
        calculator = AccuracyCalculator()
        
        # Simulate extraction with some errors
        extracted_data = {
            "bill_of_lading_number": "BOL2024001ABC",  # Format difference
            "shipper_name": "Global Shipping Solutions",  # Missing "Inc."
            "consignee_name": "Intl Import Export Ltd",  # Abbreviated
            "vessel_name": "Ocean Pioneer",  # Missing "MV"
            "voyage_number": "VOY-2024-025",
            "port_of_loading": "Los Angeles",  # Partial
            "port_of_discharge": "Hamburg",  # Partial
            "date_of_shipment": "01/15/2024",  # Different format
            "cargo_description": "Electronics - Computer Accessories",  # Similar
            "container_numbers": ["CONU1234567"]  # Missing one container
        }
        
        result = calculator.calculate_document_accuracy(extracted_data, sample_ground_truth_data)
        
        assert 0.6 < result["overall_accuracy"] < 0.9
        assert result["perfect_matches"] < 5
    
    def test_low_accuracy_scenario(self, sample_ground_truth_data):
        """Test scenario with low accuracy extraction."""
        calculator = AccuracyCalculator()
        
        # Simulate extraction with significant errors
        extracted_data = {
            "bill_of_lading_number": "ABC123XYZ",  # Completely wrong
            "shipper_name": "Unknown Shipper",
            "consignee_name": "Unknown Consignee",
            "vessel_name": "MV Ocean Pioneer",  # One correct field
            "voyage_number": "VOY-2024-999",  # Wrong number
            "port_of_loading": "Unknown Port",
            "port_of_discharge": "Unknown Port",
            "date_of_shipment": "2024-12-31",  # Wrong date
            "cargo_description": "Unknown Cargo",
            "container_numbers": []  # Empty
        }
        
        result = calculator.calculate_document_accuracy(extracted_data, sample_ground_truth_data)
        
        assert result["overall_accuracy"] < 0.4
        assert result["perfect_matches"] <= 1