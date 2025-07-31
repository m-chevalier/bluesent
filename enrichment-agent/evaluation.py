import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file before other imports
load_dotenv()

from agentmistral import analyse_post
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(filepath):
    """Loads the ground truth data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def get_unique_texts(data):
    """Extracts unique texts and their corresponding ground truths."""
    texts = {}
    for item in data:
        text = item['text']
        if text not in texts:
            texts[text] = []
        texts[text].append({'aspect': item['aspect'], 'sentiment': item['sentiment']})
    return texts

def evaluate_model(unique_texts, all_aspects):
    """Evaluates the model and returns true and predicted sentiments."""
    y_true = []
    y_pred = []
    mismatches = []

    # Create a mapping from data aspects to model field names
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
        'response_quality': 'response_quality',
        'voice feature': 'voice_feature'
    }
    # Create a reverse mapping to be used later
    reverse_aspect_mapping = {v: k for k, v in aspect_mapping.items()}


    for i, (text, ground_truths) in enumerate(unique_texts.items()):
        logging.info(f"Processing text {i+1}/{len(unique_texts)}: {text[:80]}...")
        
        # 1. Create a complete ground truth dictionary for the current text
        ground_truth_sentiments = {aspect: 'not-present' for aspect in all_aspects}
        for gt in ground_truths:
            ground_truth_sentiments[gt['aspect']] = gt['sentiment']

        try:
            # 2. Get the model's predictions
            predictions, _ = analyse_post(text)
            
            # 3. Create a complete prediction dictionary
            predicted_sentiments = {aspect: 'not-present' for aspect in all_aspects}
            if predictions and predictions.get('status') == 'success' and predictions.get('llms'):
                # Assuming we evaluate the first LLM found
                llm_sentiments = predictions['llms'][0].get('sentiments', {})
                for model_field, sentiment in llm_sentiments.items():
                    if sentiment != 'not-present':
                        data_aspect = reverse_aspect_mapping.get(model_field)
                        if data_aspect:
                            predicted_sentiments[data_aspect] = sentiment

            # 4. Compare ground truth and predictions for all aspects
            for aspect in all_aspects:
                true_sentiment = ground_truth_sentiments[aspect]
                pred_sentiment = predicted_sentiments[aspect]

                y_true.append(true_sentiment)
                y_pred.append(pred_sentiment)

                if true_sentiment != pred_sentiment:
                    mismatches.append({
                        'text': text,
                        'aspect': aspect,
                        'ground_truth': true_sentiment,
                        'prediction': pred_sentiment
                    })

        except Exception as e:
            logging.error(f"Error processing text: {text} - {e}")

    return y_true, y_pred, mismatches

def save_report(report, cm_df, mismatches):
    """Saves the evaluation report to a markdown file."""
    with open('evaluation_report.md', 'w') as f:
        f.write("# Evaluation Report\n\n")
        
        f.write("## Classification Report\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```\n\n")
        
        f.write("## Confusion Matrix\n\n")
        f.write(cm_df.to_markdown())
        f.write("\n\n")
        
        f.write("## Mismatches\n\n")
        if not mismatches:
            f.write("No mismatches found.\n")
        else:
            for i, mismatch in enumerate(mismatches):
                f.write(f"### Mismatch {i+1}\n")
                f.write(f"- **Text**: {mismatch['text']}\n")
                f.write(f"- **Aspect**: {mismatch['aspect']}\n")
                f.write(f"- **Ground Truth**: `{mismatch['ground_truth']}`\n")
                f.write(f"- **Prediction**: `{mismatch['prediction']}`\n\n")

def main():
    """Main function to run the evaluation."""
    data = load_data('enrichment-agent/randd/data.json')
    unique_texts = get_unique_texts(data)
    
    # Get a complete list of all unique aspects from the data
    all_aspects = set(item['aspect'] for item in data)

    y_true, y_pred, mismatches = evaluate_model(unique_texts, all_aspects)

    if not y_true:
        logging.warning("No data to evaluate.")
        return

    # Generate and print the classification report
    labels = sorted(list(set(y_true + y_pred)))
    report = classification_report(y_true, y_pred, labels=labels, zero_division=0)
    print("Classification Report:")
    print(report)

    # Generate and print the confusion matrix
    print("Confusion Matrix:")
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print(cm_df)

    # Print some mismatches for qualitative analysis
    print("\n--- Mismatches ---")
    for i, mismatch in enumerate(mismatches[:10]): # Print first 10 mismatches
        print(f"Mismatch {i+1}:")
        print(f"  Text: {mismatch['text']}")
        print(f"  Aspect: {mismatch['aspect']}")
        print(f"  Ground Truth: {mismatch['ground_truth']}")
        print(f"  Prediction: {mismatch['prediction']}\n")

    save_report(report, cm_df, mismatches)
    logging.info("Evaluation report saved to evaluation_report.md")


if __name__ == "__main__":
    main() 