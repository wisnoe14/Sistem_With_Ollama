"""
Shared utility functions used across modes and API endpoints.

This module provides stable import paths for common helpers so we can
decouple API code from the monolithic gpt_service implementation over time.

Currently these functions are thin wrappers around gpt_service to avoid behavior changes.
They can be migrated to standalone implementations incrementally without touching callers.
"""
from typing import Dict, List, Any

# For now, delegate to the core module to preserve behavior
from .gpt_service import (
    get_current_date_info as _get_current_date_info,
    save_conversation_to_excel as _save_conversation_to_excel,
    parse_relative_date as _parse_relative_date,
    get_ollama_performance_report as _get_ollama_performance_report,
)


def get_current_date_info() -> Dict:
    """Return current date/time information in a normalized dict format.
    Wrapper to keep stable import path for API callers.
    """
    return _get_current_date_info()


def save_conversation_to_excel(
    customer_id: str,
    mode: str = "telecollection",
    conversation: List[Dict[str, Any]] | None = None,
    prediction: Dict[str, Any] | None = None,
) -> None:
    """Persist conversation + optional prediction to an Excel log.
    Wrapper to keep stable import path for API callers.
    """
    return _save_conversation_to_excel(customer_id, mode, conversation or [], prediction or {})


def parse_relative_date(text: str) -> Dict:
    """Parse Indonesian relative date expressions into concrete dates.
    Wrapper to keep stable import path for API callers.
    """
    return _parse_relative_date(text)


def get_ollama_performance_report() -> Dict:
    """Return performance/accuracy metrics for Ollama-backed generation.
    Wrapper to keep stable import path for API callers.
    """
    return _get_ollama_performance_report()
