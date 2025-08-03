# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyLambda is a lambda calculus interpreter with beta-reduction capabilities, built in Python. It provides an interactive REPL for defining, manipulating, and reducing lambda terms.

## Development Commands

### Setup and Running
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
touch .env
echo 'DEFAULT_DB_PATH="terms.db"' > .env

# Run the REPL
python repl.py

# Run with Docker
docker build -t pylambda .
docker run -v $(pwd)/data:/app/data pylambda
```

### Testing
The project has minimal test infrastructure - `test.py` appears to be a stub file.

## Code Architecture

### Core Components

**Entry Point**: `repl.py` - Main REPL interface with command handlers and terminal interaction

**Parser**: `parser.py` - Parses lambda expressions from string literals into AST objects

**Model**: `models/model.py` - Defines the core lambda calculus AST:
- `Term` (abstract base class)  
- `Variable` - Variable terms (e.g., `x`)
- `Abstraction` - Lambda abstractions (e.g., `λx.body`)
- `Application` - Function applications (e.g., `f(x)`)

**Persistence**: `utils/persistence.py` - `TermDB` class for storing/loading lambda terms and namespaces

**History**: `utils/history.py` - `HistoryStore` for tracking REPL session history

**Colors**: `colors.py` - Terminal color formatting and UI labels

**Preprocessing**: `preproc.py` - Text normalization utilities

**Security**: `utils/security.py` - Input validation (regex pattern safety)

### Key Design Patterns

- **Visitor Pattern**: Term operations like substitution and beta-reduction are implemented as methods on `Term` subclasses
- **Database Abstraction**: `TermDB` handles SQLite persistence of lambda terms with namespace support
- **Command Pattern**: REPL commands are dispatched to handler functions based on keywords

### Lambda Calculus Features

- **Beta Reduction**: Step-by-step evaluation with interactive control
- **Alpha Conversion**: Variable renaming to avoid capture
- **Substitution**: Replace free variables with terms
- **Term Extraction**: Extract components from abstractions and applications
- **Namespaces**: Organize and import collections of predefined terms

### REPL Syntax

Lambda terms use Haskell-style syntax:
- Variables: `x`, `y`, `func_name`
- Abstractions: `\x. body` (currying supported: `\x. \y. body`)
- Applications: `func (arg)` with parentheses

## File Structure

- `repl.py` - Main REPL loop and command handlers
- `parser.py` - Lambda expression parsing logic
- `models/` - Core lambda calculus data structures
- `utils/` - Persistence, history, security utilities
- `data/` - SQLite database storage location
- `terms.db` - Default database file with predefined namespaces
- `.env` - Configuration (database path)

## Development Notes

- The codebase uses a custom AST representation rather than external lambda calculus libraries
- Terminal width detection includes server deployment markers for web interface integration
- Database schema supports hierarchical namespace organization
- No traditional unit testing framework - development relies on REPL-based testing
- Color output and formatting are integral to the user experience