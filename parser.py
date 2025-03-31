# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# parser/parse.py
# 
# Makabaka1880, 2025. All rights reserved.

from models.model import *
from models.exceptions import *
from typing import Optional, Tuple
from utils.persistence import TermDB
from utils.history import HistoryStore
import re
from colors import *

# Constants
histore_temp = HistoryStore()
db_temp = TermDB()

def allowed_identifier(identifier: str) -> bool:
    """Test whether if the given name is valid as an identifier."""
    return True if re.fullmatch(r"^[A-Za-z][A-Za-z0-9_'-]*$", identifier) else False

def parenthesis_match(literal: str) -> bool:
    count = 0
    for char in literal:
        if char == "(":
            count += 1
        elif char == ")":
            count -= 1
    return count == 0

def extract_application(literal: str) -> list[str]:
    """Extract top-level terms in an application expression."""
    terms, i, n = [], 0, len(literal)
    
    while i < n:
        if literal[i] == '(':
            start, depth = i, 1
            i += 1
            while i < n and depth > 0:
                if literal[i] == '(':
                    depth += 1
                elif literal[i] == ')':
                    depth -= 1
                i += 1
            if depth == 0:
                terms.append(literal[start:i])
            else:
                raise MismatchParenthesis(f"Unbalanced parentheses in: {literal[start:]}")
        else:
            start = i
            while i < n and literal[i] != '(':
                i += 1
            if start != i:
                terms.append(literal[start:i])
    
    return terms

def clear_parenthesis(literal: str) -> str:
    """Remove unnecessary parentheses."""
    literal = literal.replace(' ', '')
    
    def strip_outer(s: str) -> str:
        if not (s.startswith('(') and s.endswith(')')):
            return s
        depth = 0
        for i, char in enumerate(s):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and i != len(s) - 1:
                    return s
        return strip_outer(s[1:-1])
    
    stripped = strip_outer(literal)
    if not parenthesis_match(stripped):
        raise MismatchParenthesis(f"Unmatched parentheses in: {stripped}")
    return stripped

def parse_variable(literal: str) -> Optional[Term]:
    """Parse a variable."""
    literal = clear_parenthesis(literal.strip())
    if not allowed_identifier(literal):
        return None
    return Variable(literal)

def parse_lambda(literal: str) -> Term:
    """Parse a lambda expression into a Term object."""
    literal = clear_parenthesis(literal.strip())
    
    if (var := parse_variable(literal)):
        return var
    
    try:
        if literal.startswith('\\'):
            return parse_abstraction(literal[1:])
        return parse_application(literal)
    except Exception as e:
        raise ParseError(f"Failed to parse: {literal}, Error: {e}")

def parse_abstraction(literal: str) -> Term:
    """Parse an abstraction expression."""
    try:
        var_part, body_part = literal.split('.', 1)
    except ValueError:
        raise ParseError(f"Invalid abstraction: {literal}")
    
    var_part = clear_parenthesis(var_part.strip().lstrip('\\'))
    if not allowed_identifier(var_part):
        raise ParseError(f"Invalid parameter name: {var_part}")
    
    return Abstraction(Variable(var_part), parse_lambda(body_part.strip()))

def auto_alpha_convert(term: Term, bound_vars: set[str] = None, db_vars: set[str] = None) -> Term:
    """
    Alpha-conversion to avoid variable capture and name clashes with bound variables or database variables.
    
    Arguments:
        term (Term): The term to convert
        bound_vars (set[str], optional): Set of bound variables in the current scope
        db_vars (set[str], optional): Set of variables already present in the database or history
    
    Returns:
        Term: The alpha-converted term
    """
    if bound_vars is None:
        bound_vars = set()

    if db_vars is None:
        db_vars = set()

    if isinstance(term, Variable):
        # Leave free variables alone, no conversion
        return term
    elif isinstance(term, Abstraction):
        # If the bound variable is in the bound set or the db_vars, rename it
        if term.var.name in bound_vars or term.var.name in db_vars:
            _var = fresh_variable(term.var.name, lambda x: x in bound_vars or x in db_vars)
            term = term.alpha_conversion(_var)
        new_bound_vars = bound_vars | {term.var.name}
        term.body = auto_alpha_convert(term.body, new_bound_vars, db_vars)
    
    elif isinstance(term, Application):
        term.function = auto_alpha_convert(term.function, bound_vars, db_vars)
        term.value = auto_alpha_convert(term.value, bound_vars, db_vars)
    
    else:
        raise NotImplementedError(f"WTF IS THIS THING??? {type(term)}")

    return term


