import json
import os
from typing import Dict, List, Optional, Union

def load_conversation_flows(file_path: str = "app/dataset/conversation_flows.json") -> Dict:
    """
    Load conversation flows from JSON file
    
    Args:
        file_path: Path to the conversation flows JSON file
        
    Returns:
        Dictionary containing conversation flows
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"Warning: Conversation flows file not found at {file_path}")
            return {}
    except Exception as e:
        print(f"Error loading conversation flows: {str(e)}")
        return {}

def get_flow_structure(topic: str, flows: Dict = None) -> Dict:
    """
    Get the structure of a specific conversation flow
    
    Args:
        topic: The topic/flow name
        flows: Pre-loaded flows dictionary (optional)
        
    Returns:
        Dictionary containing the flow structure
    """
    if flows is None:
        flows = load_conversation_flows()
    
    return flows.get(topic, {})

def get_available_topics(flows: Dict = None) -> List[str]:
    """
    Get list of available conversation topics
    
    Args:
        flows: Pre-loaded flows dictionary (optional)
        
    Returns:
        List of available topic names
    """
    if flows is None:
        flows = load_conversation_flows()
    
    return list(flows.keys())

def validate_flow_structure(flow: Dict) -> bool:
    """
    Validate if a conversation flow has proper structure
    
    Args:
        flow: Dictionary containing flow data
        
    Returns:
        Boolean indicating if structure is valid
    """
    if not isinstance(flow, dict):
        return False
    
    # Check if flow has required keys
    required_keys = ["opening"]  # At minimum should have opening
    for key in required_keys:
        if key not in flow:
            return False
    
    return True

def find_question_by_id(topic: str, question_id: str, flows: Dict = None) -> Optional[Dict]:
    """
    Find a specific question by its ID within a topic
    
    Args:
        topic: The topic/flow name
        question_id: The question ID to find
        flows: Pre-loaded flows dictionary (optional)
        
    Returns:
        Dictionary containing question data or None if not found
    """
    if flows is None:
        flows = load_conversation_flows()
    
    flow = flows.get(topic, {})
    
    # Search in all sections of the flow
    for section_key, section in flow.items():
        if isinstance(section, dict):
            # Direct question object
            if section.get("id") == question_id:
                return section
            
            # Questions list
            if "questions" in section:
                for question in section["questions"]:
                    if question.get("id") == question_id:
                        return question
            
            # Nested questions
            for key, value in section.items():
                if isinstance(value, dict) and value.get("id") == question_id:
                    return value
    
    return None

def get_next_question_id(topic: str, current_id: str, selected_option: str = None, flows: Dict = None) -> Optional[str]:
    """
    Get the next question ID based on current question and selected option
    
    Args:
        topic: The topic/flow name
        current_id: Current question ID
        selected_option: The option selected by user
        flows: Pre-loaded flows dictionary (optional)
        
    Returns:
        Next question ID or None if conversation should end
    """
    if flows is None:
        flows = load_conversation_flows()
    
    current_question = find_question_by_id(topic, current_id, flows)
    if not current_question:
        return None
    
    # Check if there's next question logic
    if "next" in current_question:
        next_logic = current_question["next"]
        
        # If selected option maps to specific next question
        if selected_option and selected_option in next_logic:
            return next_logic[selected_option]
        
        # Default next question
        if "default" in next_logic:
            return next_logic["default"]
    
    return None

def format_question_for_customer(question_data: Dict, customer_name: str = "", agent_name: str = "CS ICONNET") -> Dict:
    """
    Format question by replacing placeholders with actual values
    
    Args:
        question_data: Dictionary containing question data
        customer_name: Customer's name
        agent_name: Agent's name
        
    Returns:
        Formatted question data
    """
    formatted_data = question_data.copy()
    
    if "question" in formatted_data:
        question = formatted_data["question"]
        question = question.replace("{customer_name}", customer_name)
        question = question.replace("{agent_name}", agent_name)
        formatted_data["question"] = question
    
    return formatted_data

def get_conversation_summary(conversation: List[Dict]) -> str:
    """
    Generate a summary of the conversation for prediction purposes
    
    Args:
        conversation: List of conversation exchanges
        
    Returns:
        String summary of the conversation
    """
    summary_parts = []
    
    for i, exchange in enumerate(conversation):
        if "question" in exchange:
            summary_parts.append(f"Q{i+1}: {exchange['question']}")
        if "answer" in exchange:
            summary_parts.append(f"A{i+1}: {exchange['answer']}")
    
    return "\n".join(summary_parts)

def extract_keywords_from_conversation(conversation: List[Dict]) -> List[str]:
    """
    Extract keywords from conversation for analysis
    
    Args:
        conversation: List of conversation exchanges
        
    Returns:
        List of extracted keywords
    """
    keywords = []
    
    # Common positive/negative indicators for telecollection
    positive_keywords = ["sudah bayar", "akan bayar", "hari ini", "besok", "berminat", "lanjut", "ya", "bisa"]
    negative_keywords = ["belum bayar", "tidak bisa", "tidak berminat", "berhenti", "tidak", "kesulitan", "tidak mampu"]
    
    conversation_text = get_conversation_summary(conversation).lower()
    
    for keyword in positive_keywords:
        if keyword in conversation_text:
            keywords.append(f"positive:{keyword}")
    
    for keyword in negative_keywords:
        if keyword in conversation_text:
            keywords.append(f"negative:{keyword}")
    
    return keywords

def calculate_conversation_score(conversation: List[Dict]) -> float:
    """
    Calculate a simple score based on conversation sentiment
    
    Args:
        conversation: List of conversation exchanges
        
    Returns:
        Float score between 0.0 and 1.0
    """
    keywords = extract_keywords_from_conversation(conversation)
    
    positive_count = len([k for k in keywords if k.startswith("positive:")])
    negative_count = len([k for k in keywords if k.startswith("negative:")])
    
    total_keywords = positive_count + negative_count
    
    if total_keywords == 0:
        return 0.5  # Neutral
    
    return positive_count / total_keywords
