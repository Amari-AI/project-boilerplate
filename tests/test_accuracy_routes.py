import pytest
from unittest.mock import patch
import json


@pytest.mark.api
class TestAccuracyRoutes:
    """Tests for accuracy evaluation endpoints."""
    
    def test_evaluate_extraction_success(self, client):
        """Test successful accuracy evaluation."""
        extracted_data = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corp",
            "consignee_name": "XYZ Company"
        }
        
        ground_truth_data = {
            "bill_of_lading_number": "BOL123456",
            "shipper_name": "ACME Corporation",
            "consignee_name": "XYZ Company"
        }
        
        response = client.post(
            "/accuracy/evaluate",
            json={
                "extracted_data": extracted_data,
                "ground_truth_data": ground_truth_data
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_accuracy" in data
        assert "field_accuracies" in data
        assert "total_fields" in data
        assert "perfect_matches" in data
        
        assert data["total_fields"] == 3
        assert data["perfect_matches"] == 2  # BOL and consignee exact matches
        assert 0.8 < data["overall_accuracy"] < 1.0
    
    def test_batch_evaluate_success(self, client):
        """Test successful batch accuracy evaluation."""
        evaluations = [
            {
                "extracted_data": {
                    "bill_of_lading_number": "BOL123",
                    "shipper_name": "Company A"
                },
                "ground_truth_data": {
                    "bill_of_lading_number": "BOL123",
                    "shipper_name": "Company A"
                }
            },
            {
                "extracted_data": {
                    "bill_of_lading_number": "BOL456",
                    "shipper_name": "Company B Inc"
                },
                "ground_truth_data": {
                    "bill_of_lading_number": "BOL456",
                    "shipper_name": "Company B"
                }
            }
        ]
        
        response = client.post("/accuracy/batch-evaluate", json=evaluations)
        
        assert response.status_code == 200
        data = response.json()
        assert "batch_summary" in data
        assert "individual_results" in data
        
        batch_summary = data["batch_summary"]
        assert "batch_accuracy" in batch_summary
        assert "field_breakdown" in batch_summary
        assert "total_documents" in batch_summary
        
        assert batch_summary["total_documents"] == 2
        assert len(data["individual_results"]) == 2
    
    def test_batch_evaluate_missing_fields(self, client):
        """Test batch evaluation with missing required fields."""
        evaluations = [
            {
                "extracted_data": {"bill_of_lading_number": "BOL123"},
                # Missing ground_truth_data
            }
        ]
        
        response = client.post("/accuracy/batch-evaluate", json=evaluations)
        
        assert response.status_code == 400
        assert "must contain" in response.json()["detail"]
    
    def test_generate_accuracy_report_success(self, client, temp_storage_service):
        """Test successful accuracy report generation."""
        with patch('app.api.accuracy_routes.storage_service', temp_storage_service):
            # Save a test document
            doc_id = temp_storage_service.save_document(
                {"bill_of_lading_number": "BOL123", "shipper_name": "ACME Corp"},
                {"content": "test"},
                []
            )
            
            ground_truth_data = {
                "bill_of_lading_number": "BOL123",
                "shipper_name": "ACME Corporation"
            }
            
            response = client.get(
                f"/accuracy/report/{doc_id}",
                params={"ground_truth_data": json.dumps(ground_truth_data)}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "report" in data
            assert "Document Processing Accuracy Report" in data["report"]
    
    def test_generate_accuracy_report_document_not_found(self, client, temp_storage_service):
        """Test accuracy report generation with non-existent document."""
        with patch('app.api.accuracy_routes.storage_service', temp_storage_service):
            ground_truth_data = {
                "bill_of_lading_number": "BOL123"
            }
            
            response = client.get(
                "/accuracy/report/nonexistent-id",
                params={"ground_truth_data": json.dumps(ground_truth_data)}
            )
            
            assert response.status_code == 404
            assert "Document not found" in response.json()["detail"]
    
    def test_get_accuracy_metrics_success(self, client):
        """Test successful accuracy metrics retrieval."""
        response = client.get("/accuracy/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents_processed" in data
        assert "average_accuracy" in data
        assert "field_accuracy_breakdown" in data
        assert "accuracy_trend" in data
        
        # Check field breakdown structure
        field_breakdown = data["field_accuracy_breakdown"]
        assert "bill_of_lading_number" in field_breakdown
        assert "shipper_name" in field_breakdown
        
        # Check accuracy trend structure
        assert len(data["accuracy_trend"]) > 0
        for trend_point in data["accuracy_trend"]:
            assert "date" in trend_point
            assert "accuracy" in trend_point
    
    def test_evaluate_extraction_error_handling(self, client):
        """Test error handling in accuracy evaluation."""
        # Send invalid data that might cause calculation errors
        response = client.post(
            "/accuracy/evaluate",
            json={
                "extracted_data": {"invalid": "data"},
                "ground_truth_data": None  # This should cause an error
            }
        )
        
        assert response.status_code == 500
        assert "Error calculating accuracy" in response.json()["detail"]


@pytest.mark.integration
class TestAccuracyIntegration:
    """Integration tests for accuracy functionality."""
    
    def test_process_documents_with_accuracy(self, client, sample_pdf_file, mock_llm_service, temp_upload_dir):
        """Test document processing with accuracy calculation."""
        ground_truth = {
            "bill_of_lading_number": "TEST123",
            "shipper_name": "Test Shipper",
            "consignee_name": "Test Consignee"
        }
        
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.services.document_processor.process_documents') as mock_processor:
                mock_processor.return_value = {"pdf_test.pdf": "Test content"}
                
                # Create form data with ground truth
                files = [("files", ("test.pdf", open(sample_pdf_file, 'rb'), "application/pdf"))]
                data = {"ground_truth": json.dumps(ground_truth)}
                
                response = client.post(
                    "/process-documents",
                    files=files,
                    data=data
                )
                
                assert response.status_code == 200
                response_data = response.json()
                
                # Should include accuracy information
                assert "accuracy" in response_data
                assert "overall_accuracy" in response_data["accuracy"]
                assert "field_accuracies" in response_data["accuracy"]
    
    def test_end_to_end_accuracy_workflow(self, client, sample_pdf_file, mock_llm_service, temp_upload_dir, temp_storage_service):
        """Test complete accuracy evaluation workflow."""
        with patch('app.api.routes.UPLOADS_DIR', temp_upload_dir):
            with patch('app.api.routes.storage_service', temp_storage_service):
                with patch('app.api.accuracy_routes.storage_service', temp_storage_service):
                    with patch('app.services.document_processor.process_documents') as mock_processor:
                        mock_processor.return_value = {"pdf_test.pdf": "Test content"}
                        
                        # 1. Process document
                        files = [("files", ("test.pdf", open(sample_pdf_file, 'rb'), "application/pdf"))]
                        process_response = client.post("/process-documents", files=files)
                        assert process_response.status_code == 200
                        
                        # 2. Save document
                        save_response = client.post("/documents/save", json=process_response.json())
                        assert save_response.status_code == 200
                        doc_id = save_response.json()["document_id"]
                        
                        # 3. Evaluate accuracy
                        extracted_data = process_response.json()["extracted_data"]
                        ground_truth = {
                            "bill_of_lading_number": "TEST123",
                            "shipper_name": "Different Shipper"  # Intentional difference
                        }
                        
                        eval_response = client.post(
                            "/accuracy/evaluate",
                            json={
                                "extracted_data": extracted_data,
                                "ground_truth_data": ground_truth
                            }
                        )
                        
                        assert eval_response.status_code == 200
                        accuracy_data = eval_response.json()
                        
                        # 4. Generate report
                        report_response = client.get(
                            f"/accuracy/report/{doc_id}",
                            params={"ground_truth_data": json.dumps(ground_truth)}
                        )
                        
                        assert report_response.status_code == 200
                        assert "report" in report_response.json()
                        
                        # 5. Get metrics
                        metrics_response = client.get("/accuracy/metrics")
                        assert metrics_response.status_code == 200