def substitute_free_vars(term: Term, db_vars: dict[str, Term]) -> Term:
    """
    Substitute free variables in the term with corresponding variables from the database.

    Arguments:
        term (Term): The term to convert.
        db_vars (dict[str, Term]): A dictionary mapping variable names to their corresponding terms in the database.

    Returns:
        Term: The term with free variables substituted.
    """
    if isinstance(term, Variable):
        # If the variable is free and in the database, substitute it
        for name, _term in db_vars:
            if term.name == name:
                return _term
        return term  # If the variable is not in the db, leave it as is
    elif isinstance(term, Abstraction):
        # In abstraction, bound variables should not be substituted.
        # So we recursively substitute in the body.
        term.body = substitute_free_vars(term.body, db_vars)
    elif isinstance(term, Application):
        # Recursively substitute in both function and argument.
        term.function = substitute_free_vars(term.function, db_vars)
        term.value = substitute_free_vars(term.value, db_vars)
    else:
        raise NotImplementedError(f"Unexpected term type: {type(term)}")
    return term


def parse_term(literal: str) -> Term:
    unreplaced = parse_lambda(literal)
    unreplaced = auto_alpha_convert(unreplaced, None, db_temp.get_vars())
    db_vars = db_temp.get_all_terms()
    his_vars = histore_temp.list_entries()
    combined_vars = [*db_vars, *his_vars]
    unreplaced = substitute_free_vars(unreplaced, combined_vars)
    return unreplaced

def parse_application(literal: str) -> Term:
    """Parse an application expression."""
    terms = extract_application(literal)
    if len(terms) < 2:
        raise ParseError(f"Application requires at least two terms: {literal}")
    
    parsed_terms = [parse_lambda(term) for term in terms]
    current = parsed_terms[0]
    for term in parsed_terms[1:]:
        current = Application(current, term)
    return current

