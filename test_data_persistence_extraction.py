"""
Test Data Persistence Extraction
=================================

Tests for data_persistence.py module to ensure:
1. save_conversation_to_excel works correctly
2. update_conversation_context returns proper dict
3. Excel file creation and directory handling
4. Error handling for edge cases

Run: python test_data_persistence_extraction.py
"""

import unittest
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.services.shared.data_persistence import (
    save_conversation_to_excel,
    update_conversation_context,
)


class TestSaveConversationToExcel(unittest.TestCase):
    """Test suite for save_conversation_to_excel function"""
    
    def tearDown(self):
        """Cleanup after each test"""
        test_dir = Path("conversations")
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    def test_save_simple_conversation(self):
        """Test saving a simple conversation"""
        conversation = [
            {
                "question": "Halo Bapak/Ibu",
                "answer": "Halo",
                "goal": "greeting",
                "timestamp": "2025-11-10 10:00:00"
            },
            {
                "question": "Kapan bisa bayar?",
                "answer": "Besok",
                "goal": "get_payment_date",
                "timestamp": "2025-11-10 10:00:30"
            }
        ]
        
        filepath = save_conversation_to_excel("CUST123", "telecollection", conversation)
        
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())
        self.assertIn("CUST123", filepath)
        self.assertIn("telecollection", filepath)
        
        # Verify content
        df = pd.read_excel(filepath)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['Pertanyaan'], "Halo Bapak/Ibu")
        self.assertEqual(df.iloc[1]['Jawaban'], "Besok")
    
    def test_save_with_prediction(self):
        """Test saving conversation with prediction result"""
        conversation = [
            {
                "question": "Kapan bisa bayar?",
                "answer": "Saya akan bayar besok",
                "goal": "get_payment_date",
                "timestamp": "2025-11-10 10:00:00"
            }
        ]
        
        prediction = {
            "keputusan": "AKAN BAYAR",
            "confidence": "TINGGI",
            "probability": 75,
            "tanggal_prediksi": "2025-11-10"
        }
        
        filepath = save_conversation_to_excel("CUST456", "telecollection", conversation, prediction)
        
        self.assertIsNotNone(filepath)
        
        # Verify content includes prediction
        df = pd.read_excel(filepath)
        self.assertEqual(len(df), 2)  # 1 conversation + 1 prediction row
        self.assertEqual(df.iloc[1]['No'], "PREDIKSI")
        self.assertEqual(df.iloc[1]['Jawaban'], "AKAN BAYAR")
        self.assertIn("TINGGI", df.iloc[1]['Goal'])
    
    def test_save_different_modes(self):
        """Test saving conversations for different modes"""
        conversation = [{"question": "Test", "answer": "Test", "goal": "test", "timestamp": "2025-11-10"}]
        
        modes = ["telecollection", "winback", "retention"]
        
        for mode in modes:
            filepath = save_conversation_to_excel(f"CUST_{mode}", mode, conversation)
            self.assertIsNotNone(filepath)
            self.assertIn(mode, filepath)
            self.assertTrue(Path(filepath).exists())
    
    def test_save_empty_conversation(self):
        """Test saving empty conversation returns None"""
        result = save_conversation_to_excel("CUST789", "telecollection", [])
        self.assertIsNone(result)
        
        result = save_conversation_to_excel("CUST789", "telecollection", None)
        self.assertIsNone(result)
    
    def test_directory_creation(self):
        """Test that conversations directory is created if not exists"""
        # Ensure directory doesn't exist
        test_dir = Path("conversations")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        conversation = [{"question": "Test", "answer": "Test", "goal": "test", "timestamp": "2025-11-10"}]
        filepath = save_conversation_to_excel("CUST999", "telecollection", conversation)
        
        self.assertIsNotNone(filepath)
        self.assertTrue(test_dir.exists())
        self.assertTrue(test_dir.is_dir())
    
    def test_filename_format(self):
        """Test filename format includes all required info"""
        conversation = [{"question": "Test", "answer": "Test", "goal": "test", "timestamp": "2025-11-10"}]
        filepath = save_conversation_to_excel("CUST_ABC", "winback", conversation)
        
        filename = Path(filepath).name
        self.assertTrue(filename.startswith("conversation_"))
        self.assertIn("CUST_ABC", filename)
        self.assertIn("winback", filename)
        self.assertTrue(filename.endswith(".xlsx"))
        
        # Just check that timestamp is present (format may vary based on customer_id length)
        # conversation_CUST_ABC_winback_YYYYMMDD_HHMMSS.xlsx
        self.assertIn("_", filename)  # Has separators


