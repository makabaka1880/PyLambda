# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# parser/parse.py
# 
# Makabaka1880, 2025. All rights reserved.

from colorist import Color, Effect
from utils.persistence import TermDB
from models.model import *
from models.exceptions import *
from typing import Tuple, Optional
from re import *

def parenthesis_match(literal: str) -> bool:
    count = 0
    for i in literal:
        if i == "(":
            count += 1
        elif i == ")":
            count -= 1
    return count == 0

def extract_application(literal: str) -> list[str]:
    """Split into all top-level terms (not just two)"""
    terms = []
    i = 0
    n = len(literal)
    
    while i < n:
        if literal[i] == '(':
            # Track nested parentheses for the current term
            start = i
            depth = 1
            i += 1
            while i < n and depth > 0:
                if literal[i] == '(':
                    depth += 1
                elif literal[i] == ')':
                    depth -= 1
                i += 1
            if depth == 0:
                terms.append(literal[start:i])  # Include closing ')'
            else:
                raise MismatchParenthesis(f"Unbalanced parentheses in: {literal[start:]}")
        else:
            # Capture non-parenthesized term (e.g., variables like 'a')
            start = i
            while i < n and literal[i] != '(':
                i += 1
            if start != i:
                terms.append(literal[start:i])
                
    return terms  # Now returns list of all top-level terms

def clear_parenthesis(literal: str) -> str:
    literal = literal.replace(' ', '')  # Clear blank spaces
    def strip_outer(s: str) -> str:
        if not (s.startswith('(') and s.endswith(')')):  # Base case: No more outer parentheses
            return s
        # Check if the outermost parentheses are actually a full wrapper
        depth = 0
        for i, char in enumerate(s):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and i != len(s) - 1:  # If closing parenthesis isn't at the end, stop
                    return s
        # If we reach here, the outermost parentheses fully wrap the expression
        return strip_outer(s[1:-1])  # Recursively remove them
    stripped = strip_outer(literal)
    if not parenthesis_match(stripped):  # Ensure no unmatched parentheses remain
        raise MismatchParenthesis(literal=stripped)
    return stripped
    
def parse_variable(literal: str, db: Optional[TermDB] = None) -> Optional[Term]:
    """Parse variable with persistence layer check"""
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    if fullmatch(pattern, literal):
        # Check database first
        if db and (stored := db.get_term(literal)):
            return stored
        return Variable(literal)
    return None

def parse_lambda(literal: str, db: Optional[TermDB] = None) -> Term:
    literal = clear_parenthesis(literal)
    
    # Check for variable match first
    if (var := parse_variable(literal, db)) is not None:
        return var
    
    if literal.startswith('\\'):
        return parse_abstraction(literal[1:], db)
    
    return parse_application(literal, db)

def parse_abstraction(literal: str, db: Optional[TermDB] = None) -> Term:
    var, body, *_ = literal.split('.', 1)
    var_term = parse_lambda(var.strip(), db)
    if not isinstance(var_term, Variable):
        raise ParseError(f"Invalid abstraction variable: {var}")
    return Abstraction(var_term, parse_lambda(body.strip(), db))

def parse_application(literal: str, db: Optional[TermDB] = None) -> Term:
    try:
        terms = extract_application(literal)
        if len(terms) < 2:
            raise ParseError(f"Application requires at least two terms: {literal}")
        
        # Build left-associative nested applications
        current_term = parse_lambda(terms[0], db)
        for term_str in terms[1:]:
            current_term = Application(current_term, parse_lambda(term_str, db))
            
        return current_term
    except ValueError as e:
        raise ParseError(f"Invalid application format: {literal}") from e
    
if __name__ == "__main__":
    test_literals = [
        r"((\x.(x (x))) (\y.(y (y))))",  # Infinite recursion
        r"((\x.(\y.(x y))) a b)",  # Reduces to (a b)
        r"((\x.(x (\y.(y y)))) z)",  # Reduces to (z (\y.(y y)))
        r"(((\x.(\y.(x y y))) (\z.(z))) (\w.(w)))",  # Reduces to identity function
        r"(((\m.(\n.(\f.(m (n f))))) (\f.(\x.(f x)))) (\f.(\x.(f (f x)))))",  # Church numeral 2
        r"((S K K) a)",  # Reduces to a
        r"((\x.(x x)) (\y.(\z.(y (y z)))))",  # Infinite pattern growth
        r"(((\x.(\y.(x y x))) (\z.(z))) (a b))",  # Reduces to ((a b) I)
        r"(Y g)",  # Infinite recursion
        r"(((\x.(\y.(x y))) (\x.(x x))) (\y.(y y)))",  # Infinite loop
        r"(((\x.(\y.(\z.(x z (y z))))) (\a.(a))) (\b.(b)))",  # Reduces to (\z.(z z))
        r"((\x.(x (\y.(x y)))) (\z.(z)))",  # Reduces to identity function
        r"(((\m.(\n.(m (n f) x))) (\f.(\x.(f (f x))))) (\f.(\x.(f (f (f x))))))",  # f^6 x
        r"((((\x.(\y.(\z.(x (y z))))) (\a.(a))) (\b.(b))) (\c.(c)))",  # Reduces to identity function
        r"(((\x.(\y.(x (y x)))) (\z.(z))) (\w.(w)))",  # Reduces to identity function
        r"(((\x.(\y.(\z.(x (y z))))) (\a.(\b.(a b)))) (\c.(\d.(c d))))",  # Complex abstraction
        r"((\x.(x x)) (\y.(y y y)))",  # Accelerated divergence
        r"(((\x.(\y.(x (x y)))) (\z.(z))) a)",  # Reduces to a
        r"((((\x.(\y.(x y))) (\x.(\y.(x)))) a) b)",  # Reduces to a
        r"((((\x.(\y.(x)))) a) b c)",  # Reduces to (a c)
        r"((((\x.(\y.(\z.(x z y)))) a) b) c)",  # Reduces to (a c b)
        r"((\n. (\f. (\x. (f((n(f))(x))))))) (\f. (\x. (f(f(x)))))"
    ]

    c = 0
    for literal in test_literals:
        c += 1
        try:
            literal = literal.replace(' ', '')
            result = parse_lambda(literal, TermDB())
            print(f"{Effect.BOLD}{Color.GREEN}Parsed ({c}/{len(test_literals)}){Color.OFF}{Effect.OFF}\n{Color.GREEN}LITERAL{Color.OFF}'{literal}'\n{Color.GREEN}TERM{Color.OFF}{result}")
        except Exception as e:
            print(f"{Color.RED}Error{Color.OFF} parsing '{literal}': {e}")