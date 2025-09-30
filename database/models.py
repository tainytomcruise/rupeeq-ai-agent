import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for SQLite operations"""

    def __init__(self, db_path: str = None):
        # ✅ Handle Vercel deployment
        if os.environ.get("VERCEL"):
            # Ephemeral storage on Vercel
            self.db_path = "/tmp/rupeeq_ai.db"
            logger.info(f"Running on Vercel. Using temp DB at {self.db_path}")
        else:
            # Local persistent storage
            self.db_path = db_path or "rupeeq_ai.db"
            logger.info(f"Running locally. Using DB at {self.db_path}")

        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Example table — replace/add your own schema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def add_user(self, name: str, email: str):
        """Insert a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (?, ?)", 
                    (name, email)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            raise

    def get_users(self):
        """Fetch all users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