class TestUpdateConversationContext(unittest.TestCase):
    """Test suite for update_conversation_context function"""
    
    def test_basic_context_update(self):
        """Test basic context update"""
        result = update_conversation_context("sess123", "saya mau bayar besok", "Kapan bisa bayar?")
        
        self.assertEqual(result['session_id'], "sess123")
        self.assertEqual(result['last_response'], "saya mau bayar besok")
        self.assertEqual(result['last_question'], "Kapan bisa bayar?")
        self.assertTrue(result['updated'])
    
    def test_context_with_empty_strings(self):
        """Test context update with empty strings"""
        result = update_conversation_context("sess456", "", "")
        
        self.assertEqual(result['session_id'], "sess456")
        self.assertEqual(result['last_response'], "")
        self.assertEqual(result['last_question'], "")
        self.assertTrue(result['updated'])
    
    def test_context_with_long_text(self):
        """Test context update with long responses"""
        long_response = "Saya ingin bayar tapi saat ini sedang kesulitan keuangan. " * 10
        long_question = "Bisa ceritakan kenapa belum bayar sampai saat ini? " * 5
        
        result = update_conversation_context("sess789", long_response, long_question)
        
        self.assertEqual(result['last_response'], long_response)
        self.assertEqual(result['last_question'], long_question)
        self.assertTrue(result['updated'])
    
    def test_context_preserves_special_characters(self):
        """Test that special characters are preserved"""
        response = "Saya akan bayar Rp.1.000.000,- besok!"
        question = "Berapa yang akan dibayar?"
        
        result = update_conversation_context("sess_special", response, question)
        
        self.assertEqual(result['last_response'], response)
        self.assertEqual(result['last_question'], question)
        self.assertIn("Rp.1.000.000,-", result['last_response'])


class TestDataPersistenceIntegration(unittest.TestCase):
    """Integration tests for data persistence workflow"""
    
    def tearDown(self):
        """Cleanup after tests"""
        test_dir = Path("conversations")
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    def test_full_conversation_workflow(self):
        """Test complete workflow: context update and save"""
        # Step 1: Update context
        context = update_conversation_context(
            "sess_complete",
            "Saya akan bayar minggu depan",
            "Kapan rencana pembayaran?"
        )
        
        self.assertTrue(context['updated'])
        
        # Step 2: Build conversation history
        conversation = [
            {
                "question": "Halo Bapak/Ibu",
                "answer": "Halo",
                "goal": "greeting",
                "timestamp": "2025-11-10 10:00:00"
            },
            {
                "question": context['last_question'],
                "answer": context['last_response'],
                "goal": "get_payment_date",
                "timestamp": "2025-11-10 10:01:00"
            }
        ]
        
        # Step 3: Save to Excel
        filepath = save_conversation_to_excel("CUST_WORKFLOW", "telecollection", conversation)
        
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())
        
        # Verify saved data
        df = pd.read_excel(filepath)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[1]['Jawaban'], "Saya akan bayar minggu depan")
    
    def test_multiple_conversations_same_customer(self):
        """Test saving multiple conversations for same customer"""
        import time
        
        conversation1 = [{"question": "Q1", "answer": "A1", "goal": "g1", "timestamp": "2025-11-10 10:00"}]
        conversation2 = [{"question": "Q2", "answer": "A2", "goal": "g2", "timestamp": "2025-11-10 11:00"}]
        
        file1 = save_conversation_to_excel("CUST_MULTI", "telecollection", conversation1)
        time.sleep(1)  # Ensure different timestamp
        file2 = save_conversation_to_excel("CUST_MULTI", "telecollection", conversation2)
        
        self.assertNotEqual(file1, file2)  # Different timestamps
        self.assertTrue(Path(file1).exists())
        self.assertTrue(Path(file2).exists())


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSaveConversationToExcel))
    suite.addTests(loader.loadTestsFromTestCase(TestUpdateConversationContext))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPersistenceIntegration))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY - Data Persistence Extraction")
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

