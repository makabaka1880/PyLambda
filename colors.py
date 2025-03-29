# Created by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# repl/colors.py
#
# Makabaka1880, 2025. All rights reserved.

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#').lower()
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def color_text(text, hex_color, bg=False):
    r, g, b = hex_to_rgb(hex_color)
    mode = 48 if bg else 38
    return f"\033[{mode};2;{r};{g};{b}m{text}\033[0m"

def bold_text(text):
    return f"\033[1m{text}\033[0m"

def italic_text(text):
    return f"\033[3m{text}\033[0m"

def underline_text(text):
    return f"\033[4m{text}\033[0m"

def blinking_text(text):
    return f"\033[5m{text}\033[0m"

def status_label(text, hex_color, bg=False):
    return bold_text(color_text(f"[{text}]", hex_color, bg))

# Global constants for colors and labels
# COLORS = {
#     'lambda_prompt': '#0055AA',
#     'alpha_prompt': '#0055AA',
#     'beta_prompt': '#0055AA',
#     'warning': '#EEAA55',
#     'data': '#227655',
#     'info': '#00AAAA',
#     'error': '#EE3300',
#     'success': '#00EE99',
#     'beta_reduction_step': '#EECC55'
# }
COLORS = {
    'lambda_prompt': '#00ff9d',  # Neon Cyan
    'alpha_prompt': '#ff6ec7',   # Hot Pink
    'beta_prompt': '#ffe74c',    # Lemon Yellow
    'warning': '#ff971c',        # Tangerine
    'data': '#20c997',           # Emerald
    'info': '#0dcaf0',           # Vivid Sky Blue
    'error': '#ff355e',          # Electric Red
    'success': '#7cfc00',        # Lawn Green
    'beta_reduction_step': '#fd7f20'  # Pumpkin
}
LABELS = {
    'lambda_prompt': 'LMB?',
    'alpha_prompt': 'ALF?',
    'beta_prompt': 'BET?',
    'warning': 'WARN',
    'data': 'DATA',
    'info': 'INFO',
    'error': 'ERR!',
    'success': 'DONE',
    'beta_reduction_step': 'BSTP'
}