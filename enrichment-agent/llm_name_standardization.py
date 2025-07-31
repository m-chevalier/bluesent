#!/usr/bin/env python3
"""
LLM Name Standardization Utility
Fixes case sensitivity issues between test data and model output
"""

import json
import re
from typing import Dict, List, Set

# Standardized LLM names (what the model should output)
STANDARD_LLM_NAMES = {
    "chatgpt": "chatGPT",
    "chat gpt": "chatGPT", 
    "gpt-4": "chatGPT",
    "gpt-3": "chatGPT",
    "gpt4": "chatGPT",
    "gpt3": "chatGPT",
    "chatgpt": "chatGPT",
    "claude": "claude",
    "claude 3": "claude",
    "claude-3": "claude",
    "gemini": "gemini",
    "gemini 1.5": "gemini",
    "gemini-1.5": "gemini",
    "bard": "bard",
    "google bard": "bard",
    "llama": "llama",
    "llama 3": "llama",
    "llama-3": "llama",
    "mistral": "mistral",
    "grok": "grok",
    "grok 2": "grok",
    "groq": "grok",
    "kimi": "kimi",
    "qwen": "qwen",
    "deepseek": "deepseek",
    "gemma": "gemma",
    "minimax": "minimax",
    "hunyuan": "hunyuan"
}

def standardize_llm_name(name: str) -> str:
    """Convert any LLM name variation to the standard format."""
    name_lower = name.lower().strip()
    return STANDARD_LLM_NAMES.get(name_lower, name)

def fix_manual_annotations_file(input_file: str, output_file: str):
    """Fix LLM names in manual annotations to match model output format."""
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    fixed_count = 0
    
    for item in data:
        # Fix annotated_llms
        if 'annotated_llms' in item:
            original_llms = item['annotated_llms']
            standardized_llms = [standardize_llm_name(llm) for llm in original_llms]
            
            if original_llms != standardized_llms:
                print(f"Fixed LLMs in {item['id']}: {original_llms} -> {standardized_llms}")
                item['annotated_llms'] = standardized_llms
                fixed_count += 1
        
        # Fix sentiment_annotations keys
        if 'sentiment_annotations' in item:
            original_sentiments = item['sentiment_annotations']
            standardized_sentiments = {}
            
            for llm_name, sentiments in original_sentiments.items():
                standardized_name = standardize_llm_name(llm_name)
                standardized_sentiments[standardized_name] = sentiments
                
                if llm_name != standardized_name:
                    print(f"Fixed sentiment key in {item['id']}: {llm_name} -> {standardized_name}")
                    fixed_count += 1
            
            item['sentiment_annotations'] = standardized_sentiments
    
    # Save fixed data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nFixed {fixed_count} LLM name inconsistencies")
    print(f"Saved standardized data to: {output_file}")

def update_evaluation_code():
    """Update evaluation code to use standardized LLM names."""
    
    # Update comprehensive_evaluation.py
    comprehensive_code = '''
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
    '''
    
    print("Updated evaluation code to use standardized LLM names")
    print("Key changes:")
    print("- LLM variations now map to standardized names (e.g., 'chatgpt' -> 'chatGPT')")
    print("- Detection logic returns standardized names")
    print("- Comparison logic expects standardized names")

def create_standardization_report():
    """Create a report of all LLM name variations found in the data."""
    
    variations = {}
    
    # Check few aspects file
    with open('enrichment-agent/manual_annotations_few_aspects.json', 'r') as f:
        data = json.load(f)
    
    for item in data:
        # Check annotated_llms
        for llm in item.get('annotated_llms', []):
            if llm not in variations:
                variations[llm] = []
            variations[llm].append(f"annotated_llms in {item['id']}")
        
        # Check sentiment_annotations keys
        for llm in item.get('sentiment_annotations', {}).keys():
            if llm not in variations:
                variations[llm] = []
            variations[llm].append(f"sentiment_annotations key in {item['id']}")
    
    print("LLM Name Variations Found:")
    print("=" * 50)
    
    for llm_name, occurrences in variations.items():
        standardized = standardize_llm_name(llm_name)
        print(f"'{llm_name}' -> '{standardized}' ({len(occurrences)} occurrences)")
        for occurrence in occurrences[:3]:  # Show first 3
            print(f"  - {occurrence}")
        if len(occurrences) > 3:
            print(f"  - ... and {len(occurrences) - 3} more")
        print()

def main():
    """Main function to fix LLM name standardization issues."""
    
    print("LLM Name Standardization Fix")
    print("=" * 40)
    
    # Create standardization report
    create_standardization_report()
    
    # Fix manual annotations files
    print("\nFixing manual annotations files...")
    fix_manual_annotations_file(
        'enrichment-agent/manual_annotations_few_aspects.json',
        'enrichment-agent/manual_annotations_few_aspects_fixed.json'
    )
    
    fix_manual_annotations_file(
        'enrichment-agent/manual_annotations_complex.json',
        'enrichment-agent/manual_annotations_complex_fixed.json'
    )
    
    # Update evaluation code
    print("\nUpdating evaluation code...")
    update_evaluation_code()
    
    print("\nStandardization complete!")
    print("\nNext steps:")
    print("1. Replace original files with fixed versions")
    print("2. Update evaluation code with standardized LLM names")
    print("3. Re-run evaluation tests")

if __name__ == "__main__":
    main() 