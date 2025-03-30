# MARK: Imports and Metadata
# Created by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# utils/persistence.py
#
# Makabaka1880, 2025. All rights reserved.

# MARK: Imports
import sqlite3
from typing import Optional, List
from utils.history import HistoryStore
from models.model import Term
from models.exceptions import InvalidTermError, ParseError
from dotenv import load_dotenv
import os
import re

# MARK: Initialization
load_dotenv()

class TermDB:
    """SQLite persistence layer for lambda terms"""
    
    def __init__(self, db_path: str = os.getenv('DEFAULT_DB_PATH')):
        self.conn = sqlite3.connect(db_path)
        self.conn.create_function('REGEXP', 2, self._regexp)
        self._create_table()

    # MARK: Regex Helper
    @staticmethod
    def _regexp(pattern: str, value: str) -> bool:
        """SQLite regex helper with partial matching"""
        try:
            return re.search(pattern, value) is not None
        except re.error:
            return False
    
    # MARK: Table Management
    def _create_table(self):
        """Initialize database schema"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS base (
                identifier TEXT PRIMARY KEY,
                literal TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        
    # MARK: Term Retrieval
    def get_term(self, identifier: str) -> Optional[Term]:
        """Retrieve a term by its exact identifier"""
        from parser import parse_lambda
        cursor = self.conn.execute(
            'SELECT literal FROM base WHERE identifier = ?', (identifier,)
        )
        row = cursor.fetchone()
        if row:
            try:
                return parse_lambda(row[0], self, HistoryStore())
            except ParseError as e:
                raise ParseError(f"Invalid term {identifier}") from e
        return None

    # MARK: Term Deletion
    def delete_terms(self, identifier: str, regex: bool = False) -> None:
        """Delete terms by scanning all entries"""
        if regex:
            targets = self.get_all_terms(
                identifier_pattern=identifier,
                forced=not regex,
                case_sensitive=True
            )
        else:
            target = self.get_term(identifier)
            if target:
                targets = [(identifier, target)]
            else:
                targets = []
        
        for target_id, _ in targets:
            self.conn.execute('DELETE FROM base WHERE identifier = ?', (target_id,))
        self.conn.commit()

    # MARK: Term Insertion
    def insert_term(self, identifier: str, term: Term) -> None:
        """Insert with existence check via get_all_terms"""
        exists = any(t[0] == identifier for t in self.get_all_terms())
        
        if exists:
            self.conn.execute('''
                UPDATE base SET literal = ?
                WHERE identifier = ?
            ''', (term.literal(), identifier))
        else:
            self.conn.execute('''
                INSERT INTO base (identifier, literal)
                VALUES (?, ?)
            ''', (identifier, term.literal()))
        self.conn.commit()
    
    # MARK: Term Querying
    def get_all_terms(
        self,
        identifier_pattern: Optional[str] = None,
        literal_pattern: Optional[str] = None,
        case_sensitive: bool = True,
        skip_invalid: bool = True,
        forced: bool = False
    ) -> List[tuple[str, Term]]:
        """Retrieve terms with optional regex/string search"""
        from parser import parse_lambda

        cursor = self.conn.execute('SELECT * FROM base')
        results = []
        fetched = cursor.fetchall()
        
        for row in fetched:
            identifier, literal = row

            if identifier_pattern:
                if forced:
                    if case_sensitive:
                        if identifier_pattern != identifier:
                            continue
                    else:
                        if identifier_pattern.lower() != identifier.lower():
                            continue
                else:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if not re.fullmatch(identifier_pattern, identifier, flags=flags):
                        continue

            if literal_pattern:
                if forced:
                    if case_sensitive:
                        if literal_pattern != literal:
                            continue
                    else:
                        if literal_pattern.lower() != literal.lower():
                            continue
                else:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if not re.fullmatch(literal_pattern, literal, flags=flags):
                        continue

            try:
                term = parse_lambda(literal, self, HistoryStore())
                results.append((identifier, term))
            except ParseError as e:
                if not skip_invalid:
                    raise ParseError(f"Invalid term {identifier}") from e
                continue
        return results
        
    # MARK: Conn Management
    def close(self):
        """Close database connection"""
        self.conn.close()

    # MARK: Namespaces
    def list_namespaces(self) -> list[str]:
        """List all available namespaces excluding 'base'"""
        cursor = self.conn.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name LIKE 'ns\\_%' ESCAPE '\\'
        ''')
        return [t[0].split('_', 1)[1] for t in cursor.fetchall()]

    def save_namespace(self, name: str, force: bool = False) -> None:
        """Save current base table as a new namespace"""
        self._validate_namespace_name(name)
        namespace_table = f'ns_{name}'
        
        if self._table_exists(namespace_table):
            if not force:
                raise ValueError(f"Namespace {name} exists. Use force decorator to overwrite")
            self.conn.execute(f'DROP TABLE {namespace_table}')
            
        self.conn.execute(f'''
            CREATE TABLE {namespace_table} AS
            SELECT * FROM base
        ''')
        self.conn.commit()

    def use_namespace(self, name: str) -> None:
        """Import terms from a namespace into base table"""
        self._validate_namespace_name(name)
        namespace_table = f'ns_{name}'
        
        if not self._table_exists(namespace_table):
            raise ValueError(f"Namespace {name} does not exist")
            
        self.conn.execute(f'''
            INSERT OR IGNORE INTO base (identifier, literal)
            SELECT identifier, literal FROM {namespace_table}
        ''')
        self.conn.commit()

    # MARK: Helpers
    def _table_exists(self, table_name: str) -> bool:
        """Check if table exists in database"""
        cursor = self.conn.execute('''
            SELECT 1 FROM sqlite_master 
            WHERE type='table' AND name=?
        ''', (table_name,))
        return bool(cursor.fetchone())

    def _validate_namespace_name(self, name: str) -> None:
        """Validate namespace naming rules"""
        if name.lower() == 'base':
            raise ValueError("'base' is a reserved namespace")
        if not re.match(r'^\w+$', name):
            raise ValueError("Namespace can only contain [A-Za-z0-9_] characters")
