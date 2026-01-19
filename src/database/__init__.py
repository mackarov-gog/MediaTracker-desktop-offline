# Из файла db.py вытягиваем функции инициализации и сессию
from .db import init_db, SessionLocal, get_db

# Из файла models.py вытягиваем все модели, чтобы они были под рукой
from .models import (
    Base, User, MediaItem, SubItem,
    Universe, Group, Tag,
    MediaType, CoreStatus
)

# Список того, что будет доступно при импорте через "from src.database import *"
__all__ = [
    "init_db",
    "SessionLocal",
    "get_db",
    "Base",
    "User",
    "MediaItem",
    "SubItem",
    "Universe",
    "Group",
    "Tag",
    "MediaType",
    "CoreStatus"
]
