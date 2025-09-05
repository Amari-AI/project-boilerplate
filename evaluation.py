#!/usr/bin/env python3
"""
Evaluation script for document processing system.
Calculates accuracy, precision, recall, and F1 metrics.
"""

import json
import os
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import argparse


@dataclass
class EvaluationResult:
    """Data class to store evaluation metrics"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    confusion_matrix: Dict[str, int] = field(default_factory=lambda: {
        'true_positives': 0,
        'false_positives': 0,
        'true_negatives': 0,
        'false_negatives': 0
    })
    total_samples: int = 0
    field_level_accuracy: Dict[str, float] = field(default_factory=dict)


class DocumentEvaluator:
    """Evaluator for document processing accuracy"""
    
    def __init__(self):
        self.results = EvaluationResult()
    
    def normalize_value(self, value: Any) -> str:
        """Normalize values for comparison"""
        if value is None:
            return ""
        
        # Convert to string and clean up
        str_val = str(value).strip().lower()
        
        # Remove common formatting differences
        str_val = str_val.replace(',', '').replace('$', '').replace('%', '')
        str_val = ''.join(str_val.split())  # Remove all whitespace
        
        return str_val
    
    def compare_fields(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Tuple[int, int, Dict[str, bool]]:
        """
        Compare predicted fields with ground truth.
        Returns: (correct_fields, total_fields, field_results)
        """
        field_results = {}
        correct_fields = 0
        
        # Get all unique field names from both dictionaries
        all_fields = set(predicted.keys()) | set(ground_truth.keys())
        
        for field_name in all_fields:
            pred_val = self.normalize_value(predicted.get(field_name))
            true_val = self.normalize_value(ground_truth.get(field_name))
            
            is_correct = pred_val == true_val
            field_results[field_name] = is_correct
            
            if is_correct:
                correct_fields += 1
        
        return correct_fields, len(all_fields), field_results
    
    def evaluate_document(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single document"""
        correct_fields, total_fields, field_results = self.compare_fields(predicted, ground_truth)
        
        document_accuracy = correct_fields / total_fields if total_fields > 0 else 0.0
        
        return {
            'document_accuracy': document_accuracy,
            'correct_fields': correct_fields,
            'total_fields': total_fields,
            'field_results': field_results
        }
    
    def calculate_binary_metrics(self, field_results: List[Dict[str, bool]]) -> None:
        """Calculate binary classification metrics (treating each field as binary classification)"""
        tp = fp = tn = fn = 0
        
        for doc_fields in field_results:
            for field_name, is_correct in doc_fields.items():
                if is_correct:
                    tp += 1  # Correctly extracted field
                else:
                    fp += 1  # Incorrectly extracted field
        
        # For this evaluation, we consider TN = 0 since we're only looking at extracted fields
        # FN would be fields that should have been extracted but weren't (hard to measure without schema)
        
        self.results.confusion_matrix.update({
            'true_positives': tp,
            'false_positives': fp,
            'true_negatives': tn,
            'false_negatives': fn
        })
        
        # Calculate metrics
        if tp + fp > 0:
            self.results.precision = tp / (tp + fp)
        
        if tp + fn > 0:
            self.results.recall = tp / (tp + fn)
        
        if self.results.precision + self.results.recall > 0:
            self.results.f1_score = 2 * (self.results.precision * self.results.recall) / (self.results.precision + self.results.recall)
    
    def evaluate_dataset(self, predictions_file: str, ground_truth_file: str) -> EvaluationResult:
        """
        Evaluate predictions against ground truth data.
        
        Args:
            predictions_file: JSON file with predictions
            ground_truth_file: JSON file with ground truth data
            
        Returns:
            EvaluationResult object with all metrics
        """
        # Load data
        try:
            with open(predictions_file, 'r', encoding='utf-8') as f:
                predictions = json.load(f)
        except FileNotFoundError:
            print(f"Error: Predictions file '{predictions_file}' not found.")
            return self.results
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in predictions file: {e}")
            return self.results
        
        try:
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                ground_truth = json.load(f)
        except FileNotFoundError:
            print(f"Error: Ground truth file '{ground_truth_file}' not found.")
            return self.results
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in ground truth file: {e}")
            return self.results
        
        # Ensure both files have the same number of samples
        if len(predictions) != len(ground_truth):
            print(f"Warning: Number of predictions ({len(predictions)}) != ground truth samples ({len(ground_truth)})")
            min_samples = min(len(predictions), len(ground_truth))
            predictions = predictions[:min_samples]
            ground_truth = ground_truth[:min_samples]
        
        self.results.total_samples = len(predictions)
        
        document_accuracies = []
        all_field_results = []
        field_accuracy_totals = {}
        
        # Evaluate each document
        for i, (pred, truth) in enumerate(zip(predictions, ground_truth)):
            doc_result = self.evaluate_document(pred, truth)
            document_accuracies.append(doc_result['document_accuracy'])
            all_field_results.append(doc_result['field_results'])
            
            # Track field-level accuracy
            for field_name, is_correct in doc_result['field_results'].items():
                if field_name not in field_accuracy_totals:
                    field_accuracy_totals[field_name] = {'correct': 0, 'total': 0}
                
                field_accuracy_totals[field_name]['total'] += 1
                if is_correct:
                    field_accuracy_totals[field_name]['correct'] += 1
        
        # Calculate overall accuracy
        self.results.accuracy = sum(document_accuracies) / len(document_accuracies) if document_accuracies else 0.0
        
        # Calculate field-level accuracies
        for field_name, totals in field_accuracy_totals.items():
            self.results.field_level_accuracy[field_name] = totals['correct'] / totals['total']
        
        # Calculate binary classification metrics
        self.calculate_binary_metrics(all_field_results)
        
        return self.results
    
    def print_results(self) -> None:
        """Print evaluation results in a formatted way"""
        print("=" * 60)
        print("DOCUMENT PROCESSING EVALUATION RESULTS")
        print("=" * 60)
        print(f"Total Samples: {self.results.total_samples}")
        print()
        
        print("OVERALL METRICS:")
        print(f"  Accuracy:  {self.results.accuracy:.4f} ({self.results.accuracy*100:.2f}%)")
        print(f"  Precision: {self.results.precision:.4f} ({self.results.precision*100:.2f}%)")
        print(f"  Recall:    {self.results.recall:.4f} ({self.results.recall*100:.2f}%)")
        print(f"  F1 Score:  {self.results.f1_score:.4f} ({self.results.f1_score*100:.2f}%)")
        print()
        
        print("CONFUSION MATRIX:")
        cm = self.results.confusion_matrix
        print(f"  True Positives:  {cm['true_positives']}")
        print(f"  False Positives: {cm['false_positives']}")
        print(f"  True Negatives:  {cm['true_negatives']}")
        print(f"  False Negatives: {cm['false_negatives']}")
        print()
        
        if self.results.field_level_accuracy:
            print("FIELD-LEVEL ACCURACY:")
            for field_name, accuracy in sorted(self.results.field_level_accuracy.items()):
                print(f"  {field_name:20}: {accuracy:.4f} ({accuracy*100:.2f}%)")
            print()
    
    def save_results(self, output_file: str) -> None:
        """Save results to JSON file"""
        results_dict = {
            'overall_metrics': {
                'accuracy': self.results.accuracy,
                'precision': self.results.precision,
                'recall': self.results.recall,
                'f1_score': self.results.f1_score
            },
            'confusion_matrix': self.results.confusion_matrix,
            'total_samples': self.results.total_samples,
            'field_level_accuracy': self.results.field_level_accuracy
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {output_file}")


def create_sample_data():
    """Create sample prediction and ground truth files for demonstration"""
    
    # Sample predictions (what the system extracted)
    sample_predictions = [
        {
            "document_type": "invoice",
            "invoice_number": "INV-001",
            "date": "2024-01-15",
            "amount": "1500.00",
            "vendor": "ACME Corp"
        },
        {
            "document_type": "bill_of_lading",
            "bol_number": "BOL-12345",
            "shipper": "Global Shipping",
            "consignee": "ABC Company",
            "weight": "2500 lbs"
        },
        {
            "document_type": "invoice",
            "invoice_number": "INV-002",
            "date": "2024-01-16", 
            "amount": "750.50",
            "vendor": "XYZ Ltd"  # This will be wrong in ground truth
        }
    ]
    
    # Sample ground truth (correct values)
    sample_ground_truth = [
        {
            "document_type": "invoice",
            "invoice_number": "INV-001",
            "date": "2024-01-15",
            "amount": "1500.00",
            "vendor": "ACME Corp"
        },
        {
            "document_type": "bill_of_lading",
            "bol_number": "BOL-12345",
            "shipper": "Global Shipping",
            "consignee": "ABC Company",
            "weight": "2500 lbs"
        },
        {
            "document_type": "invoice",
            "invoice_number": "INV-002",
            "date": "2024-01-16",
            "amount": "750.50", 
            "vendor": "XYZ Limited"  # Correct vendor name
        }
    ]
    
    # Save sample files
    with open('sample_predictions.json', 'w') as f:
        json.dump(sample_predictions, f, indent=2)
    
    with open('sample_ground_truth.json', 'w') as f:
        json.dump(sample_ground_truth, f, indent=2)
    
    print("Created sample files:")
    print("  - sample_predictions.json")
    print("  - sample_ground_truth.json")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Evaluate document processing accuracy')
    parser.add_argument('--predictions', '-p', 
                       help='Path to predictions JSON file')
    parser.add_argument('--ground_truth', '-g', 
                       help='Path to ground truth JSON file')
    parser.add_argument('--output', '-o', 
                       help='Path to save results JSON file')
    parser.add_argument('--create_samples', action='store_true',
                       help='Create sample data files for demonstration')
    
    args = parser.parse_args()
    
    if args.create_samples:
        create_sample_data()
        return
    
    # Use default files if not specified
    predictions_file = args.predictions or 'sample_predictions.json'
    ground_truth_file = args.ground_truth or 'sample_ground_truth.json'
    output_file = args.output or 'evaluation_results.json'
    
    # Check if files exist, create samples if they don't
    if not os.path.exists(predictions_file) or not os.path.exists(ground_truth_file):
        print("Sample data files not found. Creating sample files...")
        create_sample_data()
        print()
    
    # Run evaluation
    evaluator = DocumentEvaluator()
    results = evaluator.evaluate_dataset(predictions_file, ground_truth_file)
    
    # Display results
    evaluator.print_results()
    
    # Save results
    evaluator.save_results(output_file)


if __name__ == '__main__':
    main()