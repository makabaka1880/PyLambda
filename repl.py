# Created by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# repl/repl.py
# 
# Makabaka1880, 2025. All rights reserved.

import readline
from models.model import Term, Abstraction, Variable, Application
from preproc import normalize_blank
from parser import *
from models.exceptions import *
from utils.history import HistoryStore
from utils.persistence import TermDB
from colors import italic_text, bold_text, LABELS, COLORS, color_text, IO_label, status_label
from utils.security import check_for_dangerous_regex_pattern
import os
import subprocess
import re

counter = 0

def width():
    """Get the width of the terminal window"""
    result = subprocess.run(['tput', 'cols'], stdout=subprocess.PIPE)
    return int(result.stdout.decode().strip())

def filler(width, *text, regard_labels: bool = True):
    """Width of fillers needed to fill a line of certain width with text"""
    """Return a string of spaces to fill the line"""
    returned =  (width - sum(len(t) for t in text) - len(text) + 1)
    if regard_labels:
        return returned - 13 - len(str(counter))
    else:
        return returned

class REPLSession:
    def __init__(self):
        self.db: TermDB = TermDB()
        self.history: HistoryStore = HistoryStore()
        self.current_term: Term = None
        self.running: bool = True
        self.output_var: Term = None
        self._init_standard_library()

    def _init_standard_library(self):
        """Store built-in terms in DB"""
        std_terms = {
        }
        
        for name, term in std_terms.items():
            self.db.insert_term(name, term)
class REPLInterface:
    """User interface components"""
    
    @staticmethod
    def get_lambda_prompt() -> str:
        return f"{IO_label('lambda_prompt', counter)} "
        
    @staticmethod
    def get_alpha_prompt() -> str:
        return f"{IO_label('alpha_prompt', counter)} "
    
    @staticmethod
    def get_beta_prompt() -> str:
        return f"{IO_label('beta_prompt', counter)} "
    
    @staticmethod
    def get_security_prompt() -> str:
        return f"{IO_label('security_prompt', counter)} "
        
    @classmethod
    def show_warning(cls, message):
        for line in str(message).splitlines():
            print(f"{IO_label('warning', counter)} {line}")
        
    @classmethod
    def print_raw(cls, item):
        for line in str(item).splitlines():
            print(f"{IO_label('data', counter)} {line}")

    @classmethod
    def log_item(cls, message):
        for line in str(message).splitlines():
            print(f"{IO_label('info', counter)} {line}")
        
    @classmethod
    def show_error(cls, message):
        for line in str(message).splitlines():
            print(f"{IO_label('error', counter)} {line}")

    @classmethod
    def show_success(cls, message, end='\n'):
        for line in str(message).splitlines():
            print(f"{IO_label('success', counter)} {line}", end=end)

    @classmethod
    def show_beta_reduction_step(cls, term):
        for line in str(term).splitlines():
            print(f"{IO_label('beta_reduction_step', counter)} β →{filler(width(), line, ' b -') * ' '}{line}")
            
    @classmethod
    def show_alpha_reduction_step(cls, term):
        for line in str(term).splitlines():
            print(f"{IO_label('alpha_conversion_step', counter)} α →{filler(width(), line, ' a -') * ' '}{line}")
    

interface = REPLInterface()

