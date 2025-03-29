# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# utils/persistence.py
# 
# Makabaka1880, 2025. All rights reserved.

import sqlite3
from typing import Optional
from models.model import Term
from dotenv import load_dotenv
import os

load_dotenv()


class TermDB:
    """SQLite persistence layer for lambda terms"""
    
    def __init__(self, db_path: str = os.getenv('DEFAULT_DB_PATH')):
        self.conn = sqlite3.connect(db_path)
        self.conn.create_function('REGEXP', 2, self._regexp)  # Add regex support
        self._create_table()

    @staticmethod
    def _regexp(pattern: str, identifier: str) -> bool:
        """SQLite regex helper function"""
        return re.search(pattern, identifier, re.IGNORECASE) is not None
    
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
        """Store a term with its literal representation"""
        self.conn.execute('''
            INSERT OR REPLACE INTO lambda_terms (identifier, literal)
            VALUES (?, ?)
        ''', (identifier, term.literal()))
        self.conn.commit()
        
    def get_term(self, identifier: str, regex: bool = False) -> Optional[Term]:
        """Retrieve term(s) by identifier or regex pattern"""
        from parser import parse_lambda
        query = '''
            SELECT literal FROM lambda_terms 
            WHERE identifier REGEXP ? 
        ''' if regex else '''
            SELECT literal FROM lambda_terms 
            WHERE identifier = ?
        '''
        cursor = self.conn.execute(query, (identifier,))
        return parse_lambda(cursor.fetchone()[0]) if cursor.fetchone() else None

    def delete_term(self, identifier: str, regex: bool = False) -> None:
        """Delete term(s) by identifier or regex pattern"""
        query = '''
            DELETE FROM lambda_terms 
            WHERE identifier REGEXP ?
        ''' if regex else '''
            DELETE FROM lambda_terms 
            WHERE identifier = ?
        '''
        self.conn.execute(query, (identifier,))
        self.conn.commit()
    
    def get_all_terms(self) -> list:
        """Retrieve all stored terms"""
        cursor = self.conn.execute('''
            SELECT identifier, literal FROM lambda_terms
        ''')
        from parser import parse_lambda
        return [(row[0], parse_lambda(row[1])) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.conn.close()

