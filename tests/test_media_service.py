# tests/test_media_service.py
from src.database.models import MediaType, CoreStatus

def test_get_or_create_user(media_service):
    # Проверяем создание нового пользователя
    user = media_service.get_or_create_user("test_user")
    assert user.id is not None
    assert user.username == "test_user"

def test_get_existing_user(media_service):
    # Создаем пользователя первый раз
    media_service.get_or_create_user("alice")
    
    # Пытаемся получить его же (не должно упасть с IntegrityError)
    user = media_service.get_or_create_user("alice")
    assert user.id is not None
    # В базе по-прежнему должен быть 1 юзер (можно проверить через count)

def test_add_media_to_user(media_service):
    user = media_service.get_or_create_user("bob")
    item = media_service.add_media(user.id, "Inception", MediaType.VIDEO)
    
    assert item.title == "Inception"
    assert item.user_id == user.id
    assert item.core_status == CoreStatus.PLANNED

def test_get_user_library(media_service):
    user = media_service.get_or_create_user("charlie")
    media_service.add_media(user.id, "Book 1", MediaType.TEXT)
    media_service.add_media(user.id, "Movie 1", MediaType.VIDEO)
    
    library = media_service.get_user_library(user.id)
    assert len(library) == 2