# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# utils/sidefx.py
#
# Makabaka1880, 2025. All rights reserved.

import models.exceptions
import models.model

Term = models.model.Term

class SideFX(Term):
    """Base class for terms with side effects (e.g., logging, debugging)."""
    
    def __init__(self, term: Term):
        super().__init__()
        self.term = term

    def __repr__(self):
        return f"SideFX({self.term})"

    def substitute(self, target: str, replacement: Term) -> Term:
        return SideFX(self.term.substitute(target, replacement))

    def alpha_conversion(self, name: str) -> Term:
        return SideFX(self.term.alpha_conversion(name))

    def beta_reduce_step(self) -> Term:
        reduced = self.term.beta_reduce_step()
        print(f"[DEBUG] Reduction step: {self.term} → {reduced}")
        return SideFX(reduced)

    def is_normal_form(self) -> bool:
        return self.term.is_normal_form()

class STDINTerm(SideFX):
    pass