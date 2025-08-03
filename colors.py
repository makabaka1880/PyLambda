# MARK: Imports and Metadata
# Created by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# repl/colors.py
#
# Makabaka1880, 2025. All rights reserved.

# MARK: Utility Functions
def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#').lower()
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def color_text(text, hex_color, bg=False):
    if not hex_color:
        return text
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

def clear():
    return "\033[2J\033[H"

# MARK: Global Constants
PALETTES = [
    # 0. Default
    {
        'lambda_prompt': '#0055AA',
        'alpha_prompt': '#0055AA',
        'beta_prompt': '#0055AA',
        'warning': '#EEAA55',
        'data': '#227655',
        'info': '#00AAAA',
        'error': '#EE3300',
        'success': '#00EE99',
        'beta_reduction_step': '#EECC55',
        'alpha_conversion_step': '#AA55EE',
        'security_prompt': '#FF00FF'
    },
    # 1. Ocean Depths
    {
        'lambda_prompt': '#2E86AB', 'alpha_prompt': '#3DCCC7',
        'beta_prompt': '#4ECDC4', 'warning': '#FF6B6B',
        'data': '#45B7D1', 'info': '#7EC8E3',
        'error': '#FF4040', 'success': '#4DBD90',
        'beta_reduction_step': '#FFE66D',
        'alpha_conversion_step': '#6A5ACD',
        'security_prompt': '#FF00FF'
    },
    
    # 2. Midnight Syntax
    {
        'data': '#8BE9FD', 'info': '#50FA7B',
        'error': '#FF5555', 'success': '#69FF94',
        'beta_reduction_step': '#F1FA8C',
        'success': '#69FF94',
        'beta_reduction_step': '#F1FA8C',
        'alpha_conversion_step': '#FF6FCF',
        'security_prompt': '#FF00FF'
    },

    # 3. Forest Canopy  
    {
        'lambda_prompt': '#3D550C', 'alpha_prompt': '#81B622',
        'beta_prompt': '#59981A', 'warning': '#ECF87F',
        'data': '#416D19', 'info': '#B5D8CC',
        'error': '#D34E24', 'success': '#A4DE02',
        'beta_reduction_step': '#FFE8A5',
        'alpha_conversion_step': '#A3CFA3',
        'security_prompt': '#FF00FF'
    },

    # 4. Solarized Dark
    {
        'lambda_prompt': '#268BD2', 'alpha_prompt': '#859900',
        'beta_prompt': '#B58900', 'warning': '#CB4B16',
        'data': '#2AA198', 'info': '#6C71C4',
        'error': '#DC322F', 'success': '#859900',
        'beta_reduction_step': '#EEE8D5',
        'alpha_conversion_step': '#93A1A1',
        'security_prompt': '#FF00FF'
    },

    # 5. Neon Cyber
    {
        'lambda_prompt': '#00F3FF', 'alpha_prompt': '#FF00FF',
        'beta_prompt': '#FF0099', 'warning': '#FFE900',
        'data': '#00FFA3', 'info': '#8A2BE2',
        'error': '#FF0066', 'success': '#00FF57',
        'beta_reduction_step': '#FF7F11',
        'alpha_conversion_step': '#FF33FF',
        'security_prompt': '#FF00FF'
    },

    # 6. Earth Tones
    {
        'lambda_prompt': '#8B4513', 'alpha_prompt': '#CD853F',
        'beta_prompt': '#D2B48C', 'warning': '#DAA520',
        'data': '#6B8E23', 'info': '#808000',
        'error': '#8B0000', 'success': '#556B2F',
        'beta_reduction_step': '#DEB887',
        'alpha_conversion_step': '#A0522D',
        'security_prompt': '#FF00FF'
    },

    # 7. Arctic Frost
    {
        'lambda_prompt': '#4682B4', 'alpha_prompt': '#87CEEB',
        'beta_prompt': '#B0E0E6', 'warning': '#FFD700',
        'data': '#5F9EA0', 'info': '#AFEEEE',
        'error': '#B22222', 'success': '#98FB98',
        'beta_reduction_step': '#F0FFFF',
        'alpha_conversion_step': '#ADD8E6',
        'security_prompt': '#FF00FF'
    },

    # 8. Dracula
    {
        'lambda_prompt': '#BD93F9', 'alpha_prompt': '#FF79C6',
        'beta_prompt': '#8BE9FD', 'warning': '#F1FA8C',
        'data': '#6272A4', 'info': '#50FA7B',
        'error': '#FF5555', 'success': '#69FF94',
        'beta_reduction_step': '#FFB86C',
        'alpha_conversion_step': '#FF92DF',
        'security_prompt': '#FF00FF'
    },

    # 9. Retro CRT
    {
        'lambda_prompt': '#00FF00', 'alpha_prompt': '#00FFFF',
        'beta_prompt': '#FF00FF', 'warning': '#FFFF00',
        'data': '#00FF7F', 'info': '#7FFF00',
        'error': '#FF0000', 'success': '#00FF7F',
        'beta_reduction_step': '#FFA500',
        'alpha_conversion_step': '#00FFCC',
        'security_prompt': '#FF00FF'
    },

    # 10. Sunset Dunes
    {
        'lambda_prompt': '#E2725B', 'alpha_prompt': '#FFA07A',
        'beta_prompt': '#FFD700', 'warning': '#FF4500',
        'data': '#CD5C5C', 'info': '#DEB887',
        'error': '#8B0000', 'success': '#7CFC00',
        'beta_reduction_step': '#FFDAB9',
        'alpha_conversion_step': '#FFB6C1',
        'security_prompt': '#FF00FF'
    },

    # 11. Matrix
    {
        'lambda_prompt': '#00FF00', 'alpha_prompt': '#00CC00',
        'beta_prompt': '#009900', 'warning': '#FFFF00',
        'data': '#006600', 'info': '#003300',
        'error': '#FF0000', 'success': '#00FF66',
        'beta_reduction_step': '#99FF99',
        'alpha_conversion_step': '#33FF33',
        'security_prompt': '#FF00FF'
    },

    # 12. Galaxy Core
    {
        'lambda_prompt': '#9370DB', 'alpha_prompt': '#BA55D3',
        'beta_prompt': '#FF00FF', 'warning': '#FFD700',
        'data': '#4B0082', 'info': '#7B68EE',
        'error': '#DC143C', 'success': '#00FA9A',
        'beta_reduction_step': '#E6E6FA',
        'alpha_conversion_step': '#DDA0DD',
        'security_prompt': '#FF00FF'
    },

    # 13. Industrial
    {
        'lambda_prompt': '#708090', 'alpha_prompt': '#A9A9A9',
        'beta_prompt': '#808080', 'warning': '#DAA520',
        'data': '#2F4F4F', 'info': '#778899',
        'error': '#8B0000', 'success': '#228B22',
        'beta_reduction_step': '#DCDCDC',
        'alpha_conversion_step': '#B0C4DE',
        'security_prompt': '#FF00FF'
    },

    # 14. Tropical Reef
    {
        'lambda_prompt': '#00CED1', 'alpha_prompt': '#40E0D0',
        'beta_prompt': '#00FFEF', 'warning': '#FFD700',
        'data': '#008B8B', 'info': '#AFEEEE',
        'error': '#FF4500', 'success': '#7FFF00',
        'beta_reduction_step': '#FF69B4',
        'alpha_conversion_step': '#20B2AA',
        'security_prompt': '#FF00FF'
    },

    # 15. Vintage Paper
    {
        'lambda_prompt': '#8B4513', 'alpha_prompt': '#A0522D',
        'beta_prompt': '#DEB887', 'warning': '#D2691E',
        'data': '#BC8F8F', 'info': '#CD853F',
        'error': '#8B0000', 'success': '#556B2F',
        'beta_reduction_step': '#FFF8DC',
        'alpha_conversion_step': '#F5DEB3',
        'security_prompt': '#FF00FF'
    },

    # 16. Candy Shop
    {
        'lambda_prompt': '#FF69B4', 'alpha_prompt': '#FF1493',
        'beta_prompt': '#FF00FF', 'warning': '#FFD700',
        'data': '#00FF7F', 'info': '#7FFF00',
        'error': '#FF0000', 'success': '#00FF00',
        'beta_reduction_step': '#FFB6C1',
        'alpha_conversion_step': '#FF85C1',
        'security_prompt': '#FF00FF'
    },

    # 17. Deep Space
    {
        'lambda_prompt': '#4169E1', 'alpha_prompt': '#6A5ACD',
        'beta_prompt': '#483D8B', 'warning': '#FFD700',
        'data': '#000080', 'info': '#87CEEB',
        'error': '#8B0000', 'success': '#3CB371',
        'beta_reduction_step': '#F0F8FF',
        'alpha_conversion_step': '#5F9EA0',
        'security_prompt': '#FF00FF'
    },

    # 18. Autumn Leaves
    {
        'lambda_prompt': '#D2691E', 'alpha_prompt': '#CD853F',
        'beta_prompt': '#A0522D', 'warning': '#FF4500',
        'data': '#8B4513', 'info': '#DEB887',
        'error': '#8B0000', 'success': '#556B2F',
        'beta_reduction_step': '#FFDAB9',
        'alpha_conversion_step': '#DAA520',
        'security_prompt': '#FF00FF'
    },

    # 19. Bioluminescent
    {
        'lambda_prompt': '#00FFEF', 'alpha_prompt': '#7FFF00',
        'beta_prompt': '#FF69B4', 'warning': '#FFFF00',
        'data': '#40E0D0', 'info': '#00FA9A',
        'error': '#FF0000', 'success': '#00FF00',
        'beta_reduction_step': '#FF00FF',
        'alpha_conversion_step': '#00FFCC',
        'security_prompt': '#FF00FF'
    },

    # 20. Monochrome
    {
        'lambda_prompt': '#404040', 'alpha_prompt': '#606060',
        'beta_prompt': '#808080', 'warning': '#A0A0A0',
        'data': '#202020', 'info': '#505050',
        'error': '#000000', 'success': '#B0B0B0',
        'beta_reduction_step': '#D0D0D0',
        'alpha_conversion_step': '#909090',
        'security_prompt': '#FF00FF'
    }
]

COLORS = PALETTES[0]

LABELS = {
    'lambda_prompt': 'LMB?',
    'alpha_prompt': 'ALF?',
    'beta_prompt': 'BET?',
    'warning': 'WARN',
    'data': 'DATA',
    'info': 'INFO',
    'error': 'ERR!',
    'success': 'DONE',
    'alpha_conversion_step': 'ASTP',
    'beta_reduction_step': 'BSTP',
    'security_prompt': 'SEC!'
}

IOSYMBOL = {
    'lambda_prompt': 'λ',  # Left arrow
    'alpha_prompt': 'α',  # Left arrow
    'beta_prompt': 'β',  # Left arrow
    'warning': '→',  # Right arrow
    'data': '→',  # Right arrow
    'info': '→',  # Right arrow
    'error': '→',  # Right arrow
    'success': '→',  # Right arrow
    'alpha_conversion_step': '→',  # Right arrow
    'beta_reduction_step': '→',  # Right arrow
    'security_prompt': '→'  # Right arrow
}

# MARK: IO Label Function
def IO_label(index, counter):
    return status_label('%' + str(counter), COLORS[index]) + ' ' + status_label(LABELS[index] + ' ' + IOSYMBOL[index], COLORS[index], False)
