#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test import semua fungsi dari gpt_service.py
"""

import sys
import os

# Add backend to path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

print("Testing imports from gpt_service.py...")

try:
    from app.services.gpt_service import (
        generate_question,
        save_conversation_to_excel,
        predict_status_promo_ollama,
        predict_status_promo_svm,
        predict_status_promo_lda,
        get_current_date_info,
        parse_relative_date,
        get_question_from_dataset,
        generate_automatic_customer_answer,
        check_conversation_goals_completed,
        generate_final_prediction,
        CS_DATASET,
        CONVERSATION_GOALS,
        get_ollama_performance_report
    )
    
    print("✅ ALL IMPORTS SUCCESSFUL!")
    print(f"✅ CS_DATASET keys: {list(CS_DATASET.keys())}")
    print(f"✅ CONVERSATION_GOALS keys: {list(CONVERSATION_GOALS.keys())}")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"❌ OTHER ERROR: {e}")
    import traceback
    traceback.print_exc()