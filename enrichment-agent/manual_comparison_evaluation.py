import json
from dotenv import load_dotenv
import os
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
import pandas as pd
import numpy as np
import argparse
import importlib

# Load environment variables from .env file before other imports
load_dotenv()

def get_agent_and_config(full_aspects: bool):
    if full_aspects:
        agent_module = importlib.import_module('agentmistral')
        manual_annotations_file = 'manual_annotations_complex.json'
        aspects = [
            'code generation', 'API documentation', 'environmental impact', 'bias', 'security', 
            'code interpreter', 'benchmarks', 'nuance understanding', 'cost', 'data extraction', 
            'closed-source', 'math ability', 'tone flexibility', 'safety', 'availability', 'hype', 
            'multimodality', 'hardware requirements', 'performance', 'speed', 'image generation', 
            'ethics', 'regulation', 'safety filters', 'interpretability', 'API rate limits', 
            'role-playing', 'data generation', 'fine-tuning', 'knowledge cutoff', 'context window', 
            'multilingual support', 'coherence', 'humor understanding', 'pricing model', 
            'customization', 'privacy', 'creativity', 'factual accuracy', 'open-source', 'community', 
            'hallucination', 'coding_ability', 'job displacement', 'ease of use', 'reasoning', 
            'productivity', 'summarization', 'response quality', 'voice feature'
        ]
        aspect_mapping = {
            'code generation': 'code_generation',
            'API documentation': 'api_documentation',
            'environmental impact': 'environmental_impact',
            'bias': 'bias',
            'security': 'security',
            'code interpreter': 'code_interpreter',
            'benchmarks': 'benchmarks',
            'nuance understanding': 'nuance_understanding',
            'cost': 'cost',
            'data extraction': 'data_extraction',
            'closed-source': 'closed_source',
            'math ability': 'math_ability',
            'tone flexibility': 'tone_flexibility',
            'safety': 'safety',
            'availability': 'availability',
            'hype': 'hype',
            'multimodality': 'multimodality',
            'hardware requirements': 'hardware_requirements',
            'performance': 'performance',
            'speed': 'speed',
            'image generation': 'image_generation',
            'ethics': 'ethics',
            'regulation': 'regulation',
            'safety filters': 'safety_filters',
            'interpretability': 'interpretability',
            'API rate limits': 'api_rate_limits',
            'role-playing': 'role_playing',
            'data generation': 'data_generation',
            'fine-tuning': 'fine_tuning',
            'knowledge cutoff': 'knowledge_cutoff',
            'context window': 'context_window',
            'multilingual support': 'multilingual_support',
            'coherence': 'coherence',
            'humor understanding': 'humor_understanding',
            'pricing model': 'pricing_model',
            'customization': 'customization',
            'privacy': 'privacy',
            'creativity': 'creativity',
            'factual accuracy': 'factual_accuracy',
            'open-source': 'open_source',
            'community': 'community',
            'hallucination': 'hallucination',
            'coding_ability': 'coding_ability',
            'job displacement': 'job_displacement',
            'ease of use': 'ease_of_use',
            'reasoning': 'reasoning',
            'productivity': 'productivity',
            'summarization': 'summarization',
            'response quality': 'response_quality',
            'voice feature': 'voice_feature'
        }
        report_file = 'manual_comparison_complex_report.md'
    else:
        agent_module = importlib.import_module('agentmistral_few_aspects')
        manual_annotations_file = 'manual_annotations_few_aspects.json'
        aspects = [
            'speed', 'cost', 'quality', 'safety', 'reliability', 'performance', 'coding_ability', 'creativity', 'privacy', 'hallucination'
        ]
        aspect_mapping = {a: a for a in aspects}
        report_file = 'manual_comparison_few_aspects_report.md'
    return agent_module, manual_annotations_file, aspects, aspect_mapping, report_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ManualComparisonEvaluator:
    def __init__(self, manual_annotations_file: str, aspects: list, aspect_mapping: dict, agent_module):
        self.manual_annotations_file = manual_annotations_file
        self.aspects = aspects
        self.aspect_mapping = aspect_mapping
        self.reverse_aspect_mapping = {v: k for k, v in self.aspect_mapping.items()}
        self.agent_module = agent_module
        self.llm_names = set(agent_module.llms)

    def load_manual_annotations(self) -> List[Dict]:
        """Load the manually annotated test data."""
        with open(self.manual_annotations_file, 'r') as f:
            return json.load(f)

    def evaluate_llm_recognition(self, manual_data: List[Dict], predictions: Dict[str, Dict]) -> Dict:
        """Evaluate LLM recognition (NER) performance against manual annotations."""
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        llm_recognition_errors = []
        
        for item in manual_data:
            text = item['text']
            test_id = item['id']
            manual_llms = set(item['annotated_llms'])
            
            # Get model predictions
            pred_llms = set()
            if text in predictions and predictions[text].get('status') == 'success':
                pred_llms = {llm['name'] for llm in predictions[text].get('llms', [])}
            
            # Calculate metrics for this text
            tp = len(manual_llms & pred_llms)
            fp = len(pred_llms - manual_llms)
            fn = len(manual_llms - pred_llms)
            
            true_positives += tp
            false_positives += fp
            false_negatives += fn
            
            # Record errors for analysis
            if fp > 0 or fn > 0:
                llm_recognition_errors.append({
                    'test_id': test_id,
                    'text': text,
                    'manual_llms': list(manual_llms),
                    'predicted_llms': list(pred_llms),
                    'false_positives': list(pred_llms - manual_llms),
                    'false_negatives': list(manual_llms - pred_llms)
                })
        
        # Calculate overall metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'total_manual_llms': sum(len(item['annotated_llms']) for item in manual_data),
            'total_predicted_llms': sum(len([llm['name'] for llm in predictions.get(item['text'], {}).get('llms', [])]) for item in manual_data),
            'errors': llm_recognition_errors
        }

    def evaluate_sentiment_analysis(self, manual_data: List[Dict], predictions: Dict[str, Dict]) -> Dict:
        """Evaluate sentiment analysis performance against manual annotations."""
        all_true_sentiments = []
        all_predicted_sentiments = []
        sentiment_errors = []
        
        for item in manual_data:
            text = item['text']
            test_id = item['id']
            manual_sentiments = item['sentiment_annotations']
            
            if text not in predictions or predictions[text].get('status') != 'success':
                continue
            
            pred_llms = predictions[text].get('llms', [])
            
            for pred_llm in pred_llms:
                llm_name = pred_llm['name']
                pred_sentiments = pred_llm.get('sentiments', {})
                
                # Only evaluate if this LLM was manually annotated
                if llm_name in manual_sentiments:
                    manual_llm_sentiments = manual_sentiments[llm_name]
                    
                    # Compare sentiments for each aspect that was manually annotated
                    for aspect, manual_sentiment in manual_llm_sentiments.items():
                        model_field = self.aspect_mapping.get(aspect)
                        if model_field and model_field in pred_sentiments:
                            pred_sentiment = pred_sentiments[model_field]
                            
                            all_true_sentiments.append(manual_sentiment)
                            all_predicted_sentiments.append(pred_sentiment)
                            
                            if manual_sentiment != pred_sentiment:
                                sentiment_errors.append({
                                    'test_id': test_id,
                                    'text': text,
                                    'llm': llm_name,
                                    'aspect': aspect,
                                    'manual_sentiment': manual_sentiment,
                                    'predicted_sentiment': pred_sentiment
                                })
        
        # Calculate classification metrics
        labels = ['positive', 'negative', 'neutral', 'not-present']
        report = classification_report(all_true_sentiments, all_predicted_sentiments, 
                                     labels=labels, output_dict=True, zero_division=0)
        
        # Create confusion matrix
        cm = confusion_matrix(all_true_sentiments, all_predicted_sentiments, labels=labels)
        cm_df = pd.DataFrame(cm, index=labels, columns=labels)
        
        return {
            'classification_report': report,
            'confusion_matrix': cm_df,
            'total_comparisons': len(all_true_sentiments),
            'errors': sentiment_errors
        }

    def run_comparison_evaluation(self) -> Dict:
        """Run the complete comparison evaluation."""
        logging.info("Loading manual annotations...")
        manual_data = self.load_manual_annotations()
        
        logging.info("Running Mistral model predictions...")
        predictions = {}
        for i, item in enumerate(manual_data):
            text = item['text']
            test_id = item['id']
            logging.info(f"Processing test {test_id} ({i+1}/{len(manual_data)}): {text[:80]}...")
            
            try:
                pred, _ = self.agent_module.analyse_post(text)
                predictions[text] = pred
            except Exception as e:
                logging.error(f"Error processing test {test_id}: {e}")
                predictions[text] = {'status': 'error', 'llms': []}
        
        logging.info("Evaluating LLM recognition performance...")
        llm_results = self.evaluate_llm_recognition(manual_data, predictions)
        
        logging.info("Evaluating sentiment analysis performance...")
        sentiment_results = self.evaluate_sentiment_analysis(manual_data, predictions)
        
        return {
            'llm_recognition': llm_results,
            'sentiment_analysis': sentiment_results,
            'manual_data': manual_data,
            'predictions': predictions
        }

    def save_comparison_report(self, results: Dict, output_file: str):
        """Save a detailed comparison report."""
        with open(output_file, 'w') as f:
            f.write("# Manual vs Mistral Model Comparison Report\n\n")
            
            # LLM Recognition Results
            f.write("## LLM Recognition (NER) Performance\n\n")
            llm = results['llm_recognition']
            f.write(f"- **Precision**: {llm['precision']:.4f}\n")
            f.write(f"- **Recall**: {llm['recall']:.4f}\n")
            f.write(f"- **F1-Score**: {llm['f1_score']:.4f}\n")
            f.write(f"- **True Positives**: {llm['true_positives']}\n")
            f.write(f"- **False Positives**: {llm['false_positives']}\n")
            f.write(f"- **False Negatives**: {llm['false_negatives']}\n")
            f.write(f"- **Total Manual LLMs**: {llm['total_manual_llms']}\n")
            f.write(f"- **Total Predicted LLMs**: {llm['total_predicted_llms']}\n\n")
            
            # Sentiment Analysis Results
            f.write("## Sentiment Analysis Performance\n\n")
            sent = results['sentiment_analysis']
            f.write(f"- **Total Comparisons**: {sent['total_comparisons']}\n\n")
            
            f.write("### Classification Report\n\n")
            f.write("```\n")
            for label, metrics in sent['classification_report'].items():
                if isinstance(metrics, dict):
                    f.write(f"{label}:\n")
                    for metric, value in metrics.items():
                        if isinstance(value, float):
                            f.write(f"  {metric}: {value:.4f}\n")
                        else:
                            f.write(f"  {metric}: {value}\n")
                else:
                    f.write(f"{label}: {metrics}\n")
            f.write("```\n\n")
            
            f.write("### Confusion Matrix\n\n")
            f.write(sent['confusion_matrix'].to_markdown())
            f.write("\n\n")
            
            # Detailed Error Analysis
            f.write("## Detailed Error Analysis\n\n")
            
            f.write("### LLM Recognition Errors\n\n")
            if llm['errors']:
                for i, error in enumerate(llm['errors']):
                    f.write(f"#### LLM Recognition Error {i+1}\n")
                    f.write(f"- **Test ID**: {error['test_id']}\n")
                    f.write(f"- **Text**: {error['text']}\n")
                    f.write(f"- **Manual LLMs**: {error['manual_llms']}\n")
                    f.write(f"- **Predicted LLMs**: {error['predicted_llms']}\n")
                    f.write(f"- **False Positives**: {error['false_positives']}\n")
                    f.write(f"- **False Negatives**: {error['false_negatives']}\n\n")
            else:
                f.write("No LLM recognition errors found.\n\n")
            
            f.write("### Sentiment Analysis Errors\n\n")
            if sent['errors']:
                for i, error in enumerate(sent['errors']):
                    f.write(f"#### Sentiment Error {i+1}\n")
                    f.write(f"- **Test ID**: {error['test_id']}\n")
                    f.write(f"- **Text**: {error['text']}\n")
                    f.write(f"- **LLM**: {error['llm']}\n")
                    f.write(f"- **Aspect**: {error['aspect']}\n")
                    f.write(f"- **Manual Sentiment**: `{error['manual_sentiment']}`\n")
                    f.write(f"- **Predicted Sentiment**: `{error['predicted_sentiment']}`\n\n")
            else:
                f.write("No sentiment analysis errors found.\n\n")
            
            # Summary Statistics
            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total Test Cases**: {len(results['manual_data'])}\n")
            f.write(f"- **Test Cases with LLM Mentions**: {len([item for item in results['manual_data'] if item['annotated_llms']])}\n")
            f.write(f"- **Test Cases without LLM Mentions**: {len([item for item in results['manual_data'] if not item['annotated_llms']])}\n")
            f.write(f"- **Total Manual Sentiment Annotations**: {sum(len(item['sentiment_annotations']) for item in results['manual_data'])}\n")

