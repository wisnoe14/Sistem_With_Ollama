"""
Test Ollama Client Extraction
==============================

Tests for ollama_client.py module to ensure:
1. Model availability checking works
2. Warmup mechanism functions correctly
3. Chat completion handles errors gracefully
4. Reason generation with fallbacks
5. Performance tracking is accurate

Note: These are mock-based tests since Ollama server may not be running.

Run: python test_ollama_client_extraction.py
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.services.shared.ollama_client import (
    check_ollama_models,
    warmup_ollama_model,
    ask_llama3_chat,
    generate_reason_with_ollama,
    get_ollama_performance_report,
    OLLAMA_STATS,
)


class TestCheckOllamaModels(unittest.TestCase):
    """Test suite for check_ollama_models function"""
    
    def setUp(self):
        """Reset global state before each test"""
        import app.services.shared.ollama_client as ollama_module
        ollama_module._OLLAMA_AVAILABLE_MODELS = None
    
    @patch('app.services.shared.ollama_client.requests.get')
    def test_check_models_success(self, mock_get):
        """Test successful model check"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3:latest"},
                {"name": "llama2:7b"},
            ]
        }
        mock_get.return_value = mock_response
        
        models = check_ollama_models()
        
        self.assertIn("llama3", models)
        self.assertIn("llama2", models)
        self.assertEqual(len(models), 2)
    
    @patch('app.services.shared.ollama_client.requests.get')
    def test_check_models_cached(self, mock_get):
        """Test that models are cached after first call"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama3:latest"}]}
        mock_get.return_value = mock_response
        
        # First call
        models1 = check_ollama_models()
        # Second call (should use cache)
        models2 = check_ollama_models()
        
        self.assertEqual(models1, models2)
        self.assertEqual(mock_get.call_count, 1)  # Only called once
    
    @patch('app.services.shared.ollama_client.requests.get')
    def test_check_models_server_error(self, mock_get):
        """Test handling of server errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        models = check_ollama_models()
        
        self.assertEqual(models, [])
    
    @patch('app.services.shared.ollama_client.requests.get')
    def test_check_models_connection_error(self, mock_get):
        """Test handling of connection errors"""
        mock_get.side_effect = Exception("Connection refused")
        
        models = check_ollama_models()
        
        self.assertEqual(models, [])


class TestWarmupOllamaModel(unittest.TestCase):
    """Test suite for warmup_ollama_model function"""
    
    def setUp(self):
        """Reset warmup state"""
        import app.services.shared.ollama_client as ollama_module
        ollama_module._OLLAMA_WARMED_UP = False
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_warmup_success(self, mock_post):
        """Test successful warmup"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = warmup_ollama_model("llama3")
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_warmup_already_warmed(self, mock_post):
        """Test that warmup skips if already warmed"""
        import app.services.shared.ollama_client as ollama_module
        ollama_module._OLLAMA_WARMED_UP = True
        
        result = warmup_ollama_model("llama3")
        
        self.assertTrue(result)
        mock_post.assert_not_called()
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_warmup_failure(self, mock_post):
        """Test warmup failure handling"""
        mock_post.side_effect = Exception("Connection error")
        
        result = warmup_ollama_model("llama3")
        
        self.assertFalse(result)


class TestAskLlama3Chat(unittest.TestCase):
    """Test suite for ask_llama3_chat function"""
    
    def setUp(self):
        """Reset state"""
        import app.services.shared.ollama_client as ollama_module
        ollama_module._OLLAMA_AVAILABLE_MODELS = ["llama3"]
        ollama_module._OLLAMA_WARMED_UP = True
        ollama_module.OLLAMA_STATS = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_response_time": 0.0,
            "quality_scores": []
        }
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_chat_success(self, mock_post):
        """Test successful chat completion"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Hello, how can I help you?"}
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hi"}]
        response = ask_llama3_chat(messages)
        
        self.assertEqual(response, "Hello, how can I help you?")
        self.assertEqual(OLLAMA_STATS["successful_calls"], 1)
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_chat_timeout(self, mock_post):
        """Test timeout handling"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        messages = [{"role": "user", "content": "Hi"}]
        response = ask_llama3_chat(messages)
        
        self.assertEqual(response, "")
        self.assertEqual(OLLAMA_STATS["failed_calls"], 1)
    
    @patch('app.services.shared.ollama_client.check_ollama_models')
    def test_chat_no_models_available(self, mock_check):
        """Test behavior when no models available"""
        mock_check.return_value = []
        
        messages = [{"role": "user", "content": "Hi"}]
        response = ask_llama3_chat(messages)
        
        self.assertEqual(response, "")
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_chat_server_error(self, mock_post):
        """Test server error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hi"}]
        response = ask_llama3_chat(messages)
        
        self.assertEqual(response, "")
        self.assertEqual(OLLAMA_STATS["failed_calls"], 1)


