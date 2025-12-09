import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

# Test imports
try:
    from app.services.shared.ollama_client import (
        check_ollama_models,
        warmup_ollama_model,
        ask_llama3_chat,
        generate_reason_with_ollama,
        get_ollama_performance_report,
        OLLAMA_STATS,
    )
    print("✓ All ollama_client functions imported successfully")
    
    # Test that OLLAMA_STATS exists
    print(f"✓ OLLAMA_STATS initialized: {OLLAMA_STATS}")
    
    # Test report function
    report = get_ollama_performance_report()
    print(f"✓ Performance report (no calls): {report}")
    
    print("\n" + "="*60)
    print("OLLAMA CLIENT MODULE EXTRACTION - BASIC TEST PASSED")
    print("="*60)
    print("Module: backend/app/services/shared/ollama_client.py")
    print("Functions: 5/5 imported successfully")
    print("Stats tracking: Working")
    print("="*60)
    
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
