#!/usr/bin/env python3
"""
Comparative Evaluation Script
Tests both few aspects (10) and full aspects (50) configurations on the same dataset
"""

import json
import logging
import argparse
from typing import Dict, List, Tuple
import importlib
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ComparativeEvaluator:
    def __init__(self, test_data_file: str):
        self.test_data_file = test_data_file
        self.results = {}
        
    def load_test_data(self) -> List[Dict]:
        """Load the test dataset."""
        logging.info(f"Loading test data from {self.test_data_file}")
        with open(self.test_data_file, 'r') as f:
            return json.load(f)
    
    def run_few_aspects_evaluation(self, test_data: List[Dict]) -> Dict:
        """Run evaluation with 10 aspects configuration."""
        logging.info("Running few aspects (10) evaluation...")
        
        # Import the few aspects agent
        agent_module = importlib.import_module('agentmistral_few_aspects')
        
        # Define the 10 aspects
        aspects = [
            'speed', 'cost', 'quality', 'safety', 'reliability', 
            'performance', 'coding_ability', 'creativity', 'privacy', 'hallucination'
        ]
        
        results = {
            'llm_predictions': [],
            'sentiment_predictions': [],
            'total_llms_manual': 0,
            'total_llms_predicted': 0,
            'total_sentiment_comparisons': 0,
            'correct_sentiment': 0
        }
        
        for i, test_case in enumerate(test_data):
            logging.info(f"Processing test {test_case.get('id', f'test_{i+1}')} ({i+1}/{len(test_data)}): {test_case['text'][:100]}...")
            
            try:
                # Get prediction from few aspects agent
                prediction = agent_module.analyse_post(test_case['text'])
                
                # Extract LLMs and sentiments
                predicted_llms = prediction.get('llms', [])
                predicted_sentiments = prediction.get('sentiments', {})
                
                # Manual annotations
                manual_llms = test_case.get('llms', [])
                manual_sentiments = test_case.get('sentiments', {})
                
                # Count LLMs
                results['total_llms_manual'] += len(manual_llms)
                results['total_llms_predicted'] += len(predicted_llms)
                
                # Compare LLMs
                llm_comparison = {
                    'test_id': test_case.get('id', f'test_{i+1}'),
                    'text': test_case['text'],
                    'manual_llms': manual_llms,
                    'predicted_llms': predicted_llms,
                    'true_positives': len(set(manual_llms) & set(predicted_llms)),
                    'false_positives': len(set(predicted_llms) - set(manual_llms)),
                    'false_negatives': len(set(manual_llms) - set(predicted_llms))
                }
                results['llm_predictions'].append(llm_comparison)
                
                # Compare sentiments for each aspect
                for aspect in aspects:
                    if aspect in manual_sentiments:
                        manual_sentiment = manual_sentiments[aspect]
                        predicted_sentiment = predicted_sentiments.get(aspect, 'not-present')
                        
                        sentiment_comparison = {
                            'test_id': test_case.get('id', f'test_{i+1}'),
                            'llm': test_case.get('llm', 'unknown'),
                            'aspect': aspect,
                            'manual_sentiment': manual_sentiment,
                            'predicted_sentiment': predicted_sentiment,
                            'correct': manual_sentiment == predicted_sentiment
                        }
                        results['sentiment_predictions'].append(sentiment_comparison)
                        results['total_sentiment_comparisons'] += 1
                        if sentiment_comparison['correct']:
                            results['correct_sentiment'] += 1
                            
            except Exception as e:
                logging.error(f"Error processing test case {i+1}: {e}")
                continue
        
        return results
    
    def run_full_aspects_evaluation(self, test_data: List[Dict]) -> Dict:
        """Run evaluation with 50 aspects configuration."""
        logging.info("Running full aspects (50) evaluation...")
        
        # Import the full aspects agent
        agent_module = importlib.import_module('agentmistral')
        
        # Define the 50 aspects
        aspects = [
            'code generation', 'API documentation', 'environmental impact', 'bias', 'security', 
            'reliability', 'performance', 'speed', 'cost', 'quality', 'safety', 'creativity', 
            'privacy', 'hallucination', 'multimodality', 'context window', 'knowledge cutoff',
            'fine-tuning', 'open source', 'closed source', 'community', 'enterprise', 
            'research', 'production', 'edge deployment', 'scalability', 'availability',
            'regional availability', 'regulatory compliance', 'ethics', 'transparency',
            'interpretability', 'explainability', 'auditability', 'accountability',
            'data extraction', 'summarization', 'translation', 'multilingual support',
            'reasoning', 'mathematical reasoning', 'logical reasoning', 'creative reasoning',
            'factual accuracy', 'response quality', 'tone flexibility', 'style adaptation',
            'conversation coherence', 'character consistency', 'role-playing', 'voice synthesis',
            'image generation', 'video analysis'
        ]
        
        results = {
            'llm_predictions': [],
            'sentiment_predictions': [],
            'total_llms_manual': 0,
            'total_llms_predicted': 0,
            'total_sentiment_comparisons': 0,
            'correct_sentiment': 0
        }
        
        for i, test_case in enumerate(test_data):
            logging.info(f"Processing test {test_case.get('id', f'test_{i+1}')} ({i+1}/{len(test_data)}): {test_case['text'][:100]}...")
            
            try:
                # Get prediction from full aspects agent
                prediction = agent_module.analyse_post(test_case['text'])
                
                # Extract LLMs and sentiments
                predicted_llms = prediction.get('llms', [])
                predicted_sentiments = prediction.get('sentiments', {})
                
                # Manual annotations
                manual_llms = test_case.get('llms', [])
                manual_sentiments = test_case.get('sentiments', {})
                
                # Count LLMs
                results['total_llms_manual'] += len(manual_llms)
                results['total_llms_predicted'] += len(predicted_llms)
                
                # Compare LLMs
                llm_comparison = {
                    'test_id': test_case.get('id', f'test_{i+1}'),
                    'text': test_case['text'],
                    'manual_llms': manual_llms,
                    'predicted_llms': predicted_llms,
                    'true_positives': len(set(manual_llms) & set(predicted_llms)),
                    'false_positives': len(set(predicted_llms) - set(manual_llms)),
                    'false_negatives': len(set(manual_llms) - set(predicted_llms))
                }
                results['llm_predictions'].append(llm_comparison)
                
                # Compare sentiments for each aspect
                for aspect in aspects:
                    if aspect in manual_sentiments:
                        manual_sentiment = manual_sentiments[aspect]
                        predicted_sentiment = predicted_sentiments.get(aspect, 'not-present')
                        
                        sentiment_comparison = {
                            'test_id': test_case.get('id', f'test_{i+1}'),
                            'llm': test_case.get('llm', 'unknown'),
                            'aspect': aspect,
                            'manual_sentiment': manual_sentiment,
                            'predicted_sentiment': predicted_sentiment,
                            'correct': manual_sentiment == predicted_sentiment
                        }
                        results['sentiment_predictions'].append(sentiment_comparison)
                        results['total_sentiment_comparisons'] += 1
                        if sentiment_comparison['correct']:
                            results['correct_sentiment'] += 1
                            
            except Exception as e:
                logging.error(f"Error processing test case {i+1}: {e}")
                continue
        
        return results
    
    def calculate_metrics(self, results: Dict) -> Dict:
        """Calculate performance metrics."""
        # LLM metrics
        total_true_positives = sum(r['true_positives'] for r in results['llm_predictions'])
        total_false_positives = sum(r['false_positives'] for r in results['llm_predictions'])
        total_false_negatives = sum(r['false_negatives'] for r in results['llm_predictions'])
        
        precision = total_true_positives / (total_true_positives + total_false_positives) if (total_true_positives + total_false_positives) > 0 else 0
        recall = total_true_positives / (total_true_positives + total_false_negatives) if (total_true_positives + total_false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Sentiment metrics
        accuracy = results['correct_sentiment'] / results['total_sentiment_comparisons'] if results['total_sentiment_comparisons'] > 0 else 0
        
        return {
            'llm_precision': precision,
            'llm_recall': recall,
            'llm_f1_score': f1_score,
            'sentiment_accuracy': accuracy,
            'total_llms_manual': results['total_llms_manual'],
            'total_llms_predicted': results['total_llms_predicted'],
            'total_sentiment_comparisons': results['total_sentiment_comparisons'],
            'correct_sentiment': results['correct_sentiment']
        }
    
    def run_comparative_evaluation(self) -> Dict:
        """Run both evaluations on the same dataset."""
        test_data = self.load_test_data()
        
        # Run few aspects evaluation
        few_aspects_results = self.run_few_aspects_evaluation(test_data)
        few_aspects_metrics = self.calculate_metrics(few_aspects_results)
        
        # Run full aspects evaluation
        full_aspects_results = self.run_full_aspects_evaluation(test_data)
        full_aspects_metrics = self.calculate_metrics(full_aspects_results)
        
        # Generate comparison report
        comparison_report = self.generate_comparison_report(few_aspects_metrics, full_aspects_metrics)
        
        return {
            'few_aspects': few_aspects_metrics,
            'full_aspects': full_aspects_metrics,
            'comparison': comparison_report,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_comparison_report(self, few_metrics: Dict, full_metrics: Dict) -> Dict:
        """Generate comparison analysis."""
        return {
            'llm_f1_change': full_metrics['llm_f1_score'] - few_metrics['llm_f1_score'],
            'llm_precision_change': full_metrics['llm_precision'] - few_metrics['llm_precision'],
            'llm_recall_change': full_metrics['llm_recall'] - few_metrics['llm_recall'],
            'sentiment_accuracy_change': full_metrics['sentiment_accuracy'] - few_metrics['sentiment_accuracy'],
            'performance_degradation': full_metrics['llm_f1_score'] < few_metrics['llm_f1_score'],
            'sentiment_improvement': full_metrics['sentiment_accuracy'] > few_metrics['sentiment_accuracy']
        }
    
    def save_results(self, results: Dict, output_file: str):
        """Save results to file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Comparative evaluation of few vs full aspects')
    parser.add_argument('--test-data', default='manual_annotations_few_aspects.json', 
                       help='Test data file to use for both evaluations')
    parser.add_argument('--output', default='comparative_evaluation_results.json',
                       help='Output file for results')
    
    args = parser.parse_args()
    
    evaluator = ComparativeEvaluator(args.test_data)
    results = evaluator.run_comparative_evaluation()
    evaluator.save_results(results, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("COMPARATIVE EVALUATION RESULTS")
    print("="*60)
    
    few = results['few_aspects']
    full = results['full_aspects']
    comp = results['comparison']
    
    print(f"\nLLM Recognition Performance:")
    print(f"  Few Aspects (10):  F1={few['llm_f1_score']:.4f}, Precision={few['llm_precision']:.4f}, Recall={few['llm_recall']:.4f}")
    print(f"  Full Aspects (50): F1={full['llm_f1_score']:.4f}, Precision={full['llm_precision']:.4f}, Recall={full['llm_recall']:.4f}")
    print(f"  Change:            F1={comp['llm_f1_change']:+.4f}, Precision={comp['llm_precision_change']:+.4f}, Recall={comp['llm_recall_change']:+.4f}")
    
    print(f"\nSentiment Analysis Performance:")
    print(f"  Few Aspects (10):  Accuracy={few['sentiment_accuracy']:.4f}")
    print(f"  Full Aspects (50): Accuracy={full['sentiment_accuracy']:.4f}")
    print(f"  Change:            Accuracy={comp['sentiment_accuracy_change']:+.4f}")
    
    print(f"\nPerformance Analysis:")
    print(f"  LLM Performance Degradation: {'Yes' if comp['performance_degradation'] else 'No'}")
    print(f"  Sentiment Improvement: {'Yes' if comp['sentiment_improvement'] else 'No'}")
    
    print(f"\nDetailed results saved to: {args.output}")

if __name__ == "__main__":
    main() 