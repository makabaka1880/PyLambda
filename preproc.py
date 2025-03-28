# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# parser/prepoc.py
# 
# Makabaka1880, 2025. All rights reserved.

from typing import Tuple
def normalize_blank(cmd: str) -> Tuple[str, str]:
    lines = cmd.split()
    keyword = lines[0]
    command = ''.join(lines[1:])
    return keyword, command