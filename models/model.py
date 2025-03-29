# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# models/model.py
#
# Makabaka1880, 2025. All rights reserved.

from models.exceptions import *
from uuid import uuid4

def fresh_variable(base: str) -> str:
    return f"{base}_{uuid4().hex[:4]}"

class Term:
    """Base class for any term in a lambda abstraction."""
    
    def eval(self):
        raise NotImplementedError("`eval` method not yet implemented for class `Term`")
    
    def substitute(self, target: str, replacement: "Term") -> "Term":
        """Substitutes free occurrences of `target` with `replacement`, ensuring left-to-right order."""
        raise NotImplementedError("Substitute method not implemented.")
    
    def alpha_conversion(self, name: str) -> "Term":
        """Renames bound variables to prevent name conflicts."""
        raise NotImplementedError("Alpha conversion method not implemented.")
    
    def beta_reduce_step(self) -> "Term":
        """Performs a single beta reduction step."""
        raise NotImplementedError("Beta reduction step not implemented.")
    
    def is_normal_form(self) -> bool:
        """Checks if the term is in normal form (i.e., cannot be reduced further)."""
        raise NotImplementedError("Normal form detection not implemented.")

    def literal(self) -> str:
        raise NotImplementedError("Literal representation not implemented.")

class Variable(Term):
    """Represents a lambda variable."""
    
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name
    
    def is_normal_form(self):
        return True
    
    def alpha_conversion(self, name):
        return self  # No alpha conversion needed for standalone variables
    
    def substitute(self, target, replacement):
        return replacement if self.name == target else self

    def beta_reduce_step(self):
        raise ReductionOnNormalForm(term=self)
    
    def literal(self):
        return self.name
    
    def has_free(self, name: str) -> bool:
        return self.name == name

class Abstraction(Term):
    """Represents a lambda abstraction (λx. body)."""
    
    def __init__(self, var, body):
        super().__init__()
        self.var = var
        self.body = body

    def __repr__(self):
        return f"(λ{self.var}. {self.body})"
    
    def is_normal_form(self):
        return self.body.is_normal_form()

    def alpha_conversion(self, new_name: str) -> "Abstraction":
        """Renames the bound variable to avoid capture."""
        new_var = Variable(new_name)
        new_body = self.body.substitute(self.var.name, new_var)
        val = Abstraction(new_var, new_body)
        return val

    def substitute(self, target: str, replacement: Term) -> Term:
        """Substitutes target variable with replacement in the abstraction's body."""
        if self.var.name == target:
            return self  # Bound variable is shadowing `target`, so no substitution
        # Ensure no variable capture
        if replacement.has_free(self.var.name):
            new_var_name = fresh_variable(self.var.name)
            new_abs = self.alpha_conversion(new_var_name)
            return Abstraction(new_abs.var, new_abs.body.substitute(target, replacement))
        
        return Abstraction(self.var, self.body.substitute(target, replacement))

    def beta_reduce_step(self) -> "Abstraction":
        if self.is_normal_form():
            raise ReductionOnNormalForm(term=self)
        return Abstraction(self.var, self.body.beta_reduce_step())

    def literal(self):
        return rf"(\{self.var.literal()}. {self.body.literal()})"

    def has_free(self, name: str) -> bool:
        return self.var.name != name and self.body.has_free(name)

class Application(Term):
    """Represents function application (f x)."""
    
    def __init__(self, function, value):
        super().__init__()
        self.function = function
        self.value = value

    def __repr__(self):
        return f"({self.function} {self.value})"

    def is_normal_form(self):
        return isinstance(self.function, Abstraction) is False and self.function.is_normal_form() and self.value.is_normal_form()
    
    def alpha_conversion(self, name):
        """Applies alpha conversion to both function and value."""
        val = Application(self.function.alpha_conversion(name), self.value.alpha_conversion(name))
        return Application(self.function.alpha_conversion(name), self.value.alpha_conversion(name))

    def substitute(self, target, replacement):
        """Substitutes all occurence of a variabel in an application"""
        new_function = self.function.substitute(target, replacement)
        new_value = self.value.substitute(target, replacement)
        val = Application(new_function, new_value)
        print(val)
        return val

    def beta_reduce_step(self):
        """Performs a single beta reduction step."""
        if isinstance(self.function, Abstraction):
            return self.function.body.substitute(self.function.var.name, self.value)
        
        if not self.function.is_normal_form():
            try:
                return Application(self.function.beta_reduce_step(), self.value)
            except ReductionOnNormalForm:
                pass
        
        if not self.value.is_normal_form():
            try:
                return Application(self.function, self.value.beta_reduce_step())
            except ReductionOnNormalForm:
                pass
        
        raise ReductionOnNormalForm(term=self)

    def literal(self):
        return rf"({self.function.literal()}) ({self.value.literal()})"
    
    def has_free(self, name: str) -> bool:
        return self.function.has_free(name) or self.value.has_free(name)

# MARK: Helper Functions
def makeVar(name):
    return Variable(name)

# Test case to verify strict left-to-right behavior
test_expr = Application(
    Abstraction(
        Variable('x'),
        Application(
            Variable('x'),
            Variable('y')
        )
    ),
    Variable('z')
)