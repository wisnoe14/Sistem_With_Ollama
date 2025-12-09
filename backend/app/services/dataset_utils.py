"""
Dataset utilities and constants for CS ML Chatbot modes.

This module re-exports dataset-related members from gpt_service to provide
stable import paths for callers, decoupling them from the monolithic module.
"""
from typing import Dict, List, Any

# Delegate to gpt_service for now to preserve behavior
from .gpt_service import (
    CS_DATASET as _CS_DATASET,
    CONVERSATION_GOALS as _CONVERSATION_GOALS,
    get_question_from_dataset as _get_question_from_dataset,
)

# Public re-exports
CS_DATASET = _CS_DATASET
CONVERSATION_GOALS = _CONVERSATION_GOALS


def get_question_from_dataset(mode: str) -> Dict[str, Any]:
    """Return the next dataset question for a given mode.
    Thin wrapper to keep a stable import path while we migrate logic.
    """
    return _get_question_from_dataset(mode)
