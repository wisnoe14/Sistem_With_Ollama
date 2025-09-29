import json
import os
from typing import Dict, List, Optional
import random

class ConversationDataset:
    def __init__(self):
        self.data = self._load_dataset()
    
    def _load_dataset(self) -> Dict:
        """Load conversation flows from JSON file"""
        dataset_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'conversation_flows.json')
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Dataset file not found: {dataset_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing dataset JSON: {e}")
            return {}
    
    def get_question(self, flow_type: str, step: str, substep: str = None, **kwargs) -> Dict:
        """
        Get question and options from dataset
        
        Args:
            flow_type: 'telecollection', 'winback', 'retention'
            step: main step like 'opening', 'payment_info', etc.
            substep: optional substep like 'already_paid', 'not_paid'
            **kwargs: variables for string formatting like agent_name, customer_name
        
        Returns:
            Dict with 'question' and 'options' keys
        """
        try:
            if flow_type not in self.data:
                return self._default_response()
            
            flow_data = self.data[flow_type]
            
            if substep:
                question_data = flow_data.get(step, {}).get(substep, {})
            else:
                question_data = flow_data.get(step, {})
            
            if not question_data:
                return self._default_response()
            
            # Format question with provided variables
            question = question_data.get("question", "")
            if kwargs:
                question = question.format(**kwargs)
            
            return {
                "question": question,
                "options": question_data.get("options", ["OK", "Lanjutkan"])
            }
            
        except Exception as e:
            print(f"Error getting question: {e}")
            return self._default_response()
    
    def get_keywords(self, keyword_type: str) -> List[str]:
        """Get keywords for matching user responses"""
        return self.data.get("keywords", {}).get(keyword_type, [])
    
    def check_keyword_match(self, user_answer: str, keyword_type: str) -> bool:
        """Check if user answer matches any keyword in the specified type"""
        keywords = self.get_keywords(keyword_type)
        user_answer_lower = user_answer.lower().strip()
        return any(kw in user_answer_lower for kw in keywords)
    
    def _default_response(self) -> Dict:
        """Default response when data not found"""
        return {
            "question": "Terima kasih atas informasinya. Ada yang bisa kami bantu lagi?",
            "options": ["Ya", "Tidak", "Selesai"]
        }
    
    def get_random_variation(self, flow_type: str, step: str, substep: str = None) -> Dict:
        """Get random variation of question if multiple versions exist"""
        # This can be extended to support multiple variations per step
        return self.get_question(flow_type, step, substep)

# Global instance
conversation_dataset = ConversationDataset()