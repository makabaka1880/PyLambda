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
[%0] [LMB? λ] DEF func := (\x. \f. f (x))
[%0] [DONE →] Defined func
```

#### DEL / DELETE / RM