class TestGenerateReasonWithOllama(unittest.TestCase):
    """Test suite for generate_reason_with_ollama function"""
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_generate_reason_telecollection(self, mock_post):
        """Test reason generation for telecollection mode"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Customer menunjukkan komitmen pembayaran yang jelas dengan menyebutkan tanggal spesifik."}
        }
        mock_post.return_value = mock_response
        
        conversation = [
            {"q": "Kapan bisa bayar?", "a": "Besok saya akan bayar"}
        ]
        analysis = {"timeline_commitments": True, "barriers": [], "cooperation_level": 80}
        
        reason = generate_reason_with_ollama(conversation, "telecollection", "AKAN BAYAR", analysis)
        
        self.assertGreater(len(reason), 50)
        self.assertIn("komitmen", reason.lower())
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_generate_reason_winback(self, mock_post):
        """Test reason generation for winback mode"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Customer menunjukkan minat untuk reaktivasi dengan respons positif terhadap penawaran promo."}
        }
        mock_post.return_value = mock_response
        
        conversation = [
            {"q": "Mau kembali pakai layanan?", "a": "Mau, kalau ada promo"}
        ]
        analysis = {"interest_score": 75, "commitment_score": 60, "objection_count": 0}
        
        reason = generate_reason_with_ollama(conversation, "winback", "TERTARIK REAKTIVASI", analysis)
        
        self.assertGreater(len(reason), 50)
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_generate_reason_retention(self, mock_post):
        """Test reason generation for retention mode"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Customer menunjukkan kepuasan dengan layanan dan tertarik dengan paket upgrade."}
        }
        mock_post.return_value = mock_response
        
        conversation = [
            {"q": "Mau upgrade paket?", "a": "Boleh, saya tertarik"}
        ]
        analysis = {}
        
        reason = generate_reason_with_ollama(conversation, "retention", "AKAN LANJUT", analysis)
        
        self.assertGreater(len(reason), 50)
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_generate_reason_fallback_on_timeout(self, mock_post):
        """Test fallback when Ollama times out"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        conversation = [{"q": "Test", "a": "Test"}]
        reason = generate_reason_with_ollama(conversation, "telecollection", "AKAN BAYAR", {})
        
        # Should return fallback text
        self.assertGreater(len(reason), 0)
        self.assertIn("akan bayar", reason.lower())
    
    @patch('app.services.shared.ollama_client.requests.post')
    def test_generate_reason_fallback_on_invalid_response(self, mock_post):
        """Test fallback when response is too short"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "OK"}  # Too short
        }
        mock_post.return_value = mock_response
        
        conversation = [{"q": "Test", "a": "Test"}]
        reason = generate_reason_with_ollama(conversation, "telecollection", "AKAN BAYAR", {})
        
        # Should return fallback text
        self.assertGreater(len(reason), 0)


class TestOllamaPerformanceReport(unittest.TestCase):
    """Test suite for get_ollama_performance_report function"""
    
    def test_report_no_calls(self):
        """Test report when no calls made"""
        import app.services.shared.ollama_client as ollama_module
        ollama_module.OLLAMA_STATS = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_response_time": 0.0,
            "quality_scores": []
        }
        
        report = get_ollama_performance_report()
        
        self.assertIn("status", report)
        self.assertIn("No Ollama calls", report["status"])
    
    def test_report_with_calls(self):
        """Test report with actual calls"""
        import app.services.shared.ollama_client as ollama_module
        ollama_module.OLLAMA_STATS = {
            "total_calls": 10,
            "successful_calls": 8,
            "failed_calls": 2,
            "avg_response_time": 1.5,
            "quality_scores": [0.8, 0.9, 0.7]
        }
        
        report = get_ollama_performance_report()
        
        self.assertIn("total_calls", report)
        self.assertEqual(report["total_calls"], 10)
        self.assertIn("success_rate", report)
        self.assertIn("80.0%", report["success_rate"])
        self.assertIn("recommendation", report)


def run_tests():
    """Run all tests with detailed output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCheckOllamaModels))
    suite.addTests(loader.loadTestsFromTestCase(TestWarmupOllamaModel))
    suite.addTests(loader.loadTestsFromTestCase(TestAskLlama3Chat))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateReasonWithOllama))
    suite.addTests(loader.loadTestsFromTestCase(TestOllamaPerformanceReport))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY - Ollama Client Extraction")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
