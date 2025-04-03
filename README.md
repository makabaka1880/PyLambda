# PyLambda

> **Latest Update**  
> Added automatic $\alpha$-conversion to avoid variable capture. Enabled by default.

A simple lambda calculus interpreter with beta-reduction capabilities.

## Deployment

XTermJS-based Website [Here ->](https://pylambda.makabaka1880.xyz/#learn-lambda-calculus)

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

### Lambda Term Literals

Pylambda accepts definition of lambda terms as follows:

#### Variables

Directly provide the identifier. You can enclose as many layers of parenthesis as you like.

```
[%0] [LMB? λ] TREE (x)
[%0] [DATA →] Variable x
```

#### Abstractions

Use Haskell's lambda syntax: backslash + bound variable + body. Currying is allowed.

```
[%0] [LMB? λ] TREE (\x. x)
[%0] [DATA →] Abstraction λ x
[%0] [DATA →]     └── x
[%1] [LMB? λ] TREE (\x. \y. x (y))
[%1] [DATA →] Abstraction λ x
[%1] [DATA →]     └── λ y
[%1] [DATA →]         └── Applicate
[%1] [DATA →]             ├── x
[%1] [DATA →]             └── y
```

#### Applications

Wrap values in parenthesis, like in a python lambda expression call.

```
[%2] [LMB? λ] TREE (\x. \y. x (y)) (\a. a) (b)
[%2] [DATA →] Application
[%2] [DATA →]     ├── Applicate
[%2] [DATA →]     │   ├── λ x
[%2] [DATA →]     │   │   └── λ y
[%2] [DATA →]     │   │       └── Applicate
[%2] [DATA →]     │   │           ├── x
[%2] [DATA →]     │   │           └── y
[%2] [DATA →]     │   └── λ a
[%2] [DATA →]     │       └── a
[%2] [DATA →]     └── b
```

### Command Keyword
PyLambda supports the following commands:

> **Sidenote**: If you run `help`, you get a list of currently available commands.

#### DEF / DEFINE

> Handle DEF command with session's DB.

Defines a variable using the assignment operator `:=` :

```
[%0] [LMB? λ] DEF func := (\x. \f. f (x));
[%0] [DONE →] Defined func
```

#### DEL / DELETE / RM

> Handle DEL command with optional regex.

Deletes a variable from runtime.

```
[%0] [LMB? λ] DEL C2;
[%0] [DONE →] Deleted entry C2
```

When used with the optional decorator, the command queries using regex. The following example deletes all variables with identifiers starting with `C` and followed by any character.

```
[%1] [LMB? λ] ?DEL C.;
[%1] [WARN →] Regex pattern is dangerous. Proceed with caution.
[%1] [SEC! →] Are you sure you want to proceed? (y/n): y
[%1] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
[%1] [DONE →] Deleted all matching entries for C.
```

#### DISPLAY / SHOW
> Shows mathematical representation of content of term.

As the docstring shows, it outputs a unicode-built mathematical formula for the term.

```
[%0] [LMB? λ] SHOW C1;
[%0] [INFO →] Terms matching C1 are found.
[%0] [DATA →] (λf. (λx. (f x)))
```

#### EXIT / Q / QUIT
> Exit the REPL.

```
[%0] [LMB? λ] EXIT;
[%0] [WARN →] Exiting REPL. Bye!
[%0] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
```

#### H / HELP
> Show dynamically generated help information.

```
[%0] [LMB? λ] HELP;
[%0] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
[%0] [DATA →] Available commands:
[%0] [DATA →] def, define: Handle DEF command with session's DB
[%0] [DATA →] del, delete, rm: Handle DEL command with optional regex
[%0] [DATA →] display, show: Shows mathematical representation of content of term.
[%0] [DATA →] exit, q, quit: Exit the REPL
[%0] [DATA →] h, help: Show dynamically generated help information
[%0] [DATA →] list, ls: Lists all terms in the database
[%0] [DATA →] lit, literal: Shows literal content of term in PyLambda literal
[%0] [DATA →] namespace, use: Handle namespace importing
[%0] [DATA →] red, reduce, run: Handle RED command with output variable
[%0] [DATA →] save: Handles namespace saving
[%0] [DATA →] tree: Method to output a string of a tree representation of term
```

#### LIST / LS
> Lists all terms in the database.

Defaults to querying the whole runtime base namespace:

```
[%0] [LMB? λ] LIST;
[%0] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
[%0] [DATA →] succ      (λn. (λf. (λx. (f ((n f) x)))))
[%0] [DATA →] C0                          (λf. (λx. x))
[%0] [DATA →] C1                      (λf. (λx. (f x)))
[%0] [DATA →] C2                  (λf. (λx. (f (f x))))
```

When used with the optional decorator, the command queries using regex. The following example shows all variables with identifiers starting with `C` and followed by any character.

```
[%1] [LMB? λ] ?LIST C.;
[%1] [WARN →] Empty literal returned from handler, skipping history insertion for %6.
[%1] [DATA →] C0                          (λf. (λx. x))
[%1] [DATA →] C1                      (λf. (λx. (f x)))
[%1] [DATA →] C2                  (λf. (λx. (f (f x))))
```

When used with the dot decorator, the command returns a list of available namespaces.

```
[%2] [LMB? λ] .LIST;
[%2] [DATA →] Available namespaces:
[%2] [DATA →]   numerals
[%2] [WARN →] Empty literal returned from handler, skipping history insertion for %2.
[%2] [DATA →] Namespace query done
```

#### LIT / LITERAL
> Shows literal content of term in PyLambda literal

Shows a term in it's literal form:

```
[%0] [LMB? λ] LIT C1;
[%0] [DATA →] (\f. (\x. f (x)))
```

When used with the optional decorator, the command queries using regex. The following example shows the literal of all variables with identifiers starting with `C` and followed by any character.

```
[%1] [LMB? λ] ?LIT C.;
[%1] [WARN →] Empty literal returned from handler, skipping history insertion for %1.
[%1] [DATA →] C0   (λf. (λx. x))
[%1] [DATA →] C1   (λf. (λx. (f x)))
[%1] [DATA →] C2   (λf. (λx. (f (f x))))
```

#### NAMESPACE / USE
> Handle namespace importing

Imports all variables in another namespace into the base namespace.

Here's an example. Originally we have this base namespace:
```
[%0] [LMB? λ] LIST;
[%0] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
[%0] [DATA →] I                                 (λx. x)
[%0] [DATA →] omega                         (λx. (x x))
```

Now we import a namespace called numerals which contains some useful tools for manipulating church numerals:

```
[%1] [LMB? λ] USE numerals;
[%1] [WARN →] Empty literal returned from handler, skipping history insertion for %1.
```

And now the base namespace contains these new variables:
```
[%2] [LMB? λ] LIST;
[%2] [WARN →] Empty literal returned from handler, skipping history insertion for %2.
[%2] [DATA →] I                                 (λx. x)
[%2] [DATA →] omega                         (λx. (x x))
[%2] [DATA →] C0                          (λf. (λx. x))
[%2] [DATA →] C1                      (λf. (λx. (f x)))
[%2] [DATA →] C2                  (λf. (λx. (f (f x))))
[%2] [DATA →] succ      (λn. (λf. (λx. (f ((n f) x)))))
```

Note that a namespace import **will** overwrite existing variables.

#### RED / REDUCE / RUN
> Handle RED command with output variable

Opens up the beta reduction REPL. For example, if I want to find the successor of 1, then:

```
[%0] [LMB? λ] RED succ (C1);
[%0] [INFO →] Reducing           ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
[%0] [BSTP →] β →               ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
[%0] [BET? β] 
```

After you see the beta prompt, you can either press enter:

```
[%0] [LMB? λ] RED succ (C1);
[%0] [INFO →] Reducing           ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
[%0] [BSTP →] β →               ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
[%0] [BET? β] beta
[%1] [BSTP →] β →                         (λf. (λx. (f (((λf. (λx. (f x))) f) x))))
[%1] [BET? β] 
```

And the REPL automatically inserts a beta in your place and performs one step of the reduction.

You can continue this until the reducer proved that this is the normal form or it reached a fixed point.

> TODO: Check for divergence.

Normal form reached:
```
[%0] [LMB? λ] RED succ (C1);
[%0] [INFO →] Reducing           ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
[%0] [BSTP →] β →               ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
[%0] [BET? β] beta
[%1] [BSTP →] β →                         (λf. (λx. (f (((λf. (λx. (f x))) f) x))))
[%1] [BET? β] beta
[%2] [BSTP →] β →                                   (λf. (λx. (f ((λx. (f x)) x))))
[%2] [BET? β] beta
[%3] [BSTP →] β →                                             (λf. (λx. (f (f x))))
[%3] [BET? β] beta
[%3] [DONE →] Reached normal form
[%3] [INFO →] Current literal: 
[%3] [DATA →] DEF %3 := (\f. (\x. f (f (x))))
```

Fixed point reached:

```
[%4] [LMB? λ] RED omega (omega);
[%4] [INFO →] Reducing                                    ((λx. (x x)) (λx. (x x)))
[%4] [BSTP →] β                                           ((λx. (x x)) (λx. (x x)))
[%4] [BET? β] beta
[%5] [BSTP →] β →                                         ((λx. (x x)) (λx. (x x)))
[%5] [DONE →] Reduction reached fixed point
[%5] [INFO →] Current literal: 
[%5] [DATA →] DEF %5 := (\x. x (x)) ((\x. x (x)))
```

#### SAVE
> Handles namespace saving

*FEATURE UNDER DEVELOPMENT*

#### TREE
> Method to output a string of a tree representation of term

```
[%0] [LMB? λ] TREE succ (C1);
[%0] [DATA →] Application
[%0] [DATA →]     ├── λ n
[%0] [DATA →]     │   └── λ f
[%0] [DATA →]     │       └── λ x
[%0] [DATA →]     │           └── Applicate
[%0] [DATA →]     │               ├── f
[%0] [DATA →]     │               └── Applicate
[%0] [DATA →]     │                   ├── Applicate
[%0] [DATA →]     │                   │   ├── n
[%0] [DATA →]     │                   │   └── f
[%0] [DATA →]     │                   └── x
[%0] [DATA →]     └── λ f
[%0] [DATA →]         └── λ x
[%0] [DATA →]             └── Applicate
[%0] [DATA →]                 ├── f
[%0] [DATA →]                 └── x
```

## Changelog
- **Apr. 3** Major fixes:
    - *repl.py* Fixed return type for `SHOW` command handler 
    - *parser.py* Fixed history marker (`%[0-9]+`) parsing
- **Apr. 4** Major additions:
    - *terms.db* Added standard namespace `numerals`, `booleans`, and `list`