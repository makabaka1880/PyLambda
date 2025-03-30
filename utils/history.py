# Create by Sean L. on Mar. 28
# 
# Lambda Calculus Implementation
# utils/history.py
# 
# Makabaka1880, 2025. All rights reserved.

import sqlite3
from typing import Optional
from dotenv import load_dotenv
from models.exceptions import InvalidTermError, ParseError
import os
import re
from models.model import Term

load_dotenv()

# MARK: HistoryStore Class
class HistoryStore:
    """Minimal history storage persistant layer with index-based overwrite semantics"""
    
    # MARK: Initialization
    def __init__(self, db_path: str = 'file::memory:?cache=shared', uri: bool = True):
        r"""Initialize the history store with a SQLite database.
        :param db_path: Path to the SQLite database file.
        :param uri: Whether to use URI filename.
        """
        self.conn = sqlite3.connect(db_path, uri=uri)
        self._init_table()

    # MARK: Table Initialization
    def _init_table(self):
        """Create or overwrite history table"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                literal TEXT NOT NULL
            ) WITHOUT ROWID
        ''')
        self.conn.commit()
    
    # MARK: Clear History
    def clear(self) -> None:
        """Clear the history table"""
        self.conn.execute('DROP TABLE IF EXISTS history')
        self.conn.execute('''
            CREATE TABLE history (
                id INTEGER PRIMARY KEY,
                literal TEXT NOT NULL
            ) WITHOUT ROWID
        ''')

    # MARK: Insert Entry
    def insert(self, index: int, literal: str) -> None:
        """Insert/overwrite entry at specified index"""
        
        self.conn.execute('''
            INSERT OR REPLACE INTO history (id, literal)
            VALUES (?, ?)
        ''', (index, literal))
        self.conn.commit()

    # MARK: Fetch Entry
    def fetch(self, index: int) -> Term:
        """Get literal by index, raises IndexError if missing"""
        from parser import parse_lambda
        from utils.persistence import TermDB
        
        # Validate index
        if not isinstance(index, int) or index < 0:
            raise IndexError(f"Invalid index: {index}")
        
        # Fetch the literal
        cursor = self.conn.execute('''
            SELECT literal FROM history
            WHERE id = ?
        ''', (index,))
        
        if result := cursor.fetchone():
            return parse_lambda(result[0], TermDB(), self)
        else:
            raise IndexError(f"Index {index} not found in history")

    # MARK: Close Connection
    def close(self):
        """Close database connection"""
        self.conn.close()