# PyLambda Architecture Overview

## Executive Summary

PyLambda is a lambda calculus interpreter implemented in Python with a clean object-oriented architecture centered around an AST-based representation. The system follows standard language interpreter patterns with lexing/parsing, AST evaluation, and REPL interaction layers.

## Inheritance Hierarchy

### Core Lambda Calculus AST (`models/model.py`)

```
Term (Abstract Base Class)
├── Variable - Represents lambda variables (e.g., x, y)
├── Abstraction - Lambda abstractions (λx.body)
└── Application - Function applications (f x)
```

**Design Pattern**: Classic Composite Pattern with Visitor-style operations
- All terms implement: `substitute()`, `beta_reduce_step()`, `alpha_conversion()`, `literal()`, `tree_str()`
- Each subclass provides type-specific implementations
- Polymorphic dispatch enables uniform term manipulation

### Exception Hierarchy (`models/exceptions.py`)

```
Exception
├── ReductionOnNormalForm - Term already fully reduced
├── MismatchParenthesis - Parser syntax errors  
├── ParseError - General parsing failures
├── FixedPointDetected - Infinite reduction loops
├── UnexpectedArgsError - Command argument errors
├── IdentifierNameClash - Variable name conflicts
├── InvalidTermError - Malformed terms
└── UserCancelledOperation - User interruption
```

**Design**: Granular exception types enable precise error handling and user feedback

## Call Stack & Control Flow

### Primary Execution Path

1. **Entry Point**: `repl.py` → `REPLSession.run()`
2. **Input Processing**: `normalize_blank()` → `parse_command()` → `CommandHandler.execute()`
3. **Term Parsing**: `parse_term()` → `parse_lambda()` → AST construction
4. **Operations**: Term methods (`substitute`, `beta_reduce_step`) → Result generation
5. **Output**: `REPLInterface` display methods → Terminal

### Beta Reduction Flow

```
Application.beta_reduce_step()
├── If function is Abstraction → Direct substitution
├── Else try reducing function first
└── Fallback to reducing argument (leftmost-outermost)
```

### Command Dispatch Pattern

```
CommandHandler.execute()
├── Keyword lookup in command_map
├── Handler method call with arguments
├── Database/History operations
└── Result formatting via REPLInterface
```

## Type System

### Type Annotations Coverage
- **Moderate coverage**: Core functions annotated with return types
- **Models**: Comprehensive typing with `Term`, `Variable`, etc.
- **Utilities**: Basic annotations (`Optional`, `List`, `Tuple`)
- **Missing**: Many REPL functions lack parameter type hints

### Key Type Patterns
```python
def parse_lambda(literal: str) -> Term
def substitute(self, target: str, replacement: "Term") -> "Term"  
def get_all_terms(...) -> List[tuple[str, Term]]
```

**Forward References**: Uses string literals for self-referential types (`"Term"`)

## API Exposure & Interfaces

### External Dependencies
- **SQLite3**: Database persistence (no external DB required)
- **readline**: Command-line editing
- **requests**: Optional web API calls (deployment feature)
- **subprocess**: Terminal width detection
- **dotenv**: Configuration management

### Internal API Boundaries

**Parser Module** (`parser.py`):
```python
parse_term(literal: str, db: TermDB, history: HistoryStore) -> Term
parse_lambda(literal: str) -> Term
```

**Persistence Layer** (`utils/persistence.py`):
```python
class TermDB:
    get_term(identifier: str) -> Optional[Term]
    insert_term(identifier: str, term: Term) -> None
    get_all_terms(...) -> List[tuple[str, Term]]
```

**History Management** (`utils/history.py`):
```python
class HistoryStore:
    insert(index: int, literal: str) -> None
    fetch(index: int) -> Term
```

### Web Integration Points
- Server deployment markers in `repl.py:33` for web terminal
- HTTP endpoint calls for terminal dimensions
- Deployment webhook trigger via GitHub Actions

## Technology Stack

### Core Technologies
- **Python 3.12+**: Main implementation language
- **SQLite3**: Embedded database for term/namespace persistence
- **Docker**: Containerization support (development stage)

### Python Libraries
- **Standard Library**: `sqlite3`, `readline`, `subprocess`, `os`, `re`
- **Third-party**: `python-dotenv`, `pyreadline` (Windows compatibility), `requests`

### Development & Deployment
- **GitHub Actions**: Automated deployment pipeline
- **Docker**: Cross-platform containerization
- **Environment Variables**: Configuration via `.env` files

## Architectural Strengths

### Clean Separation of Concerns
- **Model**: Pure lambda calculus operations
- **View**: Terminal interface and formatting  
- **Controller**: REPL command processing
- **Persistence**: Database abstraction layer

### Extensibility Points
- **Command System**: Easy to add new REPL commands via `command_map`
- **Term Operations**: New lambda calculus features via Term subclass methods
- **Namespace System**: Modular term organization and imports

### Performance Considerations
- **SQLite**: Efficient term storage and regex-based queries
- **In-memory History**: Fast session-based term references
- **Lazy Evaluation**: Terms only reduced on explicit user request

## Architectural Concerns

### Type Safety
- **Partial Coverage**: Missing type hints in many functions
- **Runtime Checks**: Limited validation of Term AST integrity

### Error Handling
- **Granular Exceptions**: Good error categorization
- **User Experience**: Clear error messages but could be more contextual

### Scalability
- **Single-threaded**: No concurrency support for large reductions
- **Memory Usage**: No garbage collection for complex term trees

## Deployment Architecture

### Modes of Operation
1. **CLI Mode**: Direct Python execution with terminal interface
2. **Docker Mode**: Containerized with volume mounting for persistence  
3. **Web Mode**: Server deployment with HTTP API integration

### Configuration Management
- **Environment Variables**: Database paths, server settings
- **Docker Volumes**: Persistent data storage
- **Deployment Hooks**: Automated updates via webhook triggers