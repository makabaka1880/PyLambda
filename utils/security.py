import re

# Created by Sean L. On Mar. 30
#
# Lambda Calculus Implementation
# utils/security.py
# 
# Makabaka1880, 2025. All rights reserved.

def check_for_dangerous_regex_pattern(pattern):
    """
    Check if a regex pattern is likely to match a lot of strings,
    which could cause significant damage when used in sensitive operations.
    """
    dangerous_patterns = [
        r".*",  # Matches everything
        r".+?", # Matches almost everything lazily
        r".+.*", # Matches everything with combinations
        r"^.*$", # Matches everything from start to end
        r".*?",  # Matches everything lazily
    ]
    
    for dangerous in dangerous_patterns:
        if re.fullmatch(dangerous, pattern):
            return True
    return False