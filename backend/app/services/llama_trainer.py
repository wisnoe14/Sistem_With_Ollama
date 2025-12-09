"""
🤖 Llama3 Training Data Loader
Load CSV training data untuk Llama3 few-shot learning
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict

def load_training_examples_from_csv(csv_path: str, mode: str = "telecollection") -> List[Dict]:
    """
    Load contoh percakapan dari CSV untuk few-shot learning
    
    Args:
        csv_path: Path ke file CSV training data
        mode: Mode (telecollection/winback)
    
    Returns:
        List of conversation examples
    """
    try:
        df = pd.read_csv(csv_path)
        
        examples = []
        for _, row in df.iterrows():
            if 'goal' in df.columns and 'question' in df.columns and 'answer' in df.columns:
                example = {
                    "goal": row.get('goal', ''),
                    "question": row.get('question', ''),
                    "answer": row.get('answer', ''),
                    "context": row.get('context', '')
                }
                examples.append(example)
        
        print(f"[TRAINING DATA] Loaded {len(examples)} examples from {csv_path}")
        return examples
        
    except Exception as e:
        print(f"[TRAINING DATA ERROR] {str(e)}")
        return []

def format_few_shot_examples(examples: List[Dict], goal: str = None) -> str:
    """
    Format examples menjadi few-shot prompt string
    
    Args:
        examples: List of training examples
        goal: Filter by specific goal (optional)
    
    Returns:
        Formatted string untuk prompt
    """
    if goal:
        examples = [ex for ex in examples if ex.get('goal') == goal]
    
    # Ambil maksimal 3 examples
    examples = examples[:3]
    
    formatted = "\n\nCONTOH PERCAKAPAN YANG BAIK:\n"
    for i, ex in enumerate(examples, 1):
        formatted += f"\nContoh {i}:\n"
        if ex.get('context'):
            formatted += f"Konteks: {ex['context']}\n"
        formatted += f"CS: {ex['question']}\n"
        formatted += f"Customer: {ex['answer']}\n"
    
    return formatted

def get_training_data_path(mode: str = "telecollection") -> Path:
    """Get path to training data CSV"""
    base_path = Path(__file__).parent.parent / "dataset"
    
    training_files = {
        "telecollection": base_path / "telecollection_training.csv",
        "winback": base_path / "winback_training.csv"
    }
    
    return training_files.get(mode, base_path / "training_data.csv")