if __name__ == "__main__":
    test_literals = [
        r"(\f'. f') ((\x. x))",
        r"((\(n). ((\(f). ((\(x). ((f) (((n) (f)) (x))))))))) ((\(f). ((\(x). (x)))))",
        r"(\x. (x (x)))",  # Checks for variable-parameter name clash
        r"(((\x. ((x (x)))) (\y. ((y (y))))))",  # Infinite recursion
        r"(((\x. ((\y. ((x) (y))))) (a)) (b))",  # Reduces to (a b)
        r"(((\x. ((x ((\y. ((y) (y))))))) (z)))",  # Reduces to (z (\y. (y y)))
        r"((((\x. ((\y. ((x) (y) (y))))) ((\z. (z)))) ((\w. (w)))))",  # Reduces to identity function
        r"((((\m. ((\n. ((\f. ((m) ((n) (f)))))))) ((\f. ((\x. ((f) (x))))))) ((\f. ((\x. ((f) ((f) (x)))))))))",  # Church numeral 2
        r"(((S) (K)) (K) (a))",  # Reduces to a
        r"(((\x. ((x) (x)))) ((\y. ((\z. ((y) ((y) (z))))))))",  # Infinite pattern growth
        r"((((\x. ((\y. ((x) (y) (x))))) ((\z. (z)))) ((a) (b))))",  # Reduces to ((a b) I)
        r"((Y) (g))",  # Infinite recursion
        r"((((\x. ((\y. ((x) (y))))) ((\x. ((x) (x))))) ((\y. ((y) (y))))))",  # Infinite loop
        r"((((\x. ((\y. ((\z. ((x) (z) ((y) (z)))))))) ((\a. (a)))) ((\b. (b)))))",  # Reduces to (\z. (z z))
        r"(((\x. ((x) ((\y. ((x) (y)))))) ((\z. (z)))))",  # Reduces to identity function
        r"((((\m. ((\n. ((m) (((n) (f)) (x))))))) ((\f. ((\x. ((f) ((f) (x)))))))) ((\f. ((\x. ((f) ((f) ((f) (x)))))))))",  # f^6 x
        r"(((((\x. ((\y. ((\z. ((x) ((y) (z)))))))) ((\a. (a)))) ((\b. (b)))) ((\c. (c)))))",  # Reduces to identity function
        r"((((\x. ((\y. ((x) ((y) (x)))))) ((\z. (z)))) ((\w. (w)))))",  # Reduces to identity function
        r"((((\x. ((\y. ((\z. ((x) ((y) (z)))))))) ((\a. ((\b. ((a) (b))))))) ((\c. ((\d. ((c) (d))))))))",  # Complex abstraction
        r"(((\x. ((x) ((x) ((x)))))) ((\y. ((y) ((y) ((y)))))))",  # Accelerated divergence
        r"((((\x. ((\y. ((x) ((x) (y)))))) ((\z. (z)))) (a)))",  # Reduces to a
        r"(((((\x. ((\y. ((x) (y)))))) ((\x. ((\y. (x)))))) (a)) (b))",  # Reduces to a
        r"(((((\x. ((\y. ((x)))))) (a)) (b)) (c))",  # Reduces to (a c)
        r"(((((\x. ((\y. ((\z. ((x) ((z) (y))))))))) (a)) (b) (c)))",  # Reduces to (a c b)
        r"(((\n. ((\f. ((\x. ((f) (((n) (f)) (x))))))))) ((\f. ((\x. ((f) ((f) (x))))))))",  # Successor of Church numeral 2
        r"((((\x. ((\y. ((\z. ((x) ((y) (z))))))))) ((\a. (a)))) ((\b. (b))))",  # Reduces to identity function
        r"(((\x. ((\y. ((x) ((y)))))) ((\z. (z)))) ((\w. (w))))",  # Simple application
        r"((((\x. ((\y. ((\z. ((x) ((y) ((z))))))))) ((\a. (a)))) ((\b. (b)))) ((\c. (c))))",  # Nested application
        r"(((\x. ((\y. ((x) ((y)))))) ((\z. ((z) ((z)))))) ((\w. ((w) ((w))))))",  # Higher-order application
        r"(((\x. ((\y. ((x) ((y)))))) ((\z. (z)))) (((\w. (w))) ((\v. (v)))))",  # Application with nested terms
        r"((((\x. ((\y. ((\z. ((x) ((y) ((z))))))))) ((\a. ((\b. ((a) (b))))))) ((\c. ((\d. ((c) (d))))))) ((\e. ((\f. ((e) (f)))))))",  # Complex nested application
        r"((((\x. ((\y. ((\z. ((x) ((y) ((z)))))))))) ((\a. (a)))) (((\b. (b))) ((\c. (c)))))",  # Mixed abstraction and application
        r"(((\x. ((\y. ((x) ((y)))))) ((\z. (z)))) ((\w. ((\v. ((w) (v)))))))",  # Currying with nested applications
        r"(((\x. ((\y. ((x) ((y)))))) ((\z. ((z) ((z)))))) (((\w. (w))) ((\v. ((v) ((v)))))))",  # Higher-order currying
    ]
    c = 0
    passed = 0
    for literal in test_literals:
        c += 1
        try:
            result = parse_term(literal)
            print(bold_text(color_text(f"[PASS] ({c}/{len(test_literals)})", "#3FF1B0")))  # Green
            print(color_text("[LITERAL]", "#3FF1B0"), literal)
            print(color_text("[PARSED]", "#3FF1B0"), result.literal())
            print(color_text("[EXPR]", "#3FF1B0"), result.__repr__())
            print(color_text("[TREE]", "#3FF1B0"), result.tree_str())
            passed += 1
        except Exception as e:
            print(bold_text(color_text("[ERR!]", "#D60025")), f"({c}/{len(test_literals)})")  # Red for keyword
            print(color_text("[LITERAL]", "#D60025"), literal)
            print(color_text("[ERROR]", "#D60025"), str(e))
    print('ALL UNIT TEST PASSED' if c == passed else color_text(f"FAILED (Only {passed}/{c} passed)", "#FF0000"))  # Red
    
    while True:
        literal = input('λ > ').strip()
        try:
            result = parse_term(literal)
            print(bold_text(color_text("[PARSE SUCCESS]", "#3FF1B0")))
            print(color_text("[LITERAL]", "#3FF1B0"), literal)
            print(color_text("[PARSED]", "#3FF1B0"), result.literal())
            print(color_text("[EXPR]", "#3FF1B0"), result.__repr__())
            print(color_text("[TREE]", "#3FF1B0"), result.tree_str())
        except Exception as e:
            print(bold_text(color_text("[ERROR]", "#D60025")), str(e))
