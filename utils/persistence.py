# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# utils/persistence.py
# 
# Makabaka1880, 2025. All rights reserved.

import sqlite3
from typing import Optional
from models.model import Term
from models.exceptions import InvalidTermError, ParseError
from colorist import Color, Effect
from dotenv import load_dotenv
import os
import re

load_dotenv()

class TermDB:
    """SQLite persistence layer for lambda terms"""
    
    def __init__(self, db_path: str = os.getenv('DEFAULT_DB_PATH')):
        self.conn = sqlite3.connect(db_path)
        self.conn.create_function('REGEXP', 2, self._regexp)
        self._create_table()

    @staticmethod
    def _regexp(pattern: str, value: str) -> bool:
        """SQLite regex helper with partial matching"""
        try:
            return re.search(pattern, value) is not None
        except re.error:
            return False
    
    def _create_table(self):
        """Initialize database schema"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS lambda_terms (
                identifier TEXT PRIMARY KEY,
                literal TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        
    def insert_term(self, identifier: str, term: Term) -> None:
        """Store a validated term"""
        from parser import parse_lambda

        self.conn.execute('''
            INSERT OR REPLACE INTO lambda_terms (identifier, literal)
            VALUES (?, ?)
        ''', (identifier, term.literal()))
        self.conn.commit()
        
    def get_term(self, identifier: str, regex: bool = False) -> Optional[Term]:
        """Retrieve term(s) by identifier or regex pattern
        
        Args:
            identifier: Exact ID or regex pattern if regex=True
            regex: Treat identifier as regex pattern
        """
        from parser import parse_lambda
        query = '''
            SELECT literal FROM lambda_terms 
            WHERE identifier REGEXP ?
        ''' if regex else '''
            SELECT literal FROM lambda_terms 
            WHERE identifier = ?
        '''
        cursor = self.conn.execute(query, (identifier,))
        result = cursor.fetchone()
        return parse_lambda(result[0]) if result else None

    def delete_term(self, identifier: str, regex: bool = False) -> None:
        """Delete term(s) by identifier or regex pattern
        
        Args:
            identifier: Exact ID or partial pattern if regex=True
            regex: Use partial matching (e.g. "church" matches "church_2")
        """
        query = '''
            DELETE FROM lambda_terms 
            WHERE identifier REGEXP ?
        ''' if regex else '''
            DELETE FROM lambda_terms 
            WHERE identifier = ?
        '''
        self.conn.execute(query, (f'.*{identifier}.*',) if regex else (identifier,))
        self.conn.commit()
    
    def get_all_terms(
        self,
        identifier_pattern: Optional[str] = None,
        literal_pattern: Optional[str] = None,
        case_sensitive: bool = False,
        skip_invalid: bool = True,
        forced: bool = False
    ) -> list[tuple[str, Term]]:
        """Retrieve terms with regex or exact matching"""
        from parser import parse_lambda
        import re

        # Build base query
        query = 'SELECT identifier, literal FROM lambda_terms'
        params = []
        conditions = []

        # Identifier pattern or exact matching
        if identifier_pattern:
            if forced:
                params.append(identifier_pattern)
                conditions.append("identifier = ?" if case_sensitive else "LOWER(identifier) = LOWER(?)")
            else:
                flags = 0 if case_sensitive else re.IGNORECASE
                params.append(identifier_pattern)
                conditions.append(
                    "identifier REGEXP ?" if case_sensitive 
                    else "LOWER(identifier) REGEXP LOWER(?)"
                )

        # Literal pattern or exact matching
        if literal_pattern:
            if forced:
                params.append(literal_pattern)
                conditions.append("literal = ?" if case_sensitive else "LOWER(literal) = LOWER(?)")
            else:
                flags = 0 if case_sensitive else re.IGNORECASE
                params.append(literal_pattern)
                conditions.append(
                    "literal REGEXP ?" if case_sensitive
                    else "LOWER(literal) REGEXP LOWER(?)"
                )

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute query
        cursor = self.conn.execute(query, params)
        results = []
        
        # Process results
        for row in cursor.fetchall():
            try:
                term = parse_lambda(row[1])
                results.append((row[0], term))
            except ParseError as e:
                if not skip_invalid:
                    raise ParseError(f"Invalid term {row[0]}") from e
                continue
                
        return results
    
    def close(self):
        """Close database connection"""
        self.conn.close()