class CommandHandler:
    """Handle different REPL commands"""
    def __init__(self, session):
        self.session = session
        self.command_map = {
            # Original commands (case-insensitive)
            'def': self.handle_def,
            'red': self.handle_red,
            'show': self.handle_show,
            'tree': self.handle_tree,
            'lit': self.handle_literal,
            'help': self.handle_help,
            'list': self.handle_list,
            'exit': self.handle_exit,
            'del': self.handle_delete,
            'use': self.handle_namespace_use,
            'save': self.handle_save_namespace,
            
            # Shorthand aliases
            'ls': self.handle_list,      # list
            'rm': self.handle_delete,    # delete
            'h': self.handle_help,       # help
            'q': self.handle_exit,       # exit
            'quit': self.handle_exit,    # exit
            
            # Full-length alternatives
            'define': self.handle_def,
            'reduce': self.handle_red,
            'literal': self.handle_literal,
            'delete': self.handle_delete,
            'namespace': self.handle_namespace_use,
            # Common alternatives
            'run': self.handle_red,      # alternative to reduce
            'display': self.handle_show  # alternative to show
        }
        
    def _resolve_reference(self, identifier: str) -> Term:
        if identifier.startswith('%'):
            try:
                return self.session.history.fetch(int(identifier[1:]))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid history reference {identifier}") from e
        return None

    def execute(self, command, decorator=None):
        """Execute a parsed command"""
        keyword, args = command
        handler = self.command_map.get(keyword.lower(), self.handle_unknown)
        return handler(args, decorator)

    def handle_def(self, args, decorator=None):
        """Handle DEF command with session's DB"""
        forced = (decorator == '!')
        try:
            identifier, literal = args.split(':=', 1)
            identifier = identifier.strip()
            # Access DB via session
            term = parse_term(literal)
            self.session.db.insert_term(identifier, term)
            return f"Defined {identifier}", term
            
        except ValueError:
            raise ParseError("Invalid DEF syntax")

    def handle_red(self, args, decorator=None):
        """Handle RED command with output variable"""
        forced = (decorator == '!')
        identifier = args.strip()
        output_var = None
        
        if '>' in identifier:
            parts = identifier.split('>', 1)
            term_part = parts[0].strip()
            output_var = parts[1].strip()
        else:
            term_part = identifier

        # Store output_var in session
        self.session.output_var = output_var

        if term := self.session.db.get_term(term_part):
            self.session.current_term = term
        elif term_part.startswith('%'):  # Check if it's a history reference
            try:
                self.session.current_term = self.session.history.fetch(int(term_part[1:]))
            except KeyError:
                raise ValueError(f"History entry {term_part} not found")
        else:
            self.session.current_term = parse_term(term_part)

        return f"{bold_text('Reducing')}{' ' * filler(width(), 'Reducing', str(self.session.current_term))}{str(self.session.current_term)}", term

    def handle_literal(self, args, decorator=None):
        """Shows content of term in PyLambda literal"""
        forced = (decorator == '!')
        identifier = args.strip().split()[0]
        if term := self.session.db.get_term(identifier) \
            or self._resolve_reference(identifier):
            return term.literal(), term
        return None, None
    
    def handle_tree(self, args, decorator=None):
        """Method to output a string of a tree representation of term"""
        forced = (decorator == '!')
        identifier = args.strip().split()[0]
        if term := self.session.db.get_term(identifier) \
            or self._resolve_reference(identifier):
            return term.tree_str(), term
        return None, None
    
    def handle_delete(self, args, decorator=None):
        """Handle DEL command with optional regex"""
        forced = (decorator == '!')
        identifier = args.strip().split()[0]
        if not forced:
            if check_for_dangerous_regex_pattern(identifier):
                interface.show_warning("Regex pattern is dangerous. Proceed with caution.")
                print(interface.get_security_prompt(), end= '')
                if input("Are you sure you want to proceed? (y/n): ").strip().lower() != 'y':
                    raise UserCancelledOperation("Operation cancelled by user")
        if terms := self.session.db.get_all_terms(identifier, forced=forced):
            # Delete all matching terms
            for name, term in terms:
                self.session.db.delete_terms(name, regex=(not forced))
            if forced:
                return f"Deleted entry {identifier}", terms[0][1]
            else:
                return f"Deleted all matching entries for {identifier}", None
            
        raise ValueError(f"Identifier {italic_text(identifier)} not found")

    def handle_namespace_use(self, args, decorator=None):
        """Handle namespace importing"""
        forced = (decorator == '!')
        if forced:
            raise ValueError("Forced decorator '!' is not available for this command")

        self.session.db.use_namespace(args)
        return f"Namespace {args} imported", None

    def handle_save_namespace(self, args, decorator=None):
        """Handles namespace saving"""
        forced = (decorator == "!")
        
    def handle_show(self, args, decorator=None):
        """Shows mathematical representation of content of term."""
        forced = (decorator == '!')
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        if term := self.session.db.get_term(identifier):
            return term, term
        elif identifier.startswith('%'):  # Check if it's a history reference
            try:
                term = self.session.history.fetch(int(identifier[1:]))
                return term, term
            except KeyError:
                raise ValueError(f"History entry {identifier} not found")
        return None, None
    
    def handle_list(self, args, decorator=None):
        """Lists all terms in the database"""
        if decorator == '.':
            namespaces = self.session.db.list_namespaces()
            interface.print_raw("Available namespaces:")
            if len(namespaces) == 0:
                return "No namespaces available", None
            else:
                for ns in namespaces:
                    interface.print_raw(f"  {ns}")
                return "Namespace query done", None
        forced = (decorator == '!')
        if len(args) > 0:
            terms = self.session.db.get_all_terms(args, forced=forced)
        else:
            terms = self.session.db.get_all_terms(forced=forced)
        if terms:
            lines = []
            for term in terms:
                term_name = term[0]
                term_value = term[1]
                filler_spaces = filler(width(), str(term_name), str(term_value)) * ' '
                lines.append(f"{bold_text(term_name)}{filler_spaces}{term_value}")
            return "\n".join(lines), None
        
        return "No terms found", None
            
    def handle_help(self, _, decorator=None):
        """Show dynamically generated help information"""
        forced = (decorator == '!')
        # Build handler -> commands mapping
        handler_map = {}
        for cmd, handler in self.command_map.items():
            if handler == self.handle_unknown:
                continue  # Skip unknown command handler
            handler_map.setdefault(handler, []).append(cmd)

        # Generate help entries
        help_entries = []
        for handler, commands in handler_map.items():
            # Get first line of docstring as description
            doc = (handler.__doc__ or "No description available").split('\n')[0].strip()
            
            # Format command list with bold and color
            formatted_commands = f"{italic_text(bold_text(', '.join(sorted(commands))))}"
            
            help_entries.append((formatted_commands, doc))

        # Sort by first command alphabetically
        help_entries.sort(key=lambda x: x[0].lower())

        # Build help text
        help_text = ["Available commands:"]
        for commands, description in help_entries:
            help_text.append(f"{commands}: {description}")
        
        return "\n".join(help_text), None

    def handle_exit(self, _, decorator=None):
        """Exit the REPL"""
        forced = (decorator == '!')
        interface.show_warning("Exiting REPL. Bye!")
        self.session.running = False
        return "Exiting lambda calculus REPL", None

    def handle_unknown(self, _, decorator=None):
        """Handle unknown commands"""
        forced = (decorator == '!')
        raise ValueError("Unknown command")

