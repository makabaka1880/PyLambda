# Created by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# repl/repl.py
# 
# Makabaka1880, 2025. All rights reserved.

import readline
from colorist import Color, Effect
from models.model import Term, Abstraction, Variable, Application
from preproc import normalize_blank
from parser import *
from models.exceptions import *
from colors import status_label, italic_text, bold_text, LABELS, COLORS, color_text
import re

    
class REPLSession:
    def __init__(self):
        self.db = TermDB()  # Replace registered_table
        self.current_term = None
        self.running = True
        self.output_var = None
        self._init_standard_library()

    def _init_standard_library(self):
        from parser import parse_lambda
        """Store built-in terms in DB"""
        std_terms = {
        }
        
        for name, term in std_terms.items():
            self.db.insert_term(name, term)
class REPLInterface:
    """User interface components"""
    
    def init_readline():
        pass
    
    @staticmethod
    def get_lambda_prompt() -> str:
        """Wrap ANSI codes for readline compatibility"""
        return f"{status_label(LABELS['lambda_prompt'], COLORS['lambda_prompt'])} {bold_text('λ')} + "
        
    @staticmethod
    def get_alpha_prompt() -> str:
        """Wrap ANSI codes for readline compatibility"""
        return f"{status_label(LABELS['alpha_prompt'], COLORS['alpha_prompt'])} {bold_text('α')} + "
    
    @staticmethod
    def get_beta_prompt() -> str:
        """Wrap ANSI codes for readline compatibility"""
        return f"{status_label(LABELS['beta_prompt'], COLORS['beta_prompt'])} {bold_text('β')} + "
        
    @classmethod
    def show_warning(cls, message):
        for line in str(message).splitlines():
            print(f"{status_label(LABELS['warning'], COLORS['warning'])} {line}")
        
    @classmethod
    def print_raw(cls, item):
        for line in str(item).splitlines():
            print(f"{status_label(LABELS['data'], COLORS['data'])} {line}")

    @classmethod
    def log_item(cls, message):
        for line in str(message).splitlines():
            print(f"{status_label(LABELS['info'], COLORS['info'])} {line}")
        
    @classmethod
    def show_error(cls, message):
        for line in str(message).splitlines():
            print(f"{status_label(LABELS['error'], COLORS['error'])} {line}")

    @classmethod
    def show_success(cls, message, end='\n'):
        for line in str(message).splitlines():
            print(f"{status_label(LABELS['success'], COLORS['success'])} {line}", end=end)

    @classmethod
    def show_reduction_step(cls, step, term):
        for line in str(term).splitlines():
            print(f"{status_label(LABELS['beta_reduction_step'], COLORS['beta_reduction_step'])} {step}: {line}")
    

interface = REPLInterface()

REPLInterface.init_readline()

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
            
            # Common alternatives
            'run': self.handle_red,      # alternative to reduce
            'display': self.handle_show  # alternative to show
        }

    def execute(self, command, decorator=None):
        """Execute a parsed command"""
        keyword, args = command
        handler = self.command_map.get(keyword.lower(), self.handle_unknown)
        return handler(args, decorator == '!')

    def handle_def(self, args, forced=False):
        """Handle DEF command with session's DB"""
        try:
            identifier, literal = args.split(':=', 1)
            identifier = identifier.strip()
            # Access DB via session
            term = parse_lambda(literal, self.session.db)
            self.session.db.insert_term(identifier, term)
            return f"Defined {identifier}"
            
        except ValueError:
            raise ParseError("Invalid DEF syntax")

    def handle_red(self, args, forced=False):
        """Handle RED command with output variable"""
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
        else:
            self.session.current_term = parse_lambda(term_part, self.session.db)
            
        return f"Reducing: {self.session.current_term.literal()}"

    def handle_literal(self, args, forced=False):
        """Shows content of term in PyLambda literal"""
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        if term := self.session.db.get_term(identifier, regex=False):
            return term.literal()
        return None
    
    def handle_tree(self, args, forced=False):
        """Method to output a string of a tree representation of term"""
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        if term := self.session.db.get_term(identifier, regex=False):
            return term.tree_str()
        return None
    
    def handle_delete(self, args, forced=False):
        """Handle DEL command with optional regex"""
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        if self.session.db.get_term(identifier, regex=(not forced)):
            self.session.db.delete_term(identifier, regex=(not forced))
            return f"Deleted {identifier} (regex: {identifier})"
        raise ValueError(f"Identifier {italic_text(identifier)} not found")

    def handle_show(self, args, forced=False):
        """Shows mathematical representation of content of term."""
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        if term := self.session.db.get_term(identifier, regex=(not forced)):
            return term
        return None
    
    def handle_list(self, args, forced=False):
        """Lists all terms in the database"""
        if len(args) > 0:
            terms = self.session.db.get_all_terms(args, forced=forced)
        else:
            terms = self.session.db.get_all_terms(forced=forced)
        if terms:
            return ("\n".join([f"{term[0]} {term[1]}" for term in terms]))
        
        return "No terms found"
            
    def handle_help(self, _, forced=False):
        """Show dynamically generated help information"""
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
            formatted_commands = f"{Color.CYAN}{Effect.BOLD}" + \
                                f"{', '.join(sorted(commands))}" + \
                                f"{Effect.OFF}{Color.OFF}"
            
            help_entries.append((formatted_commands, doc))

        # Sort by first command alphabetically
        help_entries.sort(key=lambda x: x[0].lower())

        # Build help text
        help_text = ["Available commands:"]
        for commands, description in help_entries:
            help_text.append(f"{commands}: {description}")
        
        return "\n".join(help_text)

    def handle_exit(self, _, forced=False):
        """Exit the REPL"""
        interface.show_warning("Exiting REPL. Bye!")
        self.session.running = False
        return "Exiting lambda calculus REPL"

    def handle_unknown(self, _, forced=False):
        """Handle unknown commands"""
        raise ValueError("Unknown command")



def main():
    session = REPLSession()
    handler = CommandHandler(session)
    while session.running:
        try:
            line = input(interface.get_lambda_prompt()).strip()
            if not line:
                continue
            
            decorator = line[0]
            line = line[1:] if decorator == '!' else line
            readline.add_history(line)
            commands = line.split(';')
            
            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue
                if cmd == 'pal':
                    for color, label in zip(COLORS.values(), LABELS.values()):
                        print(f"{color_text(f'{label}', color, bg=True)}")
                    continue
                        
                keyword, args = normalize_blank(cmd)
                response = handler.execute((keyword.upper(), args), decorator)
                
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
                    step = 0
                    error_occurred = False
                    save_variable = None  # Track output variable
                    previous_literal = ""
                    parts = [p.strip() for p in args.replace(' ', '').split('>')]
                    save_variable = parts[1] if len(parts) > 1 else None
                    
                    try:
                        while True:
                            interface.show_reduction_step(step, session.current_term)
                            if session.current_term.literal() == previous_literal:
                                raise FixedPointDetected(term = session.current_term)

                            previous_literal = session.current_term.literal()

                            user_input = input(interface.get_beta_prompt()).strip()
                            
                            # Parse command and output variable
                            parts = [p.strip() for p in user_input.split('>', 1)]
                            command = parts[0].lower()
                            output_var = parts[1] if len(parts) > 1 else None
                            
                            # Handle commands
                            if command in ('exit', 'q'):
                                if output_var:
                                    session.db.insert_term(output_var, session.current_term)
                                    interface.show_success(f'Saved as "{output_var}"')
                                break

                            if command == 'save':
                                if not output_var:
                                    interface.show_error("Missing variable name after 'save >'")
                                    continue
                                session.db.insert_term(output_var, session.current_term)
                                interface.show_success(f'Saved current term as {italic_text(output_var)}')
                                continue

                            if command:  # Unknown command
                                interface.show_error(f"Unknown command: {italic_text(command)}")
                                continue

                            # Perform reduction step
                            try:
                                session.current_term = session.current_term.beta_reduce_step()
                                step += 1
                            except ReductionOnNormalForm as e:
                                interface.show_success("Reached normal form")
                                if save_variable:
                                    session.db.insert_term(save_variable, session.current_term)
                                    interface.show_success(f'Auto-saved as {italic_text(save_variable)}')
                                else:
                                    interface.log_item(f'Current literal: ')
                                    interface.print_raw(session.current_term.literal())
                                break
                    except FixedPointDetected as e:
                        interface.show_success("Reached fixed point")
                        if save_variable:
                            session.db.insert_term(save_variable, session.current_term)
                            interface.show_success(f'Auto-saved as {italic_text(save_variable)}')
                        else:
                            interface.log_item(f'Current literal: ')
                            interface.print_raw(session.current_term.literal())
                            
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
        except KeyboardInterrupt:
            interface.show_error("Operation cancelled by user")
            handler.handle_exit(None)
        except Exception as e:
            interface.show_error(str(e))

if __name__ == "__main__":
    main()