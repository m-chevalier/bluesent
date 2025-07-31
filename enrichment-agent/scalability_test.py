#!/usr/bin/env python3
"""
Scalability Test for Enrichment Agent
Tests performance with increasing numbers of aspects
"""

import json
import time
import logging
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from agentmistral import analyse_post
from agentmistral_few_aspects import analyse_post as analyse_post_few

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ScalabilityTester:
    def __init__(self):
        self.test_texts = [
            "The context window of Claude 3 is amazing for summarizing entire Github repos, but the API cost for that many tokens is eyewatering.",
            "Tried to use Gemini for a creative writing task and it was so generic. The creativity just isn't there compared to GPT-4.",
            "The new multimodality in GPT-4o is insane. I can upload a screenshot of a website and it will write the HTML/CSS for it. Game changer.",
            "Llama 3's open-source model is great for research, but the lack of an official, reliable API makes its availability for production a challenge.",
            "The speed of Groq's inference is on another level. It makes ChatGPT feel sluggish in comparison. #AI #speed",
            "I'm really worried about data privacy when using these tools. Who owns my conversations? The security and privacy policies are too vague.",
            "The model's reasoning on legal text is impressive, but I would never trust it without a human lawyer verifying everything. The risk is too high.",
            "The Hugging Face community has already released dozens of fine-tuned Llama 3 models. The power of open-source is amazing.",
            "The latest fine-tuning API update from OpenAI has new parameters for controlling the learning rate.",
            "The math ability of the new models is getting better, but it still fails on multi-step word problems that require careful setup."
        ]
        
        # Define aspect sets of increasing size
        self.aspect_sets = {
            5: ['speed', 'cost', 'quality', 'safety', 'performance'],
            10: ['speed', 'cost', 'quality', 'safety', 'performance', 'coding_ability', 'creativity', 'privacy', 'hallucination', 'reliability'],
            20: ['speed', 'cost', 'quality', 'safety', 'performance', 'coding_ability', 'creativity', 'privacy', 'hallucination', 'reliability',
                 'code generation', 'API documentation', 'environmental impact', 'bias', 'security', 'code interpreter', 'benchmarks', 'nuance understanding', 'data extraction', 'closed-source'],
            30: ['speed', 'cost', 'quality', 'safety', 'performance', 'coding_ability', 'creativity', 'privacy', 'hallucination', 'reliability',
                 'code generation', 'API documentation', 'environmental impact', 'bias', 'security', 'code interpreter', 'benchmarks', 'nuance understanding', 'data extraction', 'closed-source',
                 'math ability', 'tone flexibility', 'availability', 'hype', 'multimodality', 'hardware requirements', 'image generation', 'ethics', 'regulation', 'safety filters'],
            50: ['speed', 'cost', 'quality', 'safety', 'performance', 'coding_ability', 'creativity', 'privacy', 'hallucination', 'reliability',
                 'code generation', 'API documentation', 'environmental impact', 'bias', 'security', 'code interpreter', 'benchmarks', 'nuance understanding', 'data extraction', 'closed-source',
                 'math ability', 'tone flexibility', 'availability', 'hype', 'multimodality', 'hardware requirements', 'image generation', 'ethics', 'regulation', 'safety filters',
                 'interpretability', 'API rate limits', 'role-playing', 'data generation', 'fine-tuning', 'knowledge cutoff', 'context window', 'multilingual support', 'coherence', 'humor understanding',
                 'pricing model', 'customization', 'factual accuracy', 'open-source', 'community', 'job displacement', 'ease of use', 'reasoning', 'productivity', 'summarization', 'response quality', 'voice feature']
        }

    def test_performance_with_aspects(self, num_aspects: int, test_texts: List[str]) -> Dict:
        """Test performance with a specific number of aspects."""
        results = {
            'num_aspects': num_aspects,
            'total_time': 0,
            'avg_time_per_text': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'total_predictions': 0,
            'avg_response_size': 0,
            'response_sizes': []
        }
        
        logging.info(f"Testing with {num_aspects} aspects...")
        
        for i, text in enumerate(test_texts):
            start_time = time.time()
            
            try:
                # Use the appropriate agent based on number of aspects
                if num_aspects <= 10:
                    prediction, _ = analyse_post_few(text)
                else:
                    prediction, _ = analyse_post(text)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                results['total_time'] += processing_time
                results['total_predictions'] += 1
                
                if prediction and prediction.get('status') == 'success':
                    results['successful_predictions'] += 1
                    # Calculate response size (rough estimate)
                    response_size = len(str(prediction))
                    results['response_sizes'].append(response_size)
                else:
                    results['failed_predictions'] += 1
                
                logging.info(f"Text {i+1}/{len(test_texts)}: {processing_time:.2f}s")
                
            except Exception as e:
                logging.error(f"Error processing text {i+1}: {e}")
                results['failed_predictions'] += 1
                results['total_predictions'] += 1
        
        # Calculate averages
        if results['total_predictions'] > 0:
            results['avg_time_per_text'] = results['total_time'] / results['total_predictions']
            results['success_rate'] = results['successful_predictions'] / results['total_predictions']
        
        if results['response_sizes']:
            results['avg_response_size'] = sum(results['response_sizes']) / len(results['response_sizes'])
        
        return results

    def run_scalability_test(self) -> Dict:
        """Run scalability tests with different numbers of aspects."""
        all_results = {}
        
        for num_aspects in sorted(self.aspect_sets.keys()):
            logging.info(f"\n{'='*50}")
            logging.info(f"Testing scalability with {num_aspects} aspects")
            logging.info(f"{'='*50}")
            
            results = self.test_performance_with_aspects(num_aspects, self.test_texts)
            all_results[num_aspects] = results
            
            logging.info(f"Results for {num_aspects} aspects:")
            logging.info(f"  Total time: {results['total_time']:.2f}s")
            logging.info(f"  Avg time per text: {results['avg_time_per_text']:.2f}s")
            logging.info(f"  Success rate: {results['success_rate']:.2%}")
            logging.info(f"  Avg response size: {results['avg_response_size']:.0f} chars")
        
        return all_results

    def create_scalability_report(self, results: Dict, output_file: str = 'scalability_report.md'):
        """Create a comprehensive scalability report."""
        with open(output_file, 'w') as f:
            f.write("# Scalability Test Report\n\n")
            f.write("## Performance with Increasing Number of Aspects\n\n")
            
            # Create summary table
            f.write("| Aspects | Total Time (s) | Avg Time/Text (s) | Success Rate | Avg Response Size |\n")
            f.write("|---------|----------------|-------------------|--------------|-------------------|\n")
            
            for num_aspects in sorted(results.keys()):
                r = results[num_aspects]
                f.write(f"| {num_aspects} | {r['total_time']:.2f} | {r['avg_time_per_text']:.2f} | {r['success_rate']:.2%} | {r['avg_response_size']:.0f} |\n")
            
            f.write("\n## Detailed Results\n\n")
            
            for num_aspects in sorted(results.keys()):
                r = results[num_aspects]
                f.write(f"### {num_aspects} Aspects\n\n")
                f.write(f"- **Total Processing Time**: {r['total_time']:.2f} seconds\n")
                f.write(f"- **Average Time per Text**: {r['avg_time_per_text']:.2f} seconds\n")
                f.write(f"- **Success Rate**: {r['success_rate']:.2%}\n")
                f.write(f"- **Successful Predictions**: {r['successful_predictions']}/{r['total_predictions']}\n")
                f.write(f"- **Failed Predictions**: {r['failed_predictions']}\n")
                f.write(f"- **Average Response Size**: {r['avg_response_size']:.0f} characters\n\n")
            
            # Performance analysis
            f.write("## Performance Analysis\n\n")
            
            # Calculate scaling factors
            base_aspects = min(results.keys())
            base_time = results[base_aspects]['avg_time_per_text']
            
            f.write("### Scaling Factors (relative to base)\n\n")
            f.write("| Aspects | Time Scaling Factor |\n")
            f.write("|---------|-------------------|\n")
            
            for num_aspects in sorted(results.keys()):
                scaling_factor = results[num_aspects]['avg_time_per_text'] / base_time
                f.write(f"| {num_aspects} | {scaling_factor:.2f}x |\n")
            
            f.write(f"\nBase: {base_aspects} aspects = {base_time:.2f}s per text\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            # Find optimal performance point
            best_success_rate = max(r['success_rate'] for r in results.values())
            best_aspects = [num for num, r in results.items() if r['success_rate'] == best_success_rate][0]
            
            f.write(f"- **Optimal Success Rate**: {best_success_rate:.2%} with {best_aspects} aspects\n")
            
            # Find fastest processing
            fastest_time = min(r['avg_time_per_text'] for r in results.values())
            fastest_aspects = [num for num, r in results.items() if r['avg_time_per_text'] == fastest_time][0]
            
            f.write(f"- **Fastest Processing**: {fastest_time:.2f}s per text with {fastest_aspects} aspects\n")
            
            # Efficiency analysis
            efficiency_scores = {}
            for num_aspects, r in results.items():
                # Efficiency = success_rate / (time_per_text * num_aspects)
                efficiency = r['success_rate'] / (r['avg_time_per_text'] * num_aspects)
                efficiency_scores[num_aspects] = efficiency
            
            best_efficiency = max(efficiency_scores.values())
            best_efficiency_aspects = [num for num, score in efficiency_scores.items() if score == best_efficiency][0]
            
            f.write(f"- **Most Efficient**: {best_efficiency_aspects} aspects (efficiency score: {best_efficiency:.4f})\n")

    def plot_scalability_results(self, results: Dict, output_file: str = 'scalability_plot.png'):
        """Create visualization of scalability results."""
        try:
            import matplotlib.pyplot as plt
            
            aspects = sorted(results.keys())
            times = [results[num]['avg_time_per_text'] for num in aspects]
            success_rates = [results[num]['success_rate'] for num in aspects]
            response_sizes = [results[num]['avg_response_size'] for num in aspects]
            
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
            
            # Time scaling
            ax1.plot(aspects, times, 'bo-', linewidth=2, markersize=8)
            ax1.set_xlabel('Number of Aspects')
            ax1.set_ylabel('Average Time per Text (seconds)')
            ax1.set_title('Processing Time Scaling')
            ax1.grid(True, alpha=0.3)
            
            # Success rate
            ax2.plot(aspects, success_rates, 'go-', linewidth=2, markersize=8)
            ax2.set_xlabel('Number of Aspects')
            ax2.set_ylabel('Success Rate')
            ax2.set_title('Success Rate vs Aspects')
            ax2.grid(True, alpha=0.3)
            
            # Response size
            ax3.plot(aspects, response_sizes, 'ro-', linewidth=2, markersize=8)
            ax3.set_xlabel('Number of Aspects')
            ax3.set_ylabel('Average Response Size (characters)')
            ax3.set_title('Response Size Scaling')
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logging.info(f"Scalability plot saved to: {output_file}")
            
        except ImportError:
            logging.warning("matplotlib not available, skipping plot generation")

def main():
    """Main function to run scalability tests."""
    tester = ScalabilityTester()
    
    logging.info("Starting scalability tests...")
    results = tester.run_scalability_test()
    
    # Create reports
    tester.create_scalability_report(results)
    tester.plot_scalability_results(results)
    
    logging.info("Scalability testing completed!")
    logging.info("Reports generated:")
    logging.info("- scalability_report.md")
    logging.info("- scalability_plot.png")

if __name__ == "__main__":
    main() 