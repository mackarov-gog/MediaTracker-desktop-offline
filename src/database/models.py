# src/database/models.py
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    Enum, Table, Boolean, Text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# --- Enums (Перечисления) ---

class MediaType(enum.Enum):
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"


class CoreStatus(enum.Enum):
    PLANNED = "planned"  # В плане
    ON_HOLD = "on_hold"  # Отложено
    DROPPED = "dropped"  # Брошено
    WAITING = "waiting"  # Жду выхода
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


# --- Base ---

class Base(DeclarativeBase):
    pass


# --- Association Tables (Связующие таблицы) ---

# Связь Многие-ко-Многим: Медиа <-> Теги
media_tags_association = Table(
    "media_tags",
    Base.metadata,
    Column("media_item_id", ForeignKey("media_items.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


# --- Models ---

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Отношения
    media_items: Mapped[List["MediaItem"]] = relationship(back_populates="user")
    tags: Mapped[List["Tag"]] = relationship(back_populates="user")
    universes: Mapped[List["Universe"]] = relationship(back_populates="user")

    # Настройки кастомных статусов (UserStatus)
    status_settings: Mapped[List["UserStatusSetting"]] = relationship(back_populates="user")


class UserStatusSetting(Base):
    """
    Таблица для переименования статусов.
    Например: User 1 для типа BOOK называет статус FINISHED как "Прочитано".
    """
    __tablename__ = "user_status_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType))
    core_status: Mapped[CoreStatus] = mapped_column(Enum(CoreStatus))
    custom_label: Mapped[str] = mapped_column(String(50))  # "Прочитано", "Просмотрено"

    user: Mapped["User"] = relationship(back_populates="status_settings")


class Universe(Base):
    """Вселенная (Marvel, Middle Earth). Привязана к User, чтобы списки были личными."""
    __tablename__ = "universes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="universes")
    groups: Mapped[List["Group"]] = relationship(back_populates="universe")


class Group(Base):
    """Франшиза или цикл (Гарри Поттер, Трилогия Трауна)."""
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    universe_id: Mapped[Optional[int]] = mapped_column(ForeignKey("universes.id"))
    name: Mapped[str] = mapped_column(String(100))

    universe: Mapped["Universe"] = relationship(back_populates="groups")
    media_items: Mapped[List["MediaItem"]] = relationship(back_populates="group")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(50))

    user: Mapped["User"] = relationship(back_populates="tags")
    # Обратная связь для many-to-many
    media_items: Mapped[List["MediaItem"]] = relationship(
        secondary=media_tags_association, back_populates="tags"
    )


class MediaItem(Base):
    """Основная сущность (Книга, Фильм, Игра)."""
    __tablename__ = "media_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"))

    title: Mapped[str] = mapped_column(String(200))
    original_title: Mapped[Optional[str]] = mapped_column(String(200))
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType))

    # Статус
    core_status: Mapped[CoreStatus] = mapped_column(Enum(CoreStatus), default=CoreStatus.PLANNED)

    # Прогресс (например, 5/10)
    current_progress: Mapped[int] = mapped_column(default=0)
    total_progress: Mapped[Optional[int]] = mapped_column(default=None)  # Если None, то неизвестно или бесконечно

    score: Mapped[Optional[int]] = mapped_column(Integer)  # Оценка 1-10
    comment: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    user: Mapped["User"] = relationship(back_populates="media_items")
    group: Mapped["Group"] = relationship(back_populates="media_items")
    sub_items: Mapped[List["SubItem"]] = relationship(back_populates="media_item", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship(
        secondary=media_tags_association, back_populates="media_items"
    )


class SubItem(Base):
    """Части составного медиа (Серия, Глава, DLC)."""
    __tablename__ = "sub_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    media_item_id: Mapped[int] = mapped_column(ForeignKey("media_items.id"))

    title: Mapped[str] = mapped_column(String(200))  # "S01E01 - Начало"
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)  # Для сортировки

    media_item: Mapped["MediaItem"] = relationship(back_populates="sub_items")