def save_term(term, session):
    global counter;
    counter += 1
    """Save term to history"""
    if isinstance(term, Term):
        term = term.literal()
    if isinstance(term, str):
        term = term.strip()
        
    session.history.insert(counter, term)

def main():
    global counter
    session = REPLSession()
    session.history.clear()
    handler = CommandHandler(session)
    for color, label in zip(COLORS.values(), LABELS.values()):
        print(f"{color_text(f'{label}', color, bg=True)}", end=' ')
    print()
    while session.running:
        try:
            print(status_label(f'%{counter}', None), end=' ')
            print(filler(width(), f'[%{counter}] ', regard_labels=False) * '-')
            line = input(interface.get_lambda_prompt()).strip()
            if not line:
                continue
            decorator = line[0]
            line = line[1:] if decorator in ['!', '.'] else line
            readline.add_history(line)
            commands = line.split(';')
            
            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue
                        
                keyword, args = normalize_blank(cmd)
                response, term = handler.execute((keyword.upper(), args), decorator)
                
                if term:
                    session.history.insert(counter, term.literal())
                else:
                    interface.show_warning(f'Empty literal returned from handler, skipping history insertion for %{counter}.')
                    
                if keyword.upper() in ['SHOW', 'DISPLAY']:
                    if response:
                        interface.log_item(f'Term {italic_text(args)} found.' if decorator == '!' else f'Terms matching {italic_text(args)} are found.')
                        interface.print_raw(response)
                    else:
                        interface.show_error(f'Term for identifier {italic_text(args)} does not exist.')
                
                if keyword.upper() in ['RED', 'REDUCE', 'RUN'] and session.current_term:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('REDUCE')} command, ignored on execution.')
                    interface.log_item(response)
                    error_occurred = False
                    save_variable = None  # Track output variable
                    previous_literal = ""
                    parts = [p.strip() for p in args.replace(' ', '').split('>')]
                    save_variable = parts[1] if len(parts) > 1 else None
                    
                    try:
                        while True:
                            interface.show_beta_reduction_step(session.current_term)
                            if session.current_term.literal() == previous_literal:
                                raise FixedPointDetected(term = session.current_term)

                            user_input = input(interface.get_beta_prompt()).strip()
                            
                            # Parse command and output variable
                            parts = [p.strip() for p in user_input.split('>', 1)]
                            command = parts[0].lower()
                            output_var = parts[1] if len(parts) > 1 else None
                            
                            _skip_processing = False
                            # Handle commands
                            if command in ('exit', 'q'):
                                if output_var:
                                    _skip_processing = True
                                    session.db.insert_term(output_var, session.current_term)
                                    interface.show_success(f'Saved as "{output_var}"')
                                break

                            if command == 'save':
                                if not output_var:
                                    _skip_processing = True
                                    interface.show_error("Missing variable name after 'save >'")
                                    continue
                                session.db.insert_term(output_var, session.current_term)
                                interface.show_success(f'Saved current term as {italic_text(output_var)}')
                                continue
                            
                            if command == 'retreat':
                                if not output_var:
                                    _skip_processing = True
                                    interface.show_error("Missing variable name after 'retreat >'")
                                    continue
                                try:
                                    _skip_processing = True
                                    session.current_term = session.history.fetch(int(output_var[1:]))
                                    interface.show_success(f'Restored to {italic_text(output_var)}')
                                    save_term(session.current_term, session)
                                    continue
                                except ValueError:
                                    _skip_processing = True
                                    interface.show_error(f'History entry {output_var} not found(valueerr)')
                                    continue
                                except IndexError:
                                    _skip_processing = True
                                    interface.show_error(f'History entry {output_var} not found')
                                    continue
                            
                            if command == 'alpha':
                                if not output_var:
                                    _skip_processing = True
                                    interface.show_error("Missing variable name after 'alpha >'")
                                    continue
                                try:
                                    _skip_processing = True
                                    session.current_term = session.current_term.alpha_conversion(output_var)
                                    interface.show_alpha_reduction_step(f'{session.current_term.literal()}')
                                    save_term(session.current_term, session)
                                    continue
                                except Exception as e:
                                    _skip_processing = True
                                    interface.show_error(f'Alpha reduction failed: {str(e)}')
                                    continue
                            
                            _skip_linting = False
                            
                            if command == 'step' or command == 'beta' or not command:
                                total_chars = len(str(counter)) + 13
                                print(f'\033[1A\033[{total_chars}Cbeta', end='\n')
                                _skip_linting = True
                                
                            if command and not _skip_linting:  # Unknown command
                                interface.show_error(f"Unknown command: {italic_text(command)}")
                                interface.show_error("Available commands: exit, save, retreat, alpha, beta")
                                continue
                            
                            previous_literal = session.current_term.literal()
                            
                            # Perform reduction step
                            if not _skip_processing:
                                try:
                                    session.current_term = session.current_term.beta_reduce_step()
                                    save_term(session.current_term, session)
                                except ReductionOnNormalForm as e:
                                    interface.show_success("Reached normal form")
                                    if save_variable:
                                        session.db.insert_term(save_variable, session.current_term)
                                        interface.show_success(f'Auto-saved as {italic_text(save_variable)}')
                                    else:
                                        interface.log_item(f'Current literal: ')
                                        interface.print_raw(italic_text(f'DEF %{counter} := {session.current_term.literal()}'))
                                    break
                    except FixedPointDetected as e:
                        interface.show_success(f"Reduction reached fixed point")
                        if save_variable:
                            session.db.insert_term(save_variable, session.current_term)
                            interface.show_success(f'Auto-saved as {italic_text(save_variable)}')
                        else:
                            interface.log_item(f'Current literal: ')
                            interface.print_raw(italic_text(f'DEF %{counter} := {session.current_term.literal()}'))
                            
                    except ParseError as e:
                        interface.show_error(e.literal)
                    except Exception as e:
                        interface.show_error(str(e))
                        error_occurred = True

                    # Final save prompt if needed
                    if not error_occurred and save_variable:
                        session.db.insert_term(save_variable, session.current_term)
                        interface.show_success(f'Saved final result as {italic_text(save_variable)}')

                    session.output_var = None
                
                if keyword.upper() in ['LIST', 'LS']:
                    interface.print_raw(response)
                    
                if keyword.upper() in ['DEL', 'DELETE', 'RM']:
                    if response:
                        interface.show_success(response)
                    else:
                        interface.show_error(f'Term for identifier {italic_text(args)} does not exist.')
                
                if keyword.upper() in ['LIT', 'LITERAL']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('LIT')} command, ignored on execution.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f'Term for identifier {italic_text(args)} does not exist.')

                if keyword.upper() in ['TREE']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('TREE')} command, ignored on execution.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f'Term for identifier {italic_text(args)} does not exist.')
                        
                if keyword.upper() in ['DEF', 'DEFINE']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('DEF')} command, ignored on execution.')
                    if response:
                        interface.show_success(response)
                    else:
                        interface.show_error(f'Definition failed for {italic_text(args)}')
                if keyword.upper() in ['HELP', 'H']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('HELP')} command.')
                    interface.print_raw(response)
                if keyword.upper() == ['EXIT', 'Q', 'QUIT']:
                    interface.show_success(response)
                    session.running = False

        except EOFError:
            handler.handle_exit(None)
        except UserCancelledOperation as e:
            interface.show_warning(str(e))
        except KeyboardInterrupt:
            print()
            interface.show_warning("Operation cancelled by user")
            # handler.handle_exit(None)
        except Exception as e:
            interface.show_error(str(e))
        counter += 1
    
if __name__ == "__main__":
    main()