def main():
    """
    Manual vs Mistral Model Comparison
    Usage:
      python manual_comparison_evaluation.py [--full-aspects | --few-aspects]
    If neither is specified, defaults to --full-aspects.
    """
    parser = argparse.ArgumentParser(description="Manual vs Mistral Model Comparison Evaluation")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--full-aspects', action='store_true', help='Use all aspects (default)')
    group.add_argument('--few-aspects', action='store_true', help='Use only the selected few aspects')
    args = parser.parse_args()

    full_aspects = not args.few_aspects
    agent_module, manual_annotations_file, aspects, aspect_mapping, report_file = get_agent_and_config(full_aspects)

    evaluator = ManualComparisonEvaluator(manual_annotations_file, aspects, aspect_mapping, agent_module)
    results = evaluator.run_comparison_evaluation()

    # Print summary
    print("\n" + "="*60)
    print("MANUAL vs MISTRAL MODEL COMPARISON RESULTS")
    print("="*60)

    llm = results['llm_recognition']
    print(f"\nLLM Recognition Performance:")
    print(f"Precision: {llm['precision']:.4f}")
    print(f"Recall: {llm['recall']:.4f}")
    print(f"F1-Score: {llm['f1_score']:.4f}")
    print(f"Total Manual LLMs: {llm['total_manual_llms']}")
    print(f"Total Predicted LLMs: {llm['total_predicted_llms']}")

    sent = results['sentiment_analysis']
    print(f"\nSentiment Analysis Performance:")
    print(f"Total Comparisons: {sent['total_comparisons']}")
    print(f"Accuracy: {sent['classification_report']['accuracy']:.4f}")

    # Save detailed report
    evaluator.save_comparison_report(results, output_file=report_file)
    print(f"\nDetailed comparison report saved to: {report_file}")

if __name__ == "__main__":
    main() 