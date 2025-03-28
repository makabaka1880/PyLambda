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
        self._create_table()
        
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
        
    def get_term(self, identifier: str) -> Optional[Term]:
        from parser import parse_lambda
        """Retrieve a term by identifier"""
        cursor = self.conn.execute('''
            SELECT literal FROM lambda_terms WHERE identifier = ?
        ''', (identifier,))
        
        if result := cursor.fetchone():
            return parse_lambda(result[0])
        return None
    
    def delete_term(self, identifier: str) -> None:
        """Remove a term from storage"""
        self.conn.execute('''
            DELETE FROM lambda_terms WHERE identifier = ?
        ''', (identifier,))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()

