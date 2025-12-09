#!/usr/bin/env python3
"""
🧹 CLEANUP & CONSOLIDATION PLAN untuk gpt_service.py

ANALISIS FUNCTION YANG BISA DIGABUNG/DIHAPUS:
1. Sentiment Analysis & Goal Validation - GABUNG
2. Prediction Functions - SIMPLIFY
3. Reason Generation - CONSOLIDATE
4. Duplicate Functions - REMOVE
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Function untuk menganalisis code structure
def analyze_gpt_service_functions():
    print("🔍 ANALYZING GPT_SERVICE.PY STRUCTURE")
    print("=" * 60)
    
    functions_found = []
    
    with open('backend/app/services/gpt_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            func_name = line.strip().split('(')[0].replace('def ', '')
            functions_found.append({
                'name': func_name,
                'line': i + 1,
                'signature': line.strip()
            })
    
    print(f"📊 Total Functions Found: {len(functions_found)}")
    print(f"\n🔧 Functions to Analyze:")
    
    # Group functions by category
    categories = {
        'sentiment_analysis': [],
        'goal_validation': [],
        'prediction': [],
        'reason_generation': [],
        'question_generation': [],
        'utilities': [],
        'other': []
    }
    
    for func in functions_found:
        name = func['name'].lower()
        if 'sentiment' in name or 'analyze' in name:
            categories['sentiment_analysis'].append(func)
        elif 'validate' in name or 'goal' in name:
            categories['goal_validation'].append(func)
        elif 'predict' in name or 'prediction' in name:
            categories['prediction'].append(func)
        elif 'reason' in name or 'enhance' in name:
            categories['reason_generation'].append(func)
        elif 'generate' in name or 'question' in name:
            categories['question_generation'].append(func)
        elif any(util in name for util in ['get_', 'save_', 'load_', 'format_']):
            categories['utilities'].append(func)
        else:
            categories['other'].append(func)
    
    for category, funcs in categories.items():
        if funcs:
            print(f"\n📁 {category.upper().replace('_', ' ')} ({len(funcs)} functions):")
            for func in funcs:
                print(f"   • {func['name']} (line {func['line']})")
    
    return categories

def generate_cleanup_recommendations():
    print(f"\n🧹 CLEANUP RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = [
        {
            "action": "CONSOLIDATE",
            "target": "Sentiment Analysis Functions",
            "description": "Gabung analyze_answer_sentiment + validate_goal_achievement",
            "benefit": "Reduce code duplication, single source of truth"
        },
        {
            "action": "SIMPLIFY", 
            "target": "Prediction Functions",
            "description": "Streamline telecollection prediction logic",
            "benefit": "Fix prediction accuracy issues mentioned by user"
        },
        {
            "action": "REMOVE",
            "target": "Duplicate Helper Functions", 
            "description": "Remove unused utility functions",
            "benefit": "Reduce file size and complexity"
        },
        {
            "action": "OPTIMIZE",
            "target": "Question Generation",
            "description": "Combine similar question generation methods",
            "benefit": "Cleaner question flow, less maintenance"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['action']} - {rec['target']}")
        print(f"   Description: {rec['description']}")
        print(f"   Benefit: {rec['benefit']}\n")

if __name__ == "__main__":
    print("🧹 GPT_SERVICE CLEANUP ANALYSIS")
    print("=" * 60)
    
    categories = analyze_gpt_service_functions()
    generate_cleanup_recommendations()
    
    print("🎯 NEXT STEPS:")
    print("1. Consolidate sentiment analysis + goal validation")
    print("2. Fix prediction logic for accuracy")
    print("3. Remove unused functions")
    print("4. Test consolidated functions")
    print("\n✅ Ready to start cleanup process!")