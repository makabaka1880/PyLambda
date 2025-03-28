# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# models/model.py
#
# Makabaka1880, 2025. All rights reserved.

import models.exceptions

class Term:
    """Base class for any term found in a lambda abstraction.
    """
    def eval(self):
        raise NotImplementedError('`eval` method not yet implemented for class `Term`')
    
    def substitute(self, target: str, replacement: "Term") -> "Term":
        """
        Substitute all free occurrences of the variable named `target` in this term with `replacement`.

        Parameters:
            target (str): The variable name to be replaced.
            replacement (Term): The term that will replace occurrences of `target`.

        Returns:
            Term: A new term with the substitution applied.
        
        For a Variable:
        - If the variable's name matches `target`, return `replacement`.
        - Otherwise, return the variable unchanged.
        
        For an Abstraction:
        - If the bound variable's name is the same as `target`, return the abstraction unchanged.
        - Otherwise, recursively substitute in the body and return a new Abstraction with the same bound variable.
        
        For an Application:
        - Substitute in both the function and the argument, and return a new Application.
        """
        raise NotImplementedError("Substitute method not implemented.")
    
    def alpha_conversion(self, name: str) -> "Term":
        """Performs an alpha conversion on the term.
        
        Parameter:
            name (str): The name the bound variable is going to be renamed to.
            
        Returns:
            A new term with the bound variable renamed to `name`.
            If no variables are present, returns the term unchanged.
        """
        raise NotImplementedError("Alpha conversion method not implemented.")
    
    def beta_reduce_step(self) -> "Term":
        """
        Perform a single beta reduction step on the term.
        
        Returns:
            A new Term representing the result of one beta reduction step.
            If no reduction is possible, returns the term unchanged.
        
        Behavior:
            - If the term is an Application where the function is an Abstraction,
            then perform the substitution (i.e., beta reduction).
            - Otherwise, try to beta reduce the function part or the argument part.
        """
        
        raise NotImplementedError("beta_reduce_step not implemented")

    def is_normal_form(self) -> bool:
        """
        Checks if a term is in normal form (i.e., cannot be reduced further).
        """
        raise NotImplementedError('Normal Form detection not yet implemented in this term')

    def literal(self) -> str:
        raise NotImplementedError('literal representation not yet implemented')
    
class Variable(Term):
    name: str
    
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return self.name
    
    def is_normal_form(self):
        return True
    
    def alpha_conversion(self, name):
        return self
    
    def substitute(self, target, replacement):
        if self.name == target:
            return replacement
        else:
            return self
    
    def beta_reduce_step(self):
        raise models.exceptions.ReductionOnNormalForm(term = self)
    
    def literal(self):
        return self.name

class Abstraction(Term):
    var: Variable
    body: Term
    
    def __init__(self, var, body):
        super().__init__()
        self.var = var
        self.body = body
        
    def __repr__(self):
        return f"(λ{self.var}. {self.body})"
    
    def is_normal_form(self):
        return self.body.is_normal_form()
    
    def alpha_conversion(self, name):
        return Abstraction(makeVar(name), self.body)
    
    def substitute(self, target: str, replacement: Term) -> Term:
        if self.var.name == target:
            return self  # Bound variable ≠ free variable → no substitution
        return Abstraction(self.var, self.body.substitute(target, replacement))

    def beta_reduce_step(self) -> 'Abstraction':
        if self.is_normal_form():
            raise models.exceptions.ReductionOnNormalForm(term = self)
        
        return Abstraction(self.var, self.body.beta_reduce_step())
    
    def literal(self):
        return rf"(\{self.var.literal()}. ({self.body.literal()}))"
    
class Application(Term):
    function: Term
    value: Term
    
    def __init__(self, function, value):
        super().__init__()
        self.function = function
        self.value = value
        
    def __repr__(self):
        return f"{self.function} {self.value}"

    def is_normal_form(self):
        if isinstance(self.function, Abstraction):
            return False  # Applications with an abstraction as function can reduce
        return self.function.is_normal_form() and self.value.is_normal_form()

    
    def alpha_conversion(self, name):
        return Application(self.function.alpha_conversion(name), self.value)
    
    def substitute(self, target, replacement):
        return Application(self.function.substitute(target, replacement), self.value.substitute(target, replacement))

    def beta_reduce_step(self):
        if isinstance(self.function, Abstraction):
            return self.function.body.substitute(self.function.var.name, self.value)
        
        if not self.function.is_normal_form():
            return Application(self.function.beta_reduce_step(), self.value)
        
        if not self.value.is_normal_form():
            return Application(self.function, self.value.beta_reduce_step())
        
        raise models.exceptions.ReductionOnNormalForm(term = self)

    def literal(self):
        return rf"({self.function.literal()}) ({self.value.literal()})"
    
# MARK: Helper Methods
def makeVar(name):
    return Variable(name)