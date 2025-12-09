"""
Test to verify risk_calculator extraction works correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.shared.risk_calculator import compute_risk_level

def test_risk_calculator_basic():
    """Test basic risk calculation"""
    conversation = [
        {"speaker": "agent", "text": "Halo"},
        {"speaker": "customer", "text": "saya mau berhenti langganan"}
    ]
    
    base_prediction = {
        "probability": 20,
        "confidence": "RENDAH"
    }
    
    result = compute_risk_level(conversation, "telecollection", base_prediction)
    
    print("\n=== RISK CALCULATOR TEST ===")
    print(f"Risk Level: {result.get('risk_level')}")
    print(f"Risk Label: {result.get('risk_label')}")
    print(f"Risk Color: {result.get('risk_color')}")
    print(f"Signals: {result.get('signals', [])}")
    
    assert 'risk_level' in result
    assert 'risk_label' in result
    assert 'risk_color' in result
    assert 'signals' in result
    
    print("\n✓ Risk calculator extraction BERHASIL!")
    return True

def test_telecollection_service():
    """Test telecollection service using extracted risk_calculator"""
    from app.services import telecollection_services
    
    conversation = [
        {"speaker": "agent", "text": "Selamat pagi"},
        {"speaker": "customer", "text": "pagi"}
    ]
    
    result = telecollection_services.predict_outcome(conversation)
    
    print("\n=== TELECOLLECTION SERVICE TEST ===")
    print(f"Probability: {result.get('probability')}")
    print(f"Risk Level: {result.get('risk_level')}")
    print(f"Risk Label: {result.get('risk_label')}")
    
    assert 'probability' in result
    assert 'risk_level' in result
    assert 'risk_label' in result
    
    print("\n✓ Telecollection service integration BERHASIL!")
    return True

def test_winback_service():
    """Test winback service using extracted risk_calculator"""
    from app.services import winback_services
    
    conversation = [
        {"speaker": "agent", "text": "Selamat pagi"},
        {"speaker": "customer", "text": "pagi"}
    ]
    
    result = winback_services.predict_outcome(conversation)
    
    print("\n=== WINBACK SERVICE TEST ===")
    print(f"Probability: {result.get('probability')}")
    print(f"Risk Level: {result.get('risk_level')}")
    print(f"Risk Label: {result.get('risk_label')}")
    
    assert 'probability' in result
    assert 'risk_level' in result
    assert 'risk_label' in result
    
    print("\n✓ Winback service integration BERHASIL!")
    return True

def test_retention_service():
    """Test retention service using extracted risk_calculator"""
    from app.services import retention_services
    
    conversation = [
        {"speaker": "agent", "text": "Selamat pagi"},
        {"speaker": "customer", "text": "pagi"}
    ]
    
    result = retention_services.predict_outcome(conversation)
    
    print("\n=== RETENTION SERVICE TEST ===")
    print(f"Probability: {result.get('probability')}")
    print(f"Risk Level: {result.get('risk_level')}")
    print(f"Risk Label: {result.get('risk_label')}")
    
    assert 'probability' in result
    assert 'risk_level' in result
    assert 'risk_label' in result
    
    print("\n✓ Retention service integration BERHASIL!")
    return True

if __name__ == "__main__":
    print("="*60)
    print("TESTING RISK CALCULATOR EXTRACTION")
    print("="*60)
    
    try:
        test_risk_calculator_basic()
        test_telecollection_service()
        test_winback_service()
        test_retention_service()
        
        print("\n" + "="*60)
        print("SEMUA TEST BERHASIL! ✓")
        print("="*60)
        print("\nRisk calculator berhasil diekstrak ke shared/risk_calculator.py")
        print("Semua 3 service (telecollection, winback, retention) berhasil menggunakan modul baru!")
        
    except Exception as e:
        print(f"\n✗ TEST GAGAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
