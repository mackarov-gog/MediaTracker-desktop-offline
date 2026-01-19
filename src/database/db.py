# src/database/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


DATABASE_URL = "sqlite:///data/tracker.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создает все таблицы, если они еще не существуют"""
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    Base.metadata.create_all(bind=engine)

def get_db():
    """Генератор сессий для использования в контекстных менеджерах"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()