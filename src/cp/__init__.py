"""
Cp command policy rules.

This module provides safety checks for cp (copy) operations.
"""

from src.cp.allow import cp_safe_operations_rule

all_rules = [cp_safe_operations_rule]
all_middleware = []