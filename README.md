# PyLambda

> **Latest Update**  
> Added automatic $\alpha$-conversion to avoid variable capture. Enabled by default.

A simple lambda calculus interpreter with beta-reduction capabilities.

## Deployment

### Command-Line Interface

To run PyLambda from the command line:

```zsh
pip install -r requirements.txt
touch .env
echo 'PATH/TO/DB' > .env
python repl.py
```

### Docker Support

Docker support is currently under development.

## REPL Syntax

Commands in the REPL consist of a keyword and arguments. Keywords are case-insensitive, but arguments, especially those containing identifiers, are case-sensitive.

PyLambda supports the following commands:

### `DEF`

Defines a variable and stores it in the local SQLite database.

**Usage:**
```text
λ > DEF func := (\x. \y. x (y))
```

This defines the lambda abstraction $\lambda x.\ \lambda y.\ x\ y$. In PyLambda, bound variables use Haskell-style syntax (backslash + identifier) for declaration.

---

### `RED`

Performs $\beta$-reduction on a given application or abstraction.

**Usage:**
```text
λ > RED (\x. \y. x) (a)
```

This opens the **beta-reduction REPL** interface:

```text
λ > RED (\x. \y. x) (a)
Reducing: ((\x. ((\y. (x))))) (a)
Step 0: (λx. (λy. x)) a
β > 
Step 1: (λy. a)
β > 
Reached normal form
λ > 
```

You can save the reduced form to a new variable:

```text
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

Alternatively, save the result during the beta-reduction process:

```text
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

To exit an unwanted recursion, use the `exit` command:

```text
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

Example with Church numerals:

```text
λ > DEF ChurchSucc := (\n. \f. \x. f (n (f) (x)) )
λ > DEF C1 := (\f. \x. f(x))
λ > RED ChurchSucc (C1) > C2
Reducing: (ChurchSucc) ((\f. ((\x. ((f) (x))))))
Step 0: ChurchSucc (λf. (λx. f x))
β >
Reached normal form
Auto-saved as "C2"
Saved final result as "C2"
λ > SHOW ChurchSucc; SHOW C1; SHOW C2;
(λn. (λf. (λx. f n f x)))
(λf. (λx. f x))
ChurchSucc (λf. (λx. f x))
λ >
```

---

### `LIST` / `LS`

Lists all terms stored in the database.

**Usage:**
```text
λ + ls
C3: (λf. (λx. (f (f (f x)))))
IF: (λs. (λa. (λb. ((s a) b))))
TRUE: (λx. (λy. x))
FALSE: (λx. (λy. y))
omega_x: (λx. (x x))
Omega_x: ((λx. (x x)) (λx. (x x)))
FixedPointCombinatorExample: ((λx. (x x)) (λx. (x x)))
C1: (λf. (λx. (f x)))
succ: (λn. (λf. (λx. (f ((n f) x)))))
C2: (λf. (λx. (f (f x))))
```

`LIST` 
---

### `SHOW` / `DISPLAY`

Displays the content of a variable using Unicode to represent the lambda abstraction.

**Usage:**
```text
λ + ls
C3: (λf. (λx. (f (f (f x)))))
IF: (λs. (λa. (λb. ((s a) b))))
TRUE: (λx. (λy. x))
FALSE: (λx. (λy. y))
omega_x: (λx. (x x))
Omega_x: ((λx. (x x)) (λx. (x x)))
FixedPointCombinatorExample: ((λx. (x x)) (λx. (x x)))
C1: (λf. (λx. (f x)))
succ: (λn. (λf. (λx. (f ((n f) x)))))
C2: (λf. (λx. (f (f x))))
λ + show C2
(λf. (λx. (f (f x))))
λ +
```

---

### `EXIT`

Exits the REPL interface.

---

### `HELP`

This command is not yet implemented.

