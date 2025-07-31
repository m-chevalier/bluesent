import json
from dotenv import load_dotenv
import os
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import logging
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
import pandas as pd
import numpy as np

# Load environment variables from .env file before other imports
load_dotenv()

from agentmistral import analyse_post, llms

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ComprehensiveEvaluator:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.llm_names = set(llms)
        self.aspects = [
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
        
        # Aspect mapping for model output
        self.aspect_mapping = {
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
        self.reverse_aspect_mapping = {v: k for k, v in self.aspect_mapping.items()}

    def load_data(self) -> List[Dict]:
        """Load the ground truth data."""
        with open(self.data_file, 'r') as f:
            return json.load(f)

    def extract_llms_from_text(self, text: str) -> Set[str]:
        """Extract LLM mentions from text using simple keyword matching."""
        text_lower = text.lower()
        detected_llms = set()
        
        # Handle special cases and variations with standardized output
        llm_variations = {
            'chatGPT': ['chatgpt', 'chat gpt', 'gpt-4', 'gpt-3', 'gpt4', 'gpt3'],
            'claude': ['claude', 'claude 3', 'claude-3'],
            'gemini': ['gemini', 'gemini 1.5', 'gemini-1.5'],
            'bard': ['bard', 'google bard'],
            'llama': ['llama', 'llama 3', 'llama-3'],
            'mistral': ['mistral'],
            'grok': ['grok', 'grok 2', 'groq'],
            'kimi': ['kimi'],
            'qwen': ['qwen'],
            'deepseek': ['deepseek'],
            'gemma': ['gemma'],
            'minimax': ['minimax'],
            'hunyuan': ['hunyuan']
        }
        
        for standard_name, variations in llm_variations.items():
            for variation in variations:
                if variation in text_lower:
                    # Special handling for GPT references to avoid false positives
                    if standard_name == 'chatGPT' and variation.startswith('gpt'):
                        # Only detect GPT if it's clearly referring to ChatGPT/GPT models
                        if 'gpt-4' in text_lower or 'gpt-3' in text_lower or 'chatgpt' in text_lower:
                            detected_llms.add(standard_name)
                    else:
                        detected_llms.add(standard_name)
                    break
        
        return detected_llms

    def prepare_ground_truth(self, data: List[Dict]) -> Dict[str, Dict]:
        """Prepare ground truth data with LLM detection and sentiment labels."""
        ground_truth = {}
        
        for item in data:
            text = item['text']
            if text not in ground_truth:
                # Extract LLMs from text
                detected_llms = self.extract_llms_from_text(text)
                ground_truth[text] = {
                    'llms': detected_llms,
                    'sentiments': defaultdict(lambda: defaultdict(str))
                }
            
            # Add sentiment for the aspect
            llm_mentions = ground_truth[text]['llms']
            if llm_mentions:  # If LLMs are detected, assign sentiment to all detected LLMs
                for llm in llm_mentions:
                    ground_truth[text]['sentiments'][llm][item['aspect']] = item['sentiment']
            else:
                # If no LLM detected, this might be a general statement
                # We'll handle this case in evaluation
                pass
        
        return ground_truth

    def evaluate_ner(self, ground_truth: Dict[str, Dict], predictions: Dict[str, Dict]) -> Dict:
        """Evaluate Named Entity Recognition (LLM detection) performance."""
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        ner_errors = []
        
        for text, gt_data in ground_truth.items():
            gt_llms = gt_data['llms']
            pred_llms = set()
            
            if text in predictions:
                pred_llms = {llm['name'] for llm in predictions[text].get('llms', [])}
            
            # Calculate metrics
            tp = len(gt_llms & pred_llms)
            fp = len(pred_llms - gt_llms)
            fn = len(gt_llms - pred_llms)
            
            true_positives += tp
            false_positives += fp
            false_negatives += fn
            
            # Record errors for analysis
            if fp > 0 or fn > 0:
                ner_errors.append({
                    'text': text,
                    'ground_truth_llms': list(gt_llms),
                    'predicted_llms': list(pred_llms),
                    'false_positives': list(pred_llms - gt_llms),
                    'false_negatives': list(gt_llms - pred_llms)
                })
        
        # Calculate metrics
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
            'errors': ner_errors
        }

    def evaluate_sentiment(self, ground_truth: Dict[str, Dict], predictions: Dict[str, Dict]) -> Dict:
        """Evaluate sentiment analysis performance."""
        all_true_sentiments = []
        all_predicted_sentiments = []
        sentiment_errors = []
        
        for text, gt_data in ground_truth.items():
            gt_llms = gt_data['llms']
            gt_sentiments = gt_data['sentiments']
            
            if text not in predictions:
                continue
                
            pred_llms = predictions[text].get('llms', [])
            
            for pred_llm in pred_llms:
                llm_name = pred_llm['name']
                pred_sentiments = pred_llm.get('sentiments', {})
                
                # Only evaluate if this LLM was actually mentioned in ground truth
                if llm_name in gt_llms:
                    for aspect in self.aspects:
                        model_field = self.aspect_mapping.get(aspect)
                        if model_field and model_field in pred_sentiments:
                            pred_sentiment = pred_sentiments[model_field]
                            gt_sentiment = gt_sentiments[llm_name].get(aspect, 'not-present')
                            
                            all_true_sentiments.append(gt_sentiment)
                            all_predicted_sentiments.append(pred_sentiment)
                            
                            if gt_sentiment != pred_sentiment:
                                sentiment_errors.append({
                                    'text': text,
                                    'llm': llm_name,
                                    'aspect': aspect,
                                    'ground_truth': gt_sentiment,
                                    'prediction': pred_sentiment
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
            'total_predictions': len(all_true_sentiments),
            'errors': sentiment_errors
        }

    def run_evaluation(self) -> Dict:
        """Run the comprehensive evaluation."""
        logging.info("Loading data...")
        data = self.load_data()
        
        logging.info("Preparing ground truth...")
        ground_truth = self.prepare_ground_truth(data)
        
        logging.info("Running model predictions...")
        predictions = {}
        for i, text in enumerate(ground_truth.keys()):
            logging.info(f"Processing text {i+1}/{len(ground_truth)}: {text[:80]}...")
            try:
                pred, _ = analyse_post(text)
                predictions[text] = pred
            except Exception as e:
                logging.error(f"Error processing text: {text} - {e}")
                predictions[text] = {'status': 'error', 'llms': []}
        
        logging.info("Evaluating NER performance...")
        ner_results = self.evaluate_ner(ground_truth, predictions)
        
        logging.info("Evaluating sentiment performance...")
        sentiment_results = self.evaluate_sentiment(ground_truth, predictions)
        
        return {
            'ner_evaluation': ner_results,
            'sentiment_evaluation': sentiment_results,
            'ground_truth': ground_truth,
            'predictions': predictions
        }

    def save_comprehensive_report(self, results: Dict, output_file: str = 'comprehensive_evaluation_report.md'):
        """Save a comprehensive evaluation report."""
        with open(output_file, 'w') as f:
            f.write("# Comprehensive Evaluation Report\n\n")
            
            # NER Results
            f.write("## Named Entity Recognition (LLM Detection) Results\n\n")
            ner = results['ner_evaluation']
            f.write(f"- **Precision**: {ner['precision']:.4f}\n")
            f.write(f"- **Recall**: {ner['recall']:.4f}\n")
            f.write(f"- **F1-Score**: {ner['f1_score']:.4f}\n")
            f.write(f"- **True Positives**: {ner['true_positives']}\n")
            f.write(f"- **False Positives**: {ner['false_positives']}\n")
            f.write(f"- **False Negatives**: {ner['false_negatives']}\n\n")
            
            # Sentiment Results
            f.write("## Sentiment Analysis Results\n\n")
            sent = results['sentiment_evaluation']
            f.write(f"- **Total Predictions**: {sent['total_predictions']}\n\n")
            
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
            
            # Error Analysis
            f.write("## Error Analysis\n\n")
            
            f.write("### NER Errors\n\n")
            if ner['errors']:
                for i, error in enumerate(ner['errors'][:20]):  # Show first 20 errors
                    f.write(f"#### NER Error {i+1}\n")
                    f.write(f"- **Text**: {error['text']}\n")
                    f.write(f"- **Ground Truth LLMs**: {error['ground_truth_llms']}\n")
                    f.write(f"- **Predicted LLMs**: {error['predicted_llms']}\n")
                    f.write(f"- **False Positives**: {error['false_positives']}\n")
                    f.write(f"- **False Negatives**: {error['false_negatives']}\n\n")
            else:
                f.write("No NER errors found.\n\n")
            
            f.write("### Sentiment Errors\n\n")
            if sent['errors']:
                for i, error in enumerate(sent['errors'][:20]):  # Show first 20 errors
                    f.write(f"#### Sentiment Error {i+1}\n")
                    f.write(f"- **Text**: {error['text']}\n")
                    f.write(f"- **LLM**: {error['llm']}\n")
                    f.write(f"- **Aspect**: {error['aspect']}\n")
                    f.write(f"- **Ground Truth**: `{error['ground_truth']}`\n")
                    f.write(f"- **Prediction**: `{error['prediction']}`\n\n")
            else:
                f.write("No sentiment errors found.\n\n")

def main():
    """Main function to run the comprehensive evaluation."""
    evaluator = ComprehensiveEvaluator('enrichment-agent/randd/data.json')
    results = evaluator.run_evaluation()
    
    # Print summary
    print("\n" + "="*50)
    print("COMPREHENSIVE EVALUATION RESULTS")
    print("="*50)
    
    ner = results['ner_evaluation']
    print(f"\nNER Performance:")
    print(f"Precision: {ner['precision']:.4f}")
    print(f"Recall: {ner['recall']:.4f}")
    print(f"F1-Score: {ner['f1_score']:.4f}")
    
    sent = results['sentiment_evaluation']
    print(f"\nSentiment Performance:")
    print(f"Total Predictions: {sent['total_predictions']}")
    print(f"Accuracy: {sent['classification_report']['accuracy']:.4f}")
    
    # Save detailed report
    evaluator.save_comprehensive_report(results)
    print(f"\nDetailed report saved to: comprehensive_evaluation_report.md")

if __name__ == "__main__":
    main() 