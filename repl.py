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
import requests
from devconst import *;

counter = 0

def width():
    """Get the width of the terminal window"""
    try:
        result = subprocess.run(['tput', 'cols'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        cols = int(result.stdout.decode().strip())
        if cols > 0:
            return cols
    except Exception:
        # Fallback for Docker or non-interactive environments
        return int(os.environ.get("COLUMNS", 80))
    
    # The following code will be replaced when deployed on a server.
    # To further contributors, DO NOT REMOVE THIS CODE.
    # It is a marker for the server update.
    # This code will be run on the server backend, and if False will be replaced with if True.
    if False: # MARKER:SERVER_UPDATE1
        response = requests.get("http://localhost:5050/api/cols", verify=False)
        if response.status_code == 200:
            return int(response.json())
        else:
            raise ValueError(f"Failed to fetch rows: {response.status_code} {response.reason}")

    return 80

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
    session: REPLSession
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
            'body': self.handle_extract_body,
            'var': self.handle_extract_var,
            'func': self.handle_extract_func,
            'val': self.handle_extract_val,
            'type': self.handle_show_type,
            'alpha': self.handle_alpha_conversion,
            'substitute': self.handle_substitution,
            
            # Shorthand aliases
            'ls': self.handle_list,      # list
            'rm': self.handle_delete,    # delete
            'h': self.handle_help,       # help
            'q': self.handle_exit,       # exit
            'quit': self.handle_exit,    # exit
            'sub': self.handle_substitution, # substitute
            
            # Full-length alternatives
            'define': self.handle_def,
            'reduce': self.handle_red,
            'literal': self.handle_literal,
            'delete': self.handle_delete,
            'namespace': self.handle_namespace_use,
            'extract_body': self.handle_extract_body,
            'extract_variable': self.handle_extract_var,
            'extract_function': self.handle_extract_func,
            'extract_value': self.handle_extract_val,
            'alpha_convert': self.handle_alpha_conversion,
            'substitution': self.handle_substitution,
            
            # Common alternatives
            'run': self.handle_red,      # alternative to reduce
            'display': self.handle_show,  # alternative to show
            'rename': self.handle_alpha_conversion # alternative to alpha_convert
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

        self.session.current_term = parse_term(term_part)

        return f"{bold_text('Reducing')}{' ' * filler(width(), 'Reducing', str(self.session.current_term))}{str(self.session.current_term)}", self.session.current_term

    def handle_literal(self, args, decorator=None):
        """Shows literal content of term in PyLambda literal"""
        forced = (decorator != '?')
        identifier = args.strip().split()[0]
        if forced:
            term = parse_term(identifier)
            return term.literal(), term
        else:
            objs = ""
            for t in self.session.db.get_all_terms(identifier):
                objs += bold_text(t[0].__repr__()[1:-1])
                objs += '   '
                objs += t[1].__repr__()
                objs += '\n'
            return objs, None

    
    def handle_tree(self, args, decorator=None):
        """Method to output a string of a tree representation of term"""
        forced = (decorator == '!')
        identifier = args.strip().split()[0]
        term = parse_term(identifier)
        return term.tree_str(), term
    
    def handle_delete(self, args, decorator=None):
        """Handle DEL command with optional regex"""
        forced = (decorator != '?')
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

    def handle_substitution(self, args, decorator=None):
        """Handle substitution of term"""
        forced = (decorator == '!')
        if forced:
            raise ValueError("Forced decorator '!' is not available for this command")
        
        # Parse substitution command
        parts = args.split('<')
        if '>' in args:
            interface.show_warning(f'Operator {italic_text('>')} is used, do you mean {italic_text('<')}?')
        
        term_str = parts[0].strip()
        term = parse_term(term_str)
        
        if len(parts) == 2:
            _replacement = parts[1].strip().split(',', 1)
            if len(_replacement) != 2:
                raise UnexpectedArgsError(_replacement)
            target_str, replacement_str = _replacement[0], _replacement[1];
            

            # Parse terms
            replacement = parse_term(replacement_str)
            if not (_ := parse_variable(target_str)):
                raise ValueError(f'Target literal {italic_text(target_str)} is not a valid identifier')
            
            # Perform substitution
            substituted_term = term.substitute(target_str, replacement)
            
            return str(substituted_term), substituted_term
        
        elif len(parts) == 1:
            identifiers = self.session.db.get_all_terms();
            for id in identifiers:
                try:
                    term = term.substitute(id[0], id[1])
                except Exception as e:
                    continue
            return str(term), term
        else:
            raise UnexpectedArgsError(args)

    
    def handle_namespace_use(self, args, decorator=None):
        """Handle namespace importing"""
        forced = (decorator == '!')
        if forced:
            raise ValueError("Forced decorator '!' is not available for this command")

        self.session.db.use_namespace(args)
        return f"Namespace {args} imported", None

    def handle_save_namespace(self, args, decorator=None):
        """Handles namespace saving - UNDER DEV"""
        forced = (decorator == "!")
        name = args
        self.session.db.save_namespace(name, forced)
        print(name)
        return 'Namespace created successfully.\nUpon usage, execute ' + italic_text('USE ' + name + ';'), None
        
    def handle_show(self, args, decorator=None):
        """Shows mathematical representation of content of term."""
        forced = (decorator != '?')
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        term = parse_term(identifier)

        return term.__repr__(), term
    
    def handle_show_type(self, args, decorator=None):
        """Shows the type of term"""
        term = parse_term(args)
        if isinstance(term, Variable):
            return 'TYPE <VAR>', term
        if isinstance(term, Abstraction):
            return 'TYPE <ABSTRACTION>', term
        if isinstance(term, Application):
            return 'TYPE <APPLICATION>', term
        
        return 'WTF???', term
    
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
        forced = (decorator != '?')
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
    
    def handle_extract_body(self, args, decorator=None):
        """Extracts the body term of an lambda abstraction."""
        args = args.split('>');
        if len(args) == 2:
            destination = args[1]
        elif len(args) == 1:
            destination = None
        else:
            raise UnexpectedArgsError(args)
        
        expr = args[0]
        term = parse_term(expr)
        
        if isinstance(term, Abstraction):
            term = term.body
            if destination:
                self.session.db.insert_term(destination, term)
                return str(term) + '\n' + 'Saving body to ' + italic_text(destination), term
            else:
                return str(term), term
        else:
            raise TypeError('Term is not of type ' + italic_text('Abstraction'))
        
    def handle_extract_var(self, args, decorator=None):
        """Extracts the variable of a lambda abstraction."""
        args = args.split('>')
        if len(args) == 2:
            destination = args[1]
        elif len(args) == 1:
            destination = None
        else:
            raise UnexpectedArgsError(args)

        expr = args[0]
        term = parse_term(expr)

        if isinstance(term, Abstraction):
            variable = term.var
            if destination:
                self.session.db.insert_term(destination, variable)
                return str(variable) + '\n' + 'Saving variable to ' + italic_text(destination), variable
            else:
                return str(variable), variable
        else:
            raise TypeError('Term is not of type ' + italic_text('Abstraction'))

    def handle_extract_func(self, args, decorator=None):
        """Extracts the function part of an application."""
        args = args.split('>')
        if len(args) == 2:
            destination = args[1]
        elif len(args) == 1:
            destination = None
        else:
            raise UnexpectedArgsError(args)

        expr = args[0]
        term = parse_term(expr)

        if isinstance(term, Application):
            function = term.function
            if destination:
                self.session.db.insert_term(destination, function)
                return str(function) + '\n' + 'Saving function to ' + italic_text(destination), function
            else:
                return str(function), function
        else:
            raise TypeError('Term is not of type ' + italic_text('Application'))
        
    def handle_extract_val(self, args, decorator=None):
        """Extracts the value part of an application."""
        args = args.split('>')
        if len(args) == 2:
            destination = args[1]
        elif len(args) == 1:
            destination = None
        else:
            raise UnexpectedArgsError(args)

        expr = args[0]
        term = parse_term(expr)

        if isinstance(term, Application):
            value = term.value
            if destination:
                self.session.db.insert_term(destination, value)
                return str(value) + '\n' + 'Saving value to ' + italic_text(destination), value
            else:
                return str(value), value
        else:
            raise TypeError('Term is not of type ' + italic_text('Application'))
    
    def handle_alpha_conversion(self, args, decorator=None):
        """Computes alpha conversion on the abstraction"""
        correct = (decorator == '+')
        forced = (decorator == '!')
        args = args.split('<');
        if len(args) != 2:
            raise UnexpectedArgsError(args)
        
        term = parse_term(args[0]); name = args[1];
        
        try:
            names = self.session.db.get_vars()
            if name in names and not correct:
                if not forced:
                    raise IdentifierNameClash(name)
                else:
                    interface.show_warning('Possibility of identifier clash overriden with decorator !: identifier ' + italic_text(name))
            elif correct:
                name = fresh_variable(name, lambda x: x in names)
        except Exception as e:
            interface.show_error('Exception caught while catching for identifier name clash')
            interface.show_error(e)
        
        if not isinstance(term, Abstraction):
            raise TypeError('Term is not of type ' + italic_text('Abstraction'))

        term = term.alpha_conversion(name)
        
        return str(term), term
        
        
        
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
    # for color, label in zip(COLORS.values(), LABELS.values()):
    #     print(f"{color_text(f'{label}', color, bg=True)}", end=' ')
    # print()
    while session.running:
        try:
            print(status_label(f'%{counter}', None), end=' ')
            print(filler(width(), f'[%{counter}] ', regard_labels=False) * '-')
            line = input(interface.get_lambda_prompt()).strip()
            readline.add_history(line)
            if not line:
                continue
            decorator = line[0]
            line = line[1:] if decorator in ['!', '.', '?', '+'] else line
            commands = line.split(';')
            
            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue
                        
                keyword, args = normalize_blank(cmd)
                response, term = handler.execute((keyword.upper(), args), decorator)
                if response == WARNING_FEATURE_UNDER_DEVELOPMENT:
                    interface.show_warning(f'Command {keyword.upper()} is under development.')
                    continue
                
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
                
                if keyword.upper() in ['TYPE']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('TYPE')} command.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f"Type extraction failed for {italic_text(args)}")
                
                if keyword.upper() in ['VAR', 'EXTRACT_VARIABLE']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('EXTRACT_VARIABLE')} command.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f"Variable extraction failed for {italic_text(args)}")
                
                if keyword.upper() in ['BODY', 'EXTRACT_BODY']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('EXTRACT_BODY')} command.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f"Body extraction failed for {italic_text(args)}")
                
                if keyword.upper() in ['VAL', 'EXTRACT_VALUE']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('EXTRACT_VALUE')} command.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f"Value extraction failed for {italic_text(args)}")
                
                if keyword.upper() in ['FUNC', 'EXTRACT_FUNCTION']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('EXTRACT_FUNCTION')} command.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f"Function extraction failed for {italic_text(args)}")
                
                if keyword.upper() in ['ALPHA', 'ALPHA_CONVERT', 'RENAME']:
                    interface.print_raw(response)
                
                if keyword.upper() in ['SUB', 'SUBSTITUTION', 'SUBSTITUTE']:
                    if decorator == '!':
                        interface.show_warning(f'Force decorater \'!\' is not available for {italic_text('SUBSTITUTION')} command.')
                    if response:
                        interface.print_raw(response)
                    else:
                        interface.show_error(f"Substitution failed for {italic_text(args)}")

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