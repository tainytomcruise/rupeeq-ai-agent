# In database/models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import enum
import os

# Use an environment variable for the database URL for Vercel compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///rupeeq_ai_agent.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CallStatus(enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    busy = "busy"
    not_connected = "not_connected"

class CallOutcome(enum.Enum):
    interested = "interested"
    not_interested = "not_interested"
    call_back = "call_back"
    dnc = "dnc"
    unknown = "unknown"

class Call(Base):
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True, index=True, nullable=False)
    customer_name = Column(String, nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.in_progress)
    outcome = Column(Enum(CallOutcome), default=CallOutcome.unknown)
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True) # <-- SYNTAX ERROR FIXED
    sentiment_score = Column(Float, nullable=True)
    call_type = Column(String, default='ai_agent')
    
    def save(self):
        db = SessionLocal()
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
        finally:
            db.close()

    # NOTE: These are placeholder methods. You must add your own database query logic.
    @staticmethod
    def get_recent_calls(limit=50): return []
    @staticmethod
    def get_calls_today(): return {'total_calls': 0, 'status_counts': {}, 'avg_duration': 0, 'avg_sentiment': 0, 'outcome_counts': {}}
    @staticmethod
    def get_filtered_calls(filters): return []
    @staticmethod
    def get_call_by_id(call_id): return None

class CallTranscript(Base):
    __tablename__ = 'call_transcripts'
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, index=True, nullable=False)
    speaker = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    def save(self):
        db = SessionLocal()
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
        finally:
            db.close()

    @staticmethod
    def get_call_transcripts(call_id): return []

def init_db():
    Base.metadata.create_all(bind=engine)
