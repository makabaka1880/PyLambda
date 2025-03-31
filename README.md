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

Directly provide the identifier.

```

### Command Keyword
PyLambda supports the following commands:

> **Sidenote**: If you run `help`, you get a list of currently available commands.

#### DEF / DEFINE

> Handle DEF command with session's DB.

Defines a variable:

```
[%0] [LMB? λ] DEF func := (\x. \f. f (x))
[%0] [DONE →] Defined func
```
