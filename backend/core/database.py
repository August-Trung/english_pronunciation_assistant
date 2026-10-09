import os
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# SQLite database file path (persisted on disk)
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./fluent_english.db")

engine = create_engine(
    DB_PATH,
    connect_args={"check_same_thread": False} if DB_PATH.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# ORM Models
# -------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_sub = Column(String(100), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    equipped_badge = Column(String(50), nullable=True)
    daily_goal = Column(Integer, default=5)
    streak_count = Column(Integer, default=0)
    last_practice_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions = relationship("PracticeSession", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    weak_words = relationship("UserWeakWord", back_populates="user", cascade="all, delete-orphan")


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mode = Column(String(20), nullable=False, default="speaking")  # 'speaking' | 'reading'
    grade_level = Column(String(20), nullable=False, default="primary")
    topic = Column(Text, nullable=False)
    transcribed_text = Column(Text, nullable=False)
    overall_score = Column(Float, nullable=False)
    reading_accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    breakdown = relationship("PracticeBreakdown", back_populates="session", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("PedagogicalFeedback", back_populates="session", uselist=False, cascade="all, delete-orphan")
    word_analyses = relationship("WordAnalysis", back_populates="session", cascade="all, delete-orphan")


class PracticeBreakdown(Base):
    __tablename__ = "practice_breakdowns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False)
    pronunciation_score = Column(Float, default=0.0)
    fluency_score = Column(Float, default=0.0)
    grammar_score = Column(Float, default=0.0)
    vocabulary_score = Column(Float, default=0.0)
    interaction_score = Column(Float, default=0.0)
    clarity_confidence = Column(Float, default=0.0)

    session = relationship("PracticeSession", back_populates="breakdown")


class PedagogicalFeedback(Base):
    __tablename__ = "pedagogical_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False)
    feedback_text = Column(Text, nullable=False)

    session = relationship("PracticeSession", back_populates="feedback")


class WordAnalysis(Base):
    __tablename__ = "word_analyses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # 'correct' | 'partial' | 'missing'

    session = relationship("PracticeSession", back_populates="word_analyses")


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_code = Column(String(50), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")


class UserWeakWord(Base):
    __tablename__ = "user_weak_words"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(100), nullable=False)
    mistake_count = Column(Integer, default=1)
    is_mastered = Column(Boolean, default=False)
    last_practiced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="weak_words")
