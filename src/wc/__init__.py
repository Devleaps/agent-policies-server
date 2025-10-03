"""
Wc command policy rules.

This module provides safety checks for wc (word count) operations.
"""

from src.wc.allow import wc_safe_operations_rule

all_rules = [wc_safe_operations_rule]
all_middleware = []