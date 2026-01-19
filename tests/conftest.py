# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.services.media_service import MediaService

@pytest.fixture
def db_session():
    # Создаем базу в памяти (она пустая)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session  # Здесь запускается сам тест
    
    session.close() # После теста закрываем

@pytest.fixture
def media_service(db_session):
    # Создаем сервис, подсовывая ему временную сессию
    return MediaService(db_session)