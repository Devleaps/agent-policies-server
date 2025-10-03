"""
Python3 command policy rules.

This module provides safety checks for python3 operations.
"""

from src.python3.venv import python3_venv_rule

all_rules = [python3_venv_rule]
all_middleware = []