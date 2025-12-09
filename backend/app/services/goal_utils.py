"""
Goal and answer utilities for CS ML Chatbot.

These wrappers provide stable imports for goal tracking and automatic answer
generation across modes, delegating to gpt_service for now.
"""
from typing import Dict, List, Any

from .gpt_service import (
    generate_automatic_customer_answer as _generate_automatic_customer_answer,
    check_conversation_goals_completed as _check_conversation_goals_completed,
    check_conversation_goals as _check_conversation_goals,
)


def generate_automatic_customer_answer(question: Dict[str, Any], mode: str | None = None, conversation: List[Dict[str, Any]] | None = None, topic: str | None = None) -> str:
    """Generate an automatic customer answer.
    Maintains the original signature compatibility by passing through args.
    """
    # Support both old (question, answer_mode, conversation, mode) and possible variations
    # We'll pass everything through and let core handle optional params
    if conversation is None:
        conversation = []
    # Some callers pass (question_result, answer_mode, conversation, mode)
    return _generate_automatic_customer_answer(question, mode, conversation, topic)


def check_conversation_goals_completed(mode_or_history, conversation_history: List[Dict[str, Any]] | None = None):
    """Evaluate goal achievement for a conversation.

    Backward-compatible signature:
    - New style: check_conversation_goals_completed(mode: str, conversation_history: list)
    - Old style: check_conversation_goals_completed(conversation_history: list)  # defaults to 'telecollection'
    """
    # Support old callers that only pass conversation_history
    if conversation_history is None and isinstance(mode_or_history, list):
        mode = "telecollection"
        conv = mode_or_history
    else:
        mode = mode_or_history
        conv = conversation_history or []

    return _check_conversation_goals_completed(mode, conv)


def check_conversation_goals(conversation_history: List[Dict[str, Any]], mode: str = "telecollection") -> Dict[str, Any]:
    """Comprehensive goal checking using the core engine (preferred).

    Defaults to telecollection mode for backward-compatible single-arg usage patterns in tests.
    """
    return _check_conversation_goals(conversation_history, mode)
