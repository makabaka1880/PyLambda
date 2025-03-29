# Created by Sean L. on Mar. 28
#
# Lambda Calculus Implementation
# models/exceptions.py
#
# Makabaka1880, 2025. All rights reserved.

class ReductionOnNormalForm(Exception):
    """Exception raised when attempting to reduce a lambda term that's already in normal form."""
    
    def __init__(self, term = None, message = "Reduction attempted on term in normal form"):
        self.term = term
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.args[0]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.term!r})"

class MismatchParenthesis(Exception):
    """Exception raised when a lambda literal contains mismatched parenthesis"""
    
    def __init__(self, literal = None, message = "Parenthesis mismatch detected while parsing"):
        self.literal = literal
        self.message = message
        super().__init__(message)
    
    def __str__(self):
        return self.args[0]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.term!r})"

class ParseError(Exception):
    """Exception raised when a lambda term cannot be parsed."""
    
    def __init__(self, literal = None, message="Error parsing lambda term"):
        self.literal = literal
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.args[0]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.literal!r})"

class FixedPointDetected(Exception):
    """Raised when consecutive reduction steps produce identical terms"""
    def __init__(self, term = None, message="Infinite loop detected: term reduces to itself"):
        self.term = term
        self.message = message
        super().__init__(message)
    
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.term!r})"

class InvalidTermError(Exception):
    """Exception raised when a lambda term is invalid or malformed."""
    
    def __init__(self, term=None, message="Invalid or malformed lambda term"):
        self.term = term
        self.message = message
        super().__init__(message)
    
    def __str__(self):
        return self.args[0]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.term!r})"