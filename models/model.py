# Created by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# models/model.py
#
# Makabaka1880, 2025. All rights reserved.

from models.exceptions import *
from typing import Callable

def fresh_variable(base: str, crit: Callable[[str], bool]) -> str:
    """Generates a fresh variable name by appending primes until `crit` returns False.
    
    Used to avoid variable capture during substitution.
    
    Arguments:
        base (str): Base variable name (e.g., "z")
        crit (Callable[[str], bool]): Conflict checker function
        
    Returns:
        str: A unique variable name like "z''" if needed
        
    Example:
        >>> fresh_variable("z", lambda s: s == "z")
        "z'"
    """
    while crit(base):
        base += "'"
    return base

class Term:
    """Abstract base class for lambda calculus terms.
    
    Subclasses must implement core operations like substitution and beta reduction.
    
    Attributes:
        All subclasses define their own attributes (e.g., Variable.name).
    """
    
    def tree_str(self, indent: str = "", last: bool = True) -> str:
        """Generate hierarchical tree representation for debugging"""
        raise NotImplementedError("tree_str not implemented for base Term")
    
    def eval(self):
        raise NotImplementedError("`eval` method not yet implemented for class `Term`")
    
    def substitute(self, target: str, replacement: "Term") -> "Term":
        """Substitutes free occurrences of `target` with `replacement`.
        
        Arguments:
            target (str): Variable name to replace (e.g., "x")
            replacement (Term): Term to substitute in
            
        Returns:
            Term: New term with substitutions applied
        """
        raise NotImplementedError("Substitute method not implemented.")
    
    def alpha_conversion(self, name: str) -> "Term":
        """Renames bound variables to avoid name conflicts.
        
        Arguments:
            name (str): New variable name (e.g., "x'")
            
        Returns:
            Term: Alpha-equivalent term with renamed variables
        """
        raise NotImplementedError("Alpha conversion method not implemented.")
    
    def beta_reduce_step(self) -> "Term":
        """Performs a single beta reduction step (leftmost-outermost).
        
        Returns:
            Term: Reduced term
            
        Throws:
            ReductionOnNormalForm: If no reduction is possible
        """
        raise NotImplementedError("Beta reduction step not implemented.")
    
    def is_normal_form(self) -> bool:
        """Checks if the term is in normal form (no reducible expressions).
        
        Returns:
            bool: True if no beta reductions can be applied
        """
        raise NotImplementedError("Normal form detection not implemented.")

    def literal(self) -> str:
        """Generates a string representation matching lambda calculus syntax.
        
        Returns:
            str: Syntax-valid string like "λx. x y"
        """
        raise NotImplementedError("Literal representation not implemented.")

class Variable(Term):
    """Represents a variable in lambda calculus.
    
    Attributes:
        name (str): Variable identifier (e.g., "x")
        
    Example:
        >>> x = Variable("x")
        >>> x.has_free("x")
        True
    """
    
    def __init__(self, name: str):
        """Initializes a Variable instance.
        
        Arguments:
            name (str): Variable identifier
        """
        super().__init__()
        self.name = name

    def __repr__(self) -> str:
        return self.name
    
    def tree_str(self, indent: str = "", last: bool = True, child: bool = False) -> str:
        branch = "└── " if last else "├── "
        return f"{indent}{branch}{self.name}" if child else f"Variable {self.name}"
    
    def is_normal_form(self) -> bool:
        """Variables are always in normal form."""
        return True
    
    def alpha_conversion(self, name: str) -> "Variable":
        """Variables don't require alpha conversion (identity operation)."""
        return self
    
    def substitute(self, target: str, replacement: Term) -> Term:
        """Replaces this variable if it matches the target.
        
        Arguments:
            target (str): Variable name to replace
            replacement (Term): Term to substitute in
        """
        return replacement if self.name == target else self

    def beta_reduce_step(self) -> "Variable":
        raise ReductionOnNormalForm(term=self)
    
    def literal(self) -> str:
        return f'({self.name})'
    
    def has_free(self, name: str) -> bool:
        """Checks if this variable matches the given name."""
        return self.name == name

class Abstraction(Term):
    """Represents a lambda abstraction (λx. body).
    
    Attributes:
        var (Variable): Bound variable (e.g., "x")
        body (Term): Body of the abstraction
        
    Example:
        >>> abs_term = Abstraction(Variable("x"), Variable("x"))
        >>> abs_term.literal()
        "(\\x. x)"
    """
    
    def __init__(self, var: Variable, body: Term):
        """Initializes an Abstraction instance.
        
        Arguments:
            var (Variable): Bound variable
            body (Term): Term representing the abstraction body
        """
        super().__init__()
        self.var = var
        self.body = body

    def __repr__(self) -> str:
        return f"(λ{self.var}. {self.body})"
    
    def is_normal_form(self) -> bool:
        """Abstractions are in normal form if their body is."""
        return self.body.is_normal_form()

    def alpha_conversion(self, new_name: str) -> "Abstraction":
        """Renames the bound variable to avoid capture.
        
        Arguments:
            new_name (str): New variable name (e.g., "x'")
        """
        new_var = Variable(new_name)
        new_body = self.body.substitute(self.var.name, new_var)
        return Abstraction(new_var, new_body)

    def substitute(self, target: str, replacement: Term) -> Term:
        """Substitutes in the abstraction body, avoiding variable capture.
        
        Arguments:
            target (str): Variable name to replace
            replacement (Term): Term to substitute in
        """
        if self.var.name == target:
            return self  # Bound variable shadows target
        
        if replacement.has_free(self.var.name):
            new_name = fresh_variable(self.var.name, replacement.has_free)
            return self.alpha_conversion(new_name).substitute(target, replacement)
            
        return Abstraction(self.var, self.body.substitute(target, replacement))

    def beta_reduce_step(self) -> "Abstraction":
        """Reduces the abstraction body if possible."""
        if self.is_normal_form():
            raise ReductionOnNormalForm(term=self)
        return Abstraction(self.var, self.body.beta_reduce_step())

    def literal(self) -> str:
        return rf"(\{self.var.literal()}. {self.body.literal()})"


    def tree_str(self, indent: str = "", last: bool = True, child: bool = False) -> str:
        lines = []
        branch = "└── " if last else "├── "
        lines.append(f"{indent}{branch}λ {self.var.name}" if child else f"Abstraction λ {self.var.name}" )
        
        # Maintain vertical lines for nested abstractions
        new_indent = indent + ("│   " if not last else "    ")
        
        # Body subtree (always last child for abstractions)
        lines.append(self.body.tree_str(new_indent, True, True))
        
        return "\n".join(lines)
    
    def has_free(self, name: str) -> bool:
        """Checks for free occurrences of `name` in the body."""
        return self.var.name != name and self.body.has_free(name)

class Application(Term):
    """Represents function application (f x).
    
    Attributes:
        function (Term): Applied function term
        value (Term): Argument term
        
    Example:
        >>> app = Application(Variable("f"), Variable("x"))
        >>> app.literal()
        "(f x)"
    """
    
    def __init__(self, function: Term, value: Term):
        """Initializes an Application instance.
        
        Arguments:
            function (Term): Function to apply
            value (Term): Argument to apply
        """
        super().__init__()
        self.function = function
        self.value = value

    def __repr__(self) -> str:
        return f"({self.function} {self.value})"

    def is_normal_form(self) -> bool:
        """Applications are in normal form if neither component can reduce."""
        return (
            not isinstance(self.function, Abstraction) and 
            self.function.is_normal_form() and 
            self.value.is_normal_form()
        )
    
    def alpha_conversion(self, name: str) -> "Application":
        """Applies alpha conversion to both function and argument."""
        return Application(
            self.function.alpha_conversion(name),
            self.value.alpha_conversion(name)
        )

    def substitute(self, target: str, replacement: Term) -> "Application":
        """Substitutes in both function and argument components."""
        return Application(
            self.function.substitute(target, replacement),
            self.value.substitute(target, replacement)
        )

    def beta_reduce_step(self) -> Term:
        """Performs leftmost-outermost beta reduction."""
        if isinstance(self.function, Abstraction):
            return self.function.body.substitute(
                self.function.var.name, 
                self.value
            )
        
        try:
            return Application(self.function.beta_reduce_step(), self.value)
        except ReductionOnNormalForm:
            return Application(self.function, self.value.beta_reduce_step())

    def literal(self) -> str:
        return f"({self.function.literal()} {self.value.literal()})"
    
    def tree_str(self, indent: str = "", last: bool = True, child: bool = False) -> str:
        lines = []
        branch = "└── " if last else "├── "
        lines.append(f"{indent}{branch}Applicate" if child else f"Application")
        
        # Correct indentation: Use vertical lines for all children except last
        new_indent = indent + ("    " if last else "│   ")
        # new_indent = "│   "
        
        # Function subtree (not last)
        lines.append(self.function.tree_str(new_indent, False, True))
        
        # Value subtree (last)
        lines.append(self.value.tree_str(new_indent, True, True))
        
        return "\n".join(lines)
    
    def has_free(self, name: str) -> bool:
        """Checks for free variables in either component."""
        return self.function.has_free(name) or self.value.has_free(name)

# MARK: Helper Functions
def makeVar(name: str) -> Variable:
    """Helper for creating Variable instances.
    
    Example:
        >>> x = makeVar("x")
    """
    return Variable(name)

# Test case for left-to-right reduction
test_expr = Application(
    Abstraction(
        Variable('x'),
        Application(Variable('x'), Variable('y'))
    ),
    Variable('z')
)

church_succ = Abstraction(
    Variable('n'),
    Abstraction(
        Variable('f'),
        Abstraction(
            Variable('x'),
            Application(
                Variable('f'),
                Application(Variable('n'), Variable('f'))
            )
        )
    )
)

if __name__ == "__main__":
    print(church_succ.tree_str())
    from parser import parse_lambda
    weirdCombinator = parse_lambda(r"((\n. (n) (n))) ((\y. (\z. (y) ((y) (z)))))")
    print(weirdCombinator.tree_str())