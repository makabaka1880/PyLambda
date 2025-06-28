# PyLambda

[![Build and Push Image](https://github.com/makabaka1880/PyLambda/actions/workflows/build_docker.yml/badge.svg)](https://github.com/makabaka1880/PyLambda/actions/workflows/build_docker.yml)
[![CD Pipeline](https://github.com/makabaka1880/PyLambda/actions/workflows/cd_pipeline.yml/badge.svg)](https://github.com/makabaka1880/PyLambda/actions/workflows/cd_pipeline.yml)

> **Latest Update**  
> Added methods to directly manipulate terms like extractions and conversions

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
[%0] [INFO →] Reducing          ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
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
[%0] [INFO →] Reducing          ((λn. (λf. (λx. (f ((n f) x))))) (λf. (λx. (f x))))
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

Pass the name of the namespace you want to save.

```
[%0] [LMB? λ] ls
[%0] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
[%0] [DATA →] HI                                                      (hello world)

[%1] [LMB? λ] save hello_world;
hello_world
[%1] [WARN →] Empty literal returned from handler, skipping history insertion for %1.
```

Now in another run:

```
[%0] [LMB? λ] ls
[%0] [WARN →] Empty literal returned from handler, skipping history insertion for %0.
[%0] [DATA →] A                                               (λh. (λg. (g (h g))))
[%0] [DATA →] B                                                   (λj. (λk. (j k)))

[%1] [LMB? λ] .ls
[%1] [DATA →] Available namespaces:
[%1] [DATA →]   booleans
[%1] [DATA →]   list
[%1] [DATA →]   combinators
[%1] [DATA →]   numerals
[%1] [DATA →]   hello_world
[%1] [WARN →] Empty literal returned from handler, skipping history insertion for %1.
[%1] [DATA →] Namespace query done

[%2] [LMB? λ] use hello_world;
[%2] [WARN →] Empty literal returned from handler, skipping history insertion for %2.

[%3] [LMB? λ] ls
[%3] [WARN →] Empty literal returned from handler, skipping history insertion for %3.
[%3] [DATA →] A                                                (λh. (λg. (g (h g))))
[%3] [DATA →] B                                                    (λj. (λk. (j k)))
[%3] [DATA →] HI                                                       (hello world)
```

#### TYPE
> Shows the type of term

For variables, it outputs `TYPE <VAR>`

```
[%0] [LMB? λ] TYPE x;
[%0] [DATA →] TYPE <VAR>
```

For abstractions it is `TYPE <ABSTRACTION>`

```
[%1] [LMB? λ] TYPE (\x. x);
[%1] [DATA →] TYPE <ABSTRACTION>
```

For applications it return `TYPE <APPLICATION>`

```
[%2] [LMB? λ] TYPE x (x);
[%2] [DATA →] TYPE <APPLICATION>
```

#### EXTRACT_BODY / BODY
> Extracts the body term of an lambda abstraction.

```
[%0] [LMB? λ] EXTRACT_BODY (\var. body);
[%0] [DATA →] body
```

It can be piped out to an variable using the `>` operator:

```
[%1] [LMB? λ] EXTRACT_BODY (\var. body) > BODY_TERM;
[%1] [DATA →] body
[%1] [DATA →] Saving body to BODY_TERM

[%2] [LMB? λ] SHOW BODY_TERM;
[%2] [INFO →] Terms matching BODY_TERM are found.
[%2] [DATA →] body
```

Note that this raises an error when applying on a non-abstraction term.

```
[%3] [LMB? λ] EXTRACT_BODY func (val);
[%3] [ERR! →] Term is not of type Abstraction
```

#### EXTRACT_VARIABLE / VAR
> Extracts the bound variable of a lambda abstraction.

```
[%0] [LMB? λ] EXTRACT_VARIABLE (\var. body);
[%0] [DATA →] var
```

It can be piped out to a variable using the `>` operator:

```
[%1] [LMB? λ] EXTRACT_VARIABLE (\var. body) > BOUND_VAR;
[%1] [DATA →] var
[%1] [DATA →] Saving var to BOUND_VAR

[%2] [LMB? λ] SHOW BOUND_VAR;
[%2] [INFO →] Terms matching BOUND_VAR are found.
[%2] [DATA →] var
```

Note that this raises an error when applying on a non-abstraction term.

```
[%3] [LMB? λ] EXTRACT_VARIABLE func (val);
[%3] [ERR! →] Term is not of type Abstraction
```

#### EXTRACT_FUNCTION / FUNC
> Extracts the function part of an application.

```
[%0] [LMB? λ] EXTRACT_FUNCTION func (arg);
[%0] [DATA →] func
```

It can be piped out to a variable using the `>` operator:

```
[%1] [LMB? λ] EXTRACT_FUNCTION func (arg) > FUNC_PART;
[%1] [DATA →] func
[%1] [DATA →] Saving func to FUNC_PART

[%2] [LMB? λ] SHOW FUNC_PART;
[%2] [INFO →] Terms matching FUNC_PART are found.
[%2] [DATA →] func
```

Note that this raises an error when applying on a non-application term.

```
[%3] [LMB? λ] EXTRACT_FUNCTION (\x. x);
[%3] [ERR! →] Term is not of type Application
```
#### EXTRACT_VALUE / VAL
> Extracts the argument part of an application.

```
[%0] [LMB? λ] EXTRACT_VALUE func (arg);
[%0] [DATA →] arg
```

It can be piped out to a variable using the `>` operator:

```
[%1] [LMB? λ] EXTRACT_VALUE func (arg) > ARG_PART;
[%1] [DATA →] arg
[%1] [DATA →] Saving arg to ARG_PART

[%2] [LMB? λ] SHOW ARG_PART;
[%2] [INFO →] Terms matching ARG_PART are found.
[%2] [DATA →] arg
```

Note that this raises an error when applying on a non-application term.

```
[%3] [LMB? λ] EXTRACT_VALUE (\x. x);
[%3] [ERR! →] Term is not of type Application
```

#### ALPHA_CONVERT / ALPHA / RENAME
> Computes alpha conversion on the abstraction.

The command utilizes the left-assignment `<` operator. The new bound variable is on the right.

```
[%0] [LMB? λ] ALPHA_CONVERT (\a. a) < x;
[%0] [DATA →] (λx. x)
```

When the new bound var collides with a identifier in the base namespace, the REPL raises and error:

```
[%1] [LMB? λ] ALPHA_CONVERT (\a. a) < HI;
[%1] [ERR! →] Exception caught while catching for identifier name clash
[%1] [ERR! →] Identifier name clash detected
[%1] [DATA →] (λHI. HI)
```

You can use the smart decorator `+` to rename the bound variable to an available name:

```
[%2] [LMB? λ] +ALPHA_CONVERT (\a. a) < HI;
[%2] [DATA →] (λHI'. HI')
```

Or the force decorator `!` to forcefully perform the conversion

```
[%3] [LMB? λ] !ALPHA_CONVERT (\a. a) < HI;
[%3] [WARN →] Possibility of identifier clash overriden with decorator !: identifier HI
[%3] [DATA →] (λHI. HI)
```
#### SUBSTITUTE / SUB / SUBSTITUTION
> Handle substitution of term

The command uses the left-assignment operator `>`. Seperate the target identifier and replacement term with a comma:

```
[%0] [LMB? λ] SHOW HI;
[%0] [INFO →] Terms matching HI are found.
[%0] [DATA →] (hello world)

[%1] [LMB? λ] SUBSTITUTE HI < hello, hi;
[%1] [DATA →] (hi world)
```

Or scan the base namespace for identifiers that collides with any free variables in the target term:

```
[%2] [LMB? λ] DEF world := (\a. a);
[%2] [DONE →] Defined world

[%3] [LMB? λ] SUBSTITUTE HI;
[%3] [DATA →] (hello (λa. a))
```

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
- **Apr. 3**
    - COMMIT cf70c7b15545076fb3279faa3471e8dc65536eda:
        - *repl.py* Fixed return type for `SHOW` command handler 
        - *parser.py* Fixed history marker (`%[0-9]+`) parsing
- **Apr. 4**
    - COMMIT 26ab8c620221280b088b6fae86ff2064f39ed8c7
        - *terms.db* Added standard namespace `numerals`, `booleans`, and `list`
    - COMMIT 6453977419bb1335d445394c3920bf41f70ba3b7
        - *terms.db* Added standard namespace `combinators`
        - *repl.py* Done command handler for command `USE`
    - COMMIT 474afffe0d057df5d5973623334afdcbe89edc85
        - *terms.db* Added terms `ADD`, `MINUS`, `PRED`, `TIME` to std namespace `numerals`
    - COMMIT a539533cbf900cc303378bc19e5945589aed6347
        - *repl.py* Added methods for `EXTRACT_BODY`, `EXTRACT_VARIABLE`, `EXTRACT_FUNCTION`, `EXTRACT_VALUE`, `ALPHA_CONVERT` and introduced smart decorator `+`
        - *README.md* Added manual for `EXTRACT_BODY`, `EXTRACT_VARIABLE`, `EXTRACT_FUNCTION`, `EXTRACT_VALUE`, `ALPHA_CONVERT`
    - COMMIT 26dd5f590a727d17999e77d6acc56b3a978ef851
        - *README.md* Updated `latest` blockquote
        - *WEB* Added manual that clones from this README
    - COMMIT f7e5c30e72306d024e53f038611780932e5fb2f5
        - *repl.py* Added methods for `SUBSTITUTION`
        - *README.md* Added manual for command `SUBSTITUTION`
    - COMMIT f96189166efda24fd5f93a0b60f05fa5aa31fbc2
        - *repl.py* Update methods and marker comments for easier deployment
        - *WEB* Updated deployment script
- **Apr. 5**
    - COMMIT 75408ee5b08ef1e774c076aa6060a3e80a0a9a24
        - *.github/workflows/cd_pipeline.yml* Added gh action to automatically trigger deployment on push
        - *WEB* Updated deployment script
    - COMMIT a4e6c2503ddb36283c3d2d2c5398c6455a6cec66
        - *.github/workflows/cd_pipeline.yml* Debug
- **Apr. 12**
    - COMMIT 
        - *WEB* and *repl.py* Updated port number from 5000 -> 5050