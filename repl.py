# Created by Sean L. on Mar. 28
# Lambda Calculus Implementation
# repl/repl.py
# Makabaka1880, 2025. All rights reserved.

import readline
from colorist import Color, Effect
from models.model import Term, Abstraction, Variable, Application
from preproc import normalize_blank
from parser import *
from models.exceptions import *

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

class CommandHandler:
    """Handle different REPL commands"""
    def __init__(self, session):
        self.session = session
        self.command_map = {
            'DEF': self.handle_def,
            'RED': self.handle_red,
            'SHOW': self.handle_show,
            'HELP': self.handle_help,
            'LIST': self.handle_list,
            'EXIT': self.handle_exit,
            'DEL': self.handle_delete
        }

    def execute(self, command):
        """Execute a parsed command"""
        keyword, args = command
        handler = self.command_map.get(keyword, self.handle_unknown)
        return handler(args)

    def handle_def(self, args):
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

    def handle_red(self, args):
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

    def handle_delete(self, args):
        """Handle DEL command with optional regex"""
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        
        if self.session.db.get_term(identifier, regex=True):
            self.session.db.delete_term(identifier, regex=True)
            return f"Deleted {identifier} (regex: {regex})"
        raise ValueError(f"Identifier {identifier} not found")

    def handle_show(self, args):
        """Handle SHOW with regex"""
        parts = args.strip().split(maxsplit=1)
        identifier = parts[0]
        if term := self.session.db.get_term(identifier, regex=True):
            return term
        return None
    
    def handle_list(self, args):
        """Lists all terms in the database"""
        terms = self.session.db.get_all_terms()
        if terms:
            return ("\n".join([f"{Color.CYAN}{term[0]}{Color.OFF}: {term[1]}" for term in terms]))
        else:
            return "No terms found"
        return "No terms found"
            
    def handle_help(self, _):
        """Show help information"""
        return (
            "Available commands:\n"
            f"{Color.CYAN}{Effect.BOLD}DEF{Effect.OFF} <name> := <term> {Color.OFF} Define a new term\n"
            f"{Color.CYAN}{Effect.BOLD}RED{Effect.OFF} <term> {Color.OFF} Start beta reduction\n"
            f"{Color.CYAN}{Effect.BOLD}SHOW{Effect.OFF} <name> {Color.OFF} Show term by identifier\n"
            f"{Color.CYAN}{Effect.BOLD}DEL{Effect.OFF} <name> {Color.OFF} Delete term by identifier\n"
            f"{Color.CYAN}{Effect.BOLD}HELP{Effect.OFF} {Color.OFF} Show this help message\n"
            f"{Color.CYAN}{Effect.BOLD}LIST{Effect.OFF} {Color.OFF} List all terms\n"
            f"{Color.CYAN}{Effect.BOLD}EXIT{Effect.OFF} {Color.OFF} Quit the REPL"
        )

    def handle_exit(self, _):
        """Exit the REPL"""
        self.session.running = False
        return "Exiting lambda calculus REPL"

    def handle_unknown(self, _):
        """Handle unknown commands"""
        raise ValueError("Unknown command")

class REPLInterface:
    """User interface components"""
    
    def init_readline():
        pass
    
    @staticmethod
    def get_prompt() -> str:
        """Wrap ANSI codes for readline compatibility"""
        return f"\001{Effect.BOLD}\002λ > \001{Effect.OFF}\002"

    @classmethod
    def log_status(cls, message):
        print(f"{Color.YELLOW}{message}{Color.OFF}")
        
    @classmethod
    def print_item(cls, item):
        print(item)

    @classmethod
    def show_error(cls, message):
        print(f"{Color.RED}Error: {message}{Color.OFF}")

    @classmethod
    def show_success(cls, message, end='\n'):
        print(f"{Color.GREEN}{message}{Color.OFF}", end=end)

    @classmethod
    def show_reduction_step(cls, step, term):
        print(f"Step {step}: {term}")

def main():
    session = REPLSession()
    handler = CommandHandler(session)
    interface = REPLInterface()

    REPLInterface.init_readline()
    
    while session.running:
        try:
            line = input(interface.get_prompt())
            readline.add_history(line)
            commands = line.split(';')
            
            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue
                
                keyword, args = normalize_blank(cmd)
                response = handler.execute((keyword.upper(), args))
                
                if keyword.upper() == 'SHOW':
                    if response:
                        interface.print_item(response)
                    else:
                        interface.show_error(f'Term for identifier {args} does not exist.')
                
                if keyword.upper() == 'RED' and session.current_term:
                    interface.log_status(response)
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

                            user_input = input("β > ").strip()
                            
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
                                interface.show_success(f'Saved current term as "{output_var}"')
                                continue

                            if command:  # Unknown command
                                interface.show_error(f"Unknown command: {command}")
                                continue

                            # Perform reduction step
                            try:
                                session.current_term = session.current_term.beta_reduce_step()
                                step += 1
                            except ReductionOnNormalForm as e:
                                interface.show_success("Reached normal form")
                                if save_variable:
                                    session.db.insert_term(save_variable, session.current_term)
                                    interface.show_success(f'Auto-saved as "{save_variable}"')
                                else:
                                    interface.print_item(f'Current literal:\n{session.current_term.literal()}')
                                break
                    except FixedPointDetected as e:
                        interface.show_success("Reached fixed point")
                        if save_variable:
                            session.db.insert_term(save_variable, session.current_term)
                            interface.show_success(f'Auto-saved as "{save_variable}"')
                        else:
                            interface.print_item(f'Current literal:\n{session.current_term.literal()}')
                            
                    except Exception as e:
                        interface.show_error(str(e))
                        error_occurred = True

                    # Final save prompt if needed
                    if not error_occurred and save_variable:
                        session.db.insert_term(save_variable, session.current_term)
                        interface.show_success(f'Saved final result as "{save_variable}"')

                    session.output_var = None
                
                if keyword.upper() == 'LIST':
                    interface.print_item(response)
                if keyword.upper() == 'DEL':
                    if response:
                        interface.show_success(response)
                    else:
                        interface.show_error(f'Term for identifier {args} does not exist.')
                if keyword.upper() == 'DEF':
                    if response:
                        interface.show_success(response)
                    else:
                        interface.show_error(f'Definition failed for {args}')
                if keyword.upper() == 'HELP':
                    interface.print_item(response)
                if keyword.upper() == 'EXIT':
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