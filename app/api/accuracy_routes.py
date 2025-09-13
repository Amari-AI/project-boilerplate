from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.utils.accuracy_calculator import AccuracyCalculator
from app.services.storage_service import storage_service
import json
import logging

router = APIRouter(prefix="/accuracy", tags=["accuracy"])

# Set up logging for accuracy tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/evaluate")
async def evaluate_extraction(
    extracted_data: Dict[str, Any],
    ground_truth_data: Dict[str, Any]
):
    """Evaluate the accuracy of extracted data against ground truth."""
    try:
        accuracy_calculator = AccuracyCalculator()
        accuracy_result = accuracy_calculator.calculate_document_accuracy(
            extracted_data, ground_truth_data
        )
        
        # Log the accuracy evaluation
        logger.info(f"Accuracy evaluation completed: {accuracy_result['overall_accuracy']:.2%}")
        
        return accuracy_result
        
    except Exception as e:
        logger.error(f"Error during accuracy evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating accuracy: {str(e)}")

@router.post("/batch-evaluate")
async def batch_evaluate_extractions(
    evaluations: List[Dict[str, Any]]
):
    """Evaluate accuracy for a batch of extracted data."""
    try:
        accuracy_calculator = AccuracyCalculator()
        results = []
        
        for evaluation in evaluations:
            if "extracted_data" not in evaluation or "ground_truth_data" not in evaluation:
                raise HTTPException(
                    status_code=400, 
                    detail="Each evaluation must contain 'extracted_data' and 'ground_truth_data'"
                )
            
            result = accuracy_calculator.calculate_document_accuracy(
                evaluation["extracted_data"],
                evaluation["ground_truth_data"]
            )
            results.append(result)
        
        batch_accuracy = accuracy_calculator.calculate_batch_accuracy(results)
        
        # Log batch evaluation results
        logger.info(f"Batch accuracy evaluation completed for {len(evaluations)} documents: {batch_accuracy['batch_accuracy']:.2%}")
        
        return {
            "batch_summary": batch_accuracy,
            "individual_results": results
        }
        
    except Exception as e:
        logger.error(f"Error during batch accuracy evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating batch accuracy: {str(e)}")

@router.get("/report/{doc_id}")
async def generate_accuracy_report(doc_id: str, ground_truth_data: Dict[str, Any]):
    """Generate a detailed accuracy report for a specific document."""
    try:
        document_data = storage_service.get_document(doc_id)
        if not document_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        accuracy_calculator = AccuracyCalculator()
        report = accuracy_calculator.generate_accuracy_report(
            document_data["extracted_data"],
            ground_truth_data
        )
        
        logger.info(f"Accuracy report generated for document {doc_id}")
        
        return {"report": report}
        
    except Exception as e:
        logger.error(f"Error generating accuracy report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/metrics")
async def get_accuracy_metrics():
    """Get overall accuracy metrics from processed documents."""
    try:
        # This would typically query a metrics database or log files
        # For now, we'll return placeholder metrics
        return {
            "total_documents_processed": len(storage_service.data["documents"]),
            "average_accuracy": 0.85,  # Placeholder - would be calculated from actual data
            "field_accuracy_breakdown": {
                "bill_of_lading_number": 0.92,
                "shipper_name": 0.78,
                "consignee_name": 0.81,
                "date_of_shipment": 0.88,
                "cargo_description": 0.65
            },
            "accuracy_trend": [
                {"date": "2024-01-01", "accuracy": 0.82},
                {"date": "2024-01-02", "accuracy": 0.85},
                {"date": "2024-01-03", "accuracy": 0.87}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving accuracy metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")