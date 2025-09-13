#!/usr/bin/env python3
"""
RupeeQ AI Calling Agent - Database Models
SQLite database models and operations for the AI calling agent
"""

import sqlite3
import json
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Call:
    """Call data model"""
    id: Optional[int] = None
    customer_name: str = ""
    agent_name: str = ""
    phone_number: Optional[str] = None
    status: str = "in_progress"  # in_progress, completed, failed, not_connected, busy
    outcome: Optional[str] = None  # interested, not_interested, call_back, unknown
    sentiment_score: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: int = 0  # in seconds
    language: str = "en-IN"
    customer_data: Optional[str] = None  # JSON string
    created_at: Optional[str] = None

@dataclass
class Transcript:
    """Transcript data model"""
    id: Optional[int] = None
    call_id: int = 0
    speaker: str = ""  # agent, customer
    message: str = ""
    timestamp: Optional[str] = None
    sentiment: Optional[float] = None
    intent: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics data model"""
    id: Optional[int] = None
    date: str = ""
    total_calls: int = 0
    connected_calls: int = 0
    not_connected: int = 0
    busy: int = 0
    failed: int = 0
    interested: int = 0
    not_interested: int = 0
    call_back: int = 0
    avg_duration: float = 0.0
    avg_sentiment: float = 0.0
    created_at: Optional[str] = None

class DatabaseManager:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_path: str = 'rupeeq_ai.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create calls table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_name TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        phone_number TEXT,
                        status TEXT NOT NULL DEFAULT 'in_progress',
                        outcome TEXT,
                        sentiment_score REAL,
                        start_time DATETIME NOT NULL,
                        end_time DATETIME,
                        duration INTEGER DEFAULT 0,
                        language TEXT DEFAULT 'en-IN',
                        customer_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create transcripts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transcripts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        call_id INTEGER NOT NULL,
                        speaker TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        sentiment REAL,
                        intent TEXT,
                        FOREIGN KEY (call_id) REFERENCES calls (id) ON DELETE CASCADE
                    )
                ''')
                
                # Create performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL UNIQUE,
                        total_calls INTEGER DEFAULT 0,
                        connected_calls INTEGER DEFAULT 0,
                        not_connected INTEGER DEFAULT 0,
                        busy INTEGER DEFAULT 0,
                        failed INTEGER DEFAULT 0,
                        interested INTEGER DEFAULT 0,
                        not_interested INTEGER DEFAULT 0,
                        call_back INTEGER DEFAULT 0,
                        avg_duration REAL DEFAULT 0,
                        avg_sentiment REAL DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_calls_date ON calls(start_time)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_transcripts_call_id ON transcripts(call_id)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def create_call(self, call: Call) -> int:
        """Create a new call record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO calls (
                        customer_name, agent_name, phone_number, status, start_time,
                        language, customer_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    call.customer_name, call.agent_name, call.phone_number,
                    call.status, call.start_time or datetime.now().isoformat(),
                    call.language, call.customer_data
                ))
                call_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created call with ID: {call_id}")
                return call_id
                
        except Exception as e:
            logger.error(f"Error creating call: {e}")
            raise
    
    def update_call(self, call_id: int, updates: Dict[str, Any]) -> bool:
        """Update call record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['status', 'outcome', 'sentiment_score', 'end_time', 'duration', 'customer_data']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                query = f"UPDATE calls SET {', '.join(set_clauses)} WHERE id = ?"
                values.append(call_id)
                
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Updated call {call_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error updating call: {e}")
            raise
    
    def get_call(self, call_id: int) -> Optional[Call]:
        """Get call by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM calls WHERE id = ?', (call_id,))
                row = cursor.fetchone()
                
                if row and len(row) >= 13:
                    return Call(
                        id=row[0],
                        customer_name=row[1],
                        agent_name=row[2],
                        phone_number=row[3],
                        status=row[4],
                        outcome=row[5],
                        sentiment_score=row[6],
                        start_time=row[7],
                        end_time=row[8],
                        duration=row[9],
                        language=row[10],
                        customer_data=row[11],
                        created_at=row[12]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting call: {e}")
            raise
    
    def get_calls(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Call]:
        """Get calls with optional filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM calls WHERE 1=1"
                params = []
                
                if filters:
                    if filters.get('start_date'):
                        query += " AND DATE(start_time) >= ?"
                        params.append(filters['start_date'])
                    
                    if filters.get('end_date'):
                        query += " AND DATE(start_time) <= ?"
                        params.append(filters['end_date'])
                    
                    if filters.get('status'):
                        query += " AND status = ?"
                        params.append(filters['status'])
                    
                    if filters.get('outcome'):
                        query += " AND outcome = ?"
                        params.append(filters['outcome'])
                
                query += " ORDER BY start_time DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                calls = []
                for row in rows:
                    # Ensure we have enough columns
                    if len(row) >= 13:
                        calls.append(Call(
                            id=row[0],
                            customer_name=row[1],
                            agent_name=row[2],
                            phone_number=row[3],
                            status=row[4],
                            outcome=row[5],
                            sentiment_score=row[6],
                            start_time=row[7],
                            end_time=row[8],
                            duration=row[9],
                            language=row[10],
                            customer_data=row[11],
                            created_at=row[12]
                        ))
                    else:
                        logger.warning(f"Row has insufficient columns: {len(row)}")
                
                return calls
                
        except Exception as e:
            logger.error(f"Error getting calls: {e}")
            raise
    
    def add_transcript(self, transcript: Transcript) -> int:
        """Add transcript entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transcripts (call_id, speaker, message, timestamp, sentiment, intent)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    transcript.call_id, transcript.speaker, transcript.message,
                    transcript.timestamp or datetime.now().isoformat(),
                    transcript.sentiment, transcript.intent
                ))
                transcript_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Added transcript with ID: {transcript_id}")
                return transcript_id
                
        except Exception as e:
            logger.error(f"Error adding transcript: {e}")
            raise
    
    def get_transcripts(self, call_id: int) -> List[Transcript]:
        """Get transcripts for a call"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM transcripts 
                    WHERE call_id = ? 
                    ORDER BY timestamp ASC
                ''', (call_id,))
                rows = cursor.fetchall()
                
                transcripts = []
                for row in rows:
                    transcripts.append(Transcript(
                        id=row[0],
                        call_id=row[1],
                        speaker=row[2],
                        message=row[3],
                        timestamp=row[4],
                        sentiment=row[5],
                        intent=row[6]
                    ))
                
                return transcripts
                
        except Exception as e:
            logger.error(f"Error getting transcripts: {e}")
            raise
    
    def get_daily_statistics(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Get daily statistics"""
        try:
            if target_date is None:
                target_date = date.today()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get basic counts
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_calls,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as connected_calls,
                        SUM(CASE WHEN status = 'not_connected' THEN 1 ELSE 0 END) as not_connected,
                        SUM(CASE WHEN status = 'busy' THEN 1 ELSE 0 END) as busy,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                        AVG(duration) as avg_duration,
                        AVG(sentiment_score) as avg_sentiment
                    FROM calls 
                    WHERE DATE(start_time) = ?
                ''', (target_date.isoformat(),))
                
                stats_row = cursor.fetchone()
                
                # Ensure we have a valid result
                if not stats_row:
                    stats_row = (0, 0, 0, 0, 0, 0, 0)
                
                # Get outcome counts
                cursor.execute('''
                    SELECT outcome, COUNT(*) 
                    FROM calls 
                    WHERE DATE(start_time) = ? AND outcome IS NOT NULL
                    GROUP BY outcome
                ''', (target_date.isoformat(),))
                
                outcome_counts = dict(cursor.fetchall())
                
                # Ensure we have valid outcome counts
                if not outcome_counts:
                    outcome_counts = {}
                
                # Calculate connection rate
                total_calls = stats_row[0] if stats_row and len(stats_row) > 0 else 0
                connected_calls = stats_row[1] if stats_row and len(stats_row) > 1 else 0
                connection_rate = (connected_calls / total_calls * 100) if total_calls > 0 else 0
                
                return {
                    'date': target_date.isoformat(),
                    'total_calls': total_calls,
                    'connected_calls': connected_calls,
                    'not_connected': stats_row[2] if stats_row and len(stats_row) > 2 else 0,
                    'busy': stats_row[3] if stats_row and len(stats_row) > 3 else 0,
                    'failed': stats_row[4] if stats_row and len(stats_row) > 4 else 0,
                    'connection_rate': round(connection_rate, 1),
                    'avg_duration': stats_row[5] if stats_row and len(stats_row) > 5 else 0,
                    'avg_sentiment': stats_row[6] if stats_row and len(stats_row) > 6 else 0,
                    'outcome_counts': {
                        'interested': outcome_counts.get('interested', 0),
                        'not_interested': outcome_counts.get('not_interested', 0),
                        'call_back': outcome_counts.get('call_back', 0),
                        'unknown': outcome_counts.get('unknown', 0)
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting daily statistics: {e}")
            raise
    
    def update_performance_metrics(self, target_date: Optional[date] = None):
        """Update performance metrics for a date"""
        try:
            if target_date is None:
                target_date = date.today()
            
            stats = self.get_daily_statistics(target_date)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO performance_metrics (
                        date, total_calls, connected_calls, not_connected, busy, failed,
                        interested, not_interested, call_back, avg_duration, avg_sentiment
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    target_date.isoformat(),
                    stats['total_calls'],
                    stats['connected_calls'],
                    stats['not_connected'],
                    stats['busy'],
                    stats['failed'],
                    stats['outcome_counts']['interested'],
                    stats['outcome_counts']['not_interested'],
                    stats['outcome_counts']['call_back'],
                    stats['avg_duration'],
                    stats['avg_sentiment']
                ))
                conn.commit()
                logger.info(f"Updated performance metrics for {target_date}")
                
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
            raise
    
    def get_performance_metrics(self, days: int = 30) -> List[PerformanceMetrics]:
        """Get performance metrics for the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM performance_metrics 
                    WHERE date >= DATE('now', '-{} days')
                    ORDER BY date DESC
                '''.format(days))
                rows = cursor.fetchall()
                
                metrics = []
                for row in rows:
                    metrics.append(PerformanceMetrics(
                        id=row[0],
                        date=row[1],
                        total_calls=row[2],
                        connected_calls=row[3],
                        not_connected=row[4],
                        busy=row[5],
                        failed=row[6],
                        interested=row[7],
                        not_interested=row[8],
                        call_back=row[9],
                        avg_duration=row[10],
                        avg_sentiment=row[11],
                        created_at=row[12]
                    ))
                
                return metrics
                
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise
    
    def search_transcripts(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search transcripts by keyword"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.*, c.customer_name, c.start_time
                    FROM transcripts t
                    JOIN calls c ON t.call_id = c.id
                    WHERE t.message LIKE ?
                    ORDER BY t.timestamp DESC
                    LIMIT ?
                ''', (f'%{keyword}%', limit))
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'transcript_id': row[0],
                        'call_id': row[1],
                        'speaker': row[2],
                        'message': row[3],
                        'timestamp': row[4],
                        'sentiment': row[5],
                        'intent': row[6],
                        'customer_name': row[7],
                        'call_start_time': row[8]
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching transcripts: {e}")
            raise
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data (older than specified days)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old calls and associated transcripts
                cursor.execute('''
                    DELETE FROM calls 
                    WHERE DATE(start_time) < DATE('now', '-{} days')
                '''.format(days))
                
                deleted_calls = cursor.rowcount
                logger.info(f"Cleaned up {deleted_calls} old calls")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    # Test database operations
    db = DatabaseManager()
    
    # Test creating a call
    test_call = Call(
        customer_name="Test Customer",
        agent_name="Test Agent",
        status="in_progress",
        start_time=datetime.now().isoformat(),
        language="en-IN"
    )
    
    call_id = db.create_call(test_call)
    print(f"Created call with ID: {call_id}")
    
    # Test adding transcript
    test_transcript = Transcript(
        call_id=call_id,
        speaker="agent",
        message="Hello, how can I help you today?",
        timestamp=datetime.now().isoformat()
    )
    
    transcript_id = db.add_transcript(test_transcript)
    print(f"Added transcript with ID: {transcript_id}")
    
    # Test getting call
    retrieved_call = db.get_call(call_id)
    print(f"Retrieved call: {retrieved_call.customer_name}")
    
    # Test getting transcripts
    transcripts = db.get_transcripts(call_id)
    print(f"Retrieved {len(transcripts)} transcripts")
    
    # Test daily statistics
    stats = db.get_daily_statistics()
    print(f"Daily stats: {stats}")
    
    print("Database operations test completed successfully!")
