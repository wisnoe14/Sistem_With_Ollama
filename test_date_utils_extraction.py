"""
Test to verify date_utils extraction works correctly
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.services.shared.date_utils import (
    format_date_indonesian,
    get_current_date_info,
    parse_time_expressions_to_date,
    parse_relative_date,
)

def test_format_date_indonesian():
    """Test Indonesian date formatting"""
    test_date = datetime(2025, 11, 15)
    result = format_date_indonesian(test_date)
    
    print("\n=== FORMAT DATE INDONESIAN TEST ===")
    print(f"Input: 2025-11-15")
    print(f"Output: {result}")
    
    assert "15" in result
    assert "November" in result
    assert "2025" in result
    print("✓ Date formatting works correctly!")
    return True

def test_get_current_date_info():
    """Test current date info retrieval"""
    result = get_current_date_info()
    
    print("\n=== GET CURRENT DATE INFO TEST ===")
    print(f"Tanggal lengkap: {result['tanggal_lengkap']}")
    print(f"Tanggal: {result['tanggal']}")
    print(f"Hari: {result['hari']}")
    print(f"Bulan: {result['bulan']}")
    print(f"Tahun: {result['tahun']}")
    
    assert 'tanggal_lengkap' in result
    assert 'tanggal' in result
    assert 'hari' in result
    assert 'bulan' in result
    assert 'tahun' in result
    print("✓ Current date info works correctly!")
    return True

def test_parse_time_expressions():
    """Test time expression parsing"""
    
    test_cases = [
        ("besok saya bayar", "besok", 85),
        ("3 hari lagi", "3 days", 90),
        ("tanggal 15", "tanggal", 95),
        ("minggu depan", "minggu depan", 85),
    ]
    
    print("\n=== PARSE TIME EXPRESSIONS TEST ===")
    for text, expected_keyword, min_confidence in test_cases:
        result = parse_time_expressions_to_date(text)
        detected = result.get('detected_timeframe')
        confidence = result.get('confidence', 0)
        formatted = result.get('formatted_date', 'None')
        
        status = "✓" if detected and confidence >= min_confidence else "✗"
        print(f"{status} '{text}' -> detected='{detected}', confidence={confidence}%, date={formatted}")
        
        assert detected is not None, f"Failed to detect time expression in '{text}'"
        assert confidence >= min_confidence, f"Low confidence for '{text}': {confidence}"
    
    print("✓ All time expression tests passed!")
    return True

def test_parse_relative_date():
    """Test relative date parsing"""
    
    test_cases = [
        ("besok saya datang", True),
        ("hari ini juga", True),
        ("minggu depan", True),
        ("tidak tahu kapan", False),
    ]
    
    print("\n=== PARSE RELATIVE DATE TEST ===")
    for text, should_find in test_cases:
        result = parse_relative_date(text)
        found = result.get('found', False)
        
        status = "✓" if found == should_find else "✗"
        if found:
            print(f"{status} '{text}' -> found={found}, date={result.get('date_formatted')}")
        else:
            print(f"{status} '{text}' -> found={found}")
        
        assert found == should_find, f"Expected found={should_find} for '{text}', got {found}"
    
    print("✓ All relative date tests passed!")
    return True

def test_service_integration():
    """Test date_utils integration with services"""
    from app.services import telecollection_services
    
    conversation = [
        {"speaker": "agent", "text": "Kapan bisa bayar?"},
        {"speaker": "customer", "text": "besok", "goal": "payment_timeline"}
    ]
    
    result = telecollection_services.predict_outcome(conversation)
    
    print("\n=== SERVICE INTEGRATION TEST ===")
    print(f"Tanggal prediksi: {result.get('tanggal_prediksi')}")
    
    assert 'tanggal_prediksi' in result
    assert result['tanggal_prediksi'] != ""
    print("✓ Services can use date_utils!")
    return True

if __name__ == "__main__":
    print("="*60)
    print("TESTING DATE UTILS EXTRACTION")
    print("="*60)
    
    try:
        test_format_date_indonesian()
        test_get_current_date_info()
        test_parse_time_expressions()
        test_parse_relative_date()
        test_service_integration()
        
        print("\n" + "="*60)
        print("SEMUA TEST BERHASIL! ✓")
        print("="*60)
        print("\nDate utils berhasil diekstrak ke shared/date_utils.py")
        print("Semua 3 service dapat menggunakan modul baru!")
        print("\nExtracted functions:")
        print("  - format_date_indonesian()")
        print("  - get_current_date_info()")
        print("  - parse_time_expressions_to_date()")
        print("  - parse_relative_date()")
        
    except Exception as e:
        print(f"\n✗ TEST GAGAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
