from app.services import document_processor as dp
from app.services.llm_service import extract_fields_from_document
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
import math

# Define the ground truth data for comparison
ground_truth_data = {
    'Bill of lading number': '3411000',
    'Container Number': 'MSCU1234567',
    'Consignee Name': 'JOHN ALABAMA',
    'Consignee Address': '183 ZHONG YUAN WEST ROAD',
    'Line Items Count': 11,  # Expected number of items
    'Average Gross Weight': 267.525,  # Expected total weight
    'Average Price': 16131.64,  # Expected total price
}

# Tolerance for numeric comparison (for cases like price or weight discrepancies)
TOLERANCE = 0.05  # Allow 5% error for numeric fields

def evaluate_performance(extracted_data, ground_truth_data):
    """
    Evaluate the performance of the document processing system.
    
    Args:
    extracted_data (dict): Predicted values from the document processing system.
    ground_truth_data (dict): Actual expected values (ground truth).
    
    Returns:
    dict: Dictionary containing the accuracy, precision, recall, and F1 score.
    """
    # Initialize lists to hold true and predicted labels
    true_labels = []
    predicted_labels = []

    # Iterate through each field in the ground truth data and compare with the extracted data
    for field in ground_truth_data:
        # Get ground truth and extracted values
        true_value = ground_truth_data.get(field)
        extracted_value = extracted_data.get(field)
        
        if true_value is None:
            continue  # Skip the field if it's not in the ground truth
        
        if extracted_value is None or extracted_value == 'Not found':
            # If extracted value is 'Not found', treat it as a mismatch
            true_labels.append(1 if true_value == extracted_value else 0)
            predicted_labels.append(0)
            continue
        
        # Numeric fields (e.g., weight, price) allow some tolerance for comparison
        if isinstance(true_value, (int, float)) and isinstance(extracted_value, (int, float)):
            if math.isclose(true_value, extracted_value, abs_tol=TOLERANCE):
                true_labels.append(1)
                predicted_labels.append(1)
            else:
                true_labels.append(1)
                predicted_labels.append(0)
        elif isinstance(true_value, str) and isinstance(extracted_value, str):
            # For string fields, perform case-insensitive comparison
            if true_value.strip().lower() == extracted_value.strip().lower():
                true_labels.append(1)
                predicted_labels.append(1)
            else:
                true_labels.append(1)
                predicted_labels.append(0)
    
    # Calculate the evaluation metrics
    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels, zero_division=0)
    recall = recall_score(true_labels, predicted_labels, zero_division=0)
    f1 = f1_score(true_labels, predicted_labels, zero_division=0)
    
    # Return the metrics as a dictionary
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

def extract_data_from_documents(file_paths):
    """
    Extract fields from the provided document paths using the document processing system.
    
    Args:
    file_paths (list): List of file paths to the documents.
    
    Returns:
    dict: Extracted fields from the documents.
    """
    # Step 1: Process the documents to extract text data
    textDataResp = dp.process_documents(file_paths)
    
    # Step 2: Define the fields you want to extract
    fields = [
        'Bill of lading number',
        'Container Number',
        'Consignee Name',
        'Consignee Address',
        'Line Items Count',
        'Weight',
        'Price',
    ]
    
    # Step 3: Extract the fields from the processed documents
    fieldsJSON = extract_fields_from_document(textDataResp, fields)
    
    return fieldsJSON

# Example of how to use the flow

# List of documents you want to process (you can change this to point to your actual files)
file_paths = ['documents/InvoicePackingList.xlsx']

# Step 1: Extract data from the documents
extracted_data = extract_data_from_documents(file_paths)

# Step 2: Evaluate the performance by comparing the extracted data with the ground truth
metrics = evaluate_performance(extracted_data, ground_truth_data)

# Step 3: Print out the evaluation metrics
print(json.dumps(metrics, indent=4))
