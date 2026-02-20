"""
Conversation flows loader - loads the new decision tree structure from JSON
"""
import json
import os
from typing import Dict, List, Any, Optional

class ConversationFlowsLoader:
    """Load and manage conversation flows from JSON"""
    
    _instance = None
    _data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load(cls) -> Dict[str, Any]:
        """Load conversation flows JSON file"""
        if cls._data is None:
            json_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "dataset",
                "conversation_flows.json"
            )
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    cls._data = json.load(f)
                print(f"✅ Conversation flows loaded from {json_path}")
                print(f"   Modes available: {list(cls._data.keys())}")
                for mode in cls._data.keys():
                    node_count = len(cls._data.get(mode, {}))
                    print(f"   - {mode}: {node_count} nodes")
            except FileNotFoundError:
                print(f"❌ Conversation flows JSON not found at {json_path}")
                cls._data = {}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing conversation flows JSON: {e}")
                cls._data = {}
        
        return cls._data
    
    @classmethod
    def get_question(cls, mode: str, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific question by mode and question_id"""
        data = cls.load()
        
        if mode not in data:
            print(f"⚠️  Mode '{mode}' not found in conversation flows")
            return None
        
        if question_id not in data[mode]:
            print(f"⚠️  Question ID '{question_id}' not found in {mode}")
            return None
        
        question_node = data[mode][question_id]
        # Ensure question_id is always included for routing
        if not isinstance(question_node, dict):
            return None
        
        # Always make a copy to avoid modifying the original cached data
        result = question_node.copy()
        
        # Add question_id if not present or different
        result["question_id"] = question_id
        
        # Ensure options are in correct format (objects with text and next_question)
        if 'options' in result and result['options']:
            options = result['options']
            # If options are strings (old format), return as-is for backwards compatibility
            # If options are objects (new format), they're already correct
            if isinstance(options[0], dict):
                # New format - ensure all required fields are present
                formatted_options = []
                for opt in options:
                    formatted_options.append({
                        'text': opt.get('text', ''),
                        'next_question': opt.get('next_question', ''),
                        'action': opt.get('action', '')  # Optional
                    })
                result['options'] = formatted_options
        
        return result
    
    @classmethod
    def determine_next_question(
        cls, 
        mode: str, 
        conversation_history: List[Dict],
        last_answer: str
    ) -> Optional[str]:
        """
        Determine next question ID based on conversation history and last answer
        This uses the new decision tree structure with explicit routing
        """
        data = cls.load()
        
        if mode not in data:
            return None
        
        if not conversation_history:
            # Start with opening node
            mode_data = data.get(mode, {})
            if 'opening' in mode_data:
                return 'opening'
            # Fallback to first node if no opening
            return next(iter(mode_data.keys())) if mode_data else None
        
        # Get the current question ID from conversation history
        current_question_id = None
        if conversation_history:
            last_entry = conversation_history[-1]
            current_question_id = last_entry.get('question_id')
            print(f"   🔍 Last entry: question_id={current_question_id}, keys={list(last_entry.keys())}")
        
        if not current_question_id:
            print(f"   ⚠️  No current_question_id found in history")
            return None
        
        # Get the current question node
        current_node = cls.get_question(mode, current_question_id)
        if not current_node:
            return None
        
        # Get options and match with last_answer to find next_question
        options = current_node.get('options', [])
        
        if not options:
            # No options = closing node
            return None
        
        # Find matching option
        last_answer_lower = (last_answer or "").lower().strip()
        
        for option in options:
            if isinstance(option, dict):
                # New format
                option_text = (option.get('text', '') or "").lower().strip()
                if option_text == last_answer_lower or last_answer_lower in option_text:
                    return option.get('next_question')
            else:
                # Old format (backwards compatibility)
                option_text = (option or "").lower().strip()
                if option_text == last_answer_lower or last_answer_lower in option_text:
                    # Can't determine next from old format
                    return None
        
        # If no exact match found, try partial matching for new format  
        for option in options:
            if isinstance(option, dict):
                option_text = (option.get('text', '') or "").lower().strip()
                # Try partial match (at least 60% of words match)
                last_words = set(last_answer_lower.split())
                option_words = set(option_text.split())
                if last_words and option_words:
                    similarity = len(last_words & option_words) / max(len(last_words), len(option_words))
                    if similarity > 0.4:  # 40% match threshold
                        return option.get('next_question')
        
        # Fallback: if still no match, might want to return first option or None
        if options and isinstance(options[0], dict):
            return options[0].get('next_question')
        
        return None
    
    @classmethod
    def get_opening_question(cls, mode: str) -> Optional[Dict[str, Any]]:
        """Get the opening (first) question for a mode"""
        opening_id = 'opening'
        return cls.get_question(mode, opening_id)
    
    @classmethod
    def list_all_nodes(cls, mode: str) -> List[str]:
        """List all question node IDs for a mode"""
        data = cls.load()
        if mode not in data:
            return []
        return list(data[mode].keys())
    
    @classmethod
    def reload(cls):
        """Force reload the conversation flows from disk"""
        cls._data = None
        return cls.load()


def get_flows_loader() -> ConversationFlowsLoader:
    """Get singleton instance of conversation flows loader"""
    return ConversationFlowsLoader()
