# PyLambda

> Known Issues:
> - The lambda abstraction $\lambda z.\; (\lambda y.\; \lambda z.\; y\; (y\; z))\; (\lambda y.\; \lambda z.\; y\; (y\; z))\; z$ is unable to be reducted correctly. Literal: `(\z. (((\y. ((\z. ((y) ((y) (z))))))) (((\y. ((\z. ((y) ((y) (z))))))) (z))))`

A implementation of a simple lambda calculus intepreter, complete with beta-reduction features.

## Deployment

### Command-line

```zsh
pip install -r requirements.txt
touch .env
echo 'PATH/TO/DB' > .env
python repl.py
```

### Docker
Under development

## REPL Syntax

A command is consisted of a keyword and arguments. Keywords are case-insensitive, but args, given that they contains identifiers, are.

Below are the 4 keywords PyLambda support

### DEF
Defines a variable and stores it in the local sqlite3 db.

Usage:
```
λ > DEF func := (\x. \y. x (y))
```

This defines the lambda abstraction $\lambda x.\ \lambda y.\ x\ y$. In PyLambda, bound variables uses haskell's syntax (backslash + identifier) to declare.

Due to technical limitations, here's some points worth noting:

1. Values of applications must be inclosed in parenthesis. When values are passed to curried parameters, the function body must also be enclosed in parenthesis.
    - **Correct** `func (value)` or `(func (value1)) (value2)`
    - **Incorrect** `func value` or `func (value1) (value2)`

### RED
Performs $\beta$-reduction on a given application or abstraction.

Usage:
```
λ > RED (\x. \y. x) (a)
```

This opens up an other REPL interface: the **beta-reduction REPL**.

```
λ > RED (\x. \y. x) (a)
Reducing: ((\x. ((\y. (x))))) (a)
Step 0: (λx. (λy. x)) a
β > 
Step 1: (λy. a)
β > 
Reached normal form
λ > 
```

You can chose to store the reduced form of the application to a new variable:

```
λ > RED (\x. \y. x) (a) > result
Reducing: ((\x. ((\y. (x))))) (a)
Step 0: (λx. (λy. x)) a
β >
Step 1: (λy. a)
β >
Reached normal form
Auto-saved as "result"
Saved final result as "result"
λ >
```

Or via commands in the beta-reduction interface:

```
λ > RED (\x. \y. x) (a)
Reducing: ((\x. ((\y. (x))))) (a)
Step 0: (λx. (λy. x)) a
β >
Step 1: (λy. a)
β > save > result
Saved current term as "result"
Step 1: (λy. a)
β >
Reached normal form
λ >
```

You can also quit to jump out of an unwanted recursion:

```
λ > DEF omega := (\x. x (x))
λ > RED omega (omega)
Reducing: ((\x. ((x) (x)))) ((\x. ((x) (x))))
Step 0: (λx. x x) (λx. x x)
β >
Step 1: (λx. x x) (λx. x x)
β >
Step 2: (λx. x x) (λx. x x)
β > exit > fixedPointCombinatorExample
Saved as "fixedPointCombinatorExample"
λ >
```

### SHOW
Shows the content of a variable using unicode as a mathematical lambda abstraction expression.

```
λ > DEF ChurchSucc := (\n. \f. \x. f (n (f (x) ) ) )
λ > DEF C1 := (\f. \x. f(x))
λ > RED ChuchSucc (C1) > C2
Reducing: (ChuchSucc) ((\f. ((\x. ((f) (x))))))
Step 0: ChuchSucc (λf. (λx. f x))
β >
Reached normal form
Auto-saved as "C2"
Saved final result as "C2"
λ > SHOW ChurchSucc; SHOW C1; SHOW C2;
(λn. (λf. (λx. f n f x)))
(λf. (λx. f x))
ChuchSucc (λf. (λx. f x))
λ >
```

### EXIT
Leaves the interface

### HELP
Not yet implemented
