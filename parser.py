# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# parser/parse.py
# 
# Makabaka1880, 2025. All rights reserved.

from utils.persistence import TermDB
from utils.history import HistoryStore
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
    
def parse_variable(literal: str, db: Optional[TermDB] = None, history: Optional[HistoryStore] = None) -> Optional[Term]:
    """Parse variable with history and database lookups"""
    # Validate variable syntax
    literal = clear_parenthesis(literal.strip())
    if not fullmatch(r'^[a-zA-Z_]\w*$', literal):
        return None
    
    # Database lookup
    if db and (stored := db.get_term(literal)):
        return stored
    
    # History store lookup
    if history:
        try:
            if literal.startswith('_') and (index := int(literal[1:])):
                if stored := history.fetch(index):
                    return Variable(stored)
        except ValueError:
            pass
    
    return Variable(literal)

def parse_lambda(
        literal: str,
        db: Optional[TermDB] = None,
        history: Optional[HistoryStore] = None,
        auto_alpha_conversion: bool = True
    ) -> Term:
    r"""Parse a lambda expression into a term.

    Parameters:
        literal (str): The lambda expression to parse
        db (Optional[TermDB]): Database for variable lookup
        history (Optional[HistoryStore]): History store for term retrieval
        auto_alpha_conversion (bool): Flag for automatic alpha conversion
    Returns:
        Term: Parsed lambda term
    Raises:
        ParseError: If the expression is invalid
        MismatchParenthesis: If parentheses are mismatched
    
    Example:
        >>> parse_lambda(r"(\x.(x x))").tree_str()
        (λx. (x x))
    """
    
    # Handle blank spaces and parentheses
    literal = literal.strip()
    literal = clear_parenthesis(literal)
    
    # Check for variable match first
    if (var := parse_variable(literal, db, history)) is not None:
        return var
    # Check history store for a previously stored term
    try:
        index = int(literal[1:])
        if history and (stored := history.fetch(index)):
            return Variable(stored)
    except ValueError:
        pass
    # Check for abstraction or application
    if literal.startswith('\\'):
        return parse_abstraction(literal[1:], db, history)
    
    return parse_application(literal, db, history)

def parse_abstraction(literal: str, db: Optional[TermDB] = None, history: Optional[HistoryStore] = None) -> Term:
    """Parse abstraction with parameter conflict resolution using alpha conversion"""
    # Extract parameter and body sections
    var_part, body_part = literal.split('.', 1)
    var_part = clear_parenthesis(var_part.strip().lstrip('\\'))  # Handle both λ and \ syntax
    
    # Validate parameter syntax
    if not fullmatch(r'^[a-zA-Z_]\w*$', var_part):
        raise ParseError(f"Invalid parameter name: {var_part}")
    
    param_var = Variable(var_part)
    
    # Check for database conflicts
    if db and db.get_term(param_var.name):
        # Generate fresh variable name that's not in use
        new_name = fresh_variable(
            param_var.name,
            lambda s: db.get_term(s) is not None
        )
        
        # Create temporary abstraction for alpha conversion
        temp_abs = Abstraction(param_var, parse_lambda(body_part.strip(), db, history))
        return temp_abs.alpha_conversion(new_name)
    
    # No conflict, parse normally
    return Abstraction(param_var, parse_lambda(body_part.strip(), db, history))

def parse_application(literal: str, db: Optional[TermDB] = None, history: Optional[HistoryStore] = None) -> Term:
    """Optimized application parser with bulk processing"""
    terms = extract_application(literal)
    if len(terms) < 2:
        raise ParseError(f"Application requires at least two terms: {literal}")
    
    # Pre-parse all terms first
    parsed_terms = [parse_lambda(term, db, history) for term in terms]
    
    # Build left-associative applications
    current = parsed_terms[0]
    for term in parsed_terms[1:]:
        current = Application(current, term)
    return current

# Test cases
# These are just examples and may not cover all edge cases
# You can add more test cases to validate the parser's behavior
if __name__ == "__main__":
    test_literals = [
        r"(\(n). (\(f). (\(x). ((f) (((n) (f)) (x))))))(\(f). (\(x). (x)))"
        r"(\x.x (x))",  # Checks for variable-parameter name clash
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
        r"((\n. (\f. (\x. (f((n(f))(x))))))) (\f. (\x. (f(f(x)))))" # Successor of Church numeral 2
        r"((\x.(\y.(\z.(x (y z)))))) (\a.(a)) (\b.(b))",  # Reduces to identity function
    ]

    c = 0
    for literal in test_literals:
        c += 1
        try:
            result = parse_lambda(literal, TermDB(), HistoryStore())
            print(f"{Effect.BOLD}{Color.GREEN}[PASS] ({c}/{len(test_literals)}){Color.OFF}{Effect.OFF}")
            print(f"{Color.GREEN}LITERAL {Color.OFF}'{literal}'")
            print(f"{Color.GREEN}TERM {Color.OFF}{result}")
            print(f"{Color.GREEN}Tree {Color.OFF}{result.tree_str()}")
        except Exception as e:
            print(f"{Effect.BOLD}{Color.RED}[ERR!] ({c}/{len(test_literals)}){Color.OFF}{Effect.OFF}\n{Color.RED}LITERAL{Color.OFF} '{literal}'\n{Color.RED}ERROR {Color.OFF}{e}")
    print('ALL UNIT TEST ' if c == len(test_literals) else f"{Color.RED}FAIL{Color.OFF}")