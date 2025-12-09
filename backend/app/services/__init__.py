"""
Services package aggregator.

Provides convenient imports for mode-specific service modules and shared utils.
"""

from . import (
    telecollection_services,
    winback_services,
    retention_services,
    dataset_utils,
    goal_utils,
    shared_utils,
)

__all__ = [
	"telecollection_services",
	"winback_services",
	"retention_services",
	"dataset_utils",
	"goal_utils",
	"shared_utils",
]
