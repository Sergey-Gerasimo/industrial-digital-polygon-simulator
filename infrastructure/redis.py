from typing import Union, Optional, TypeVar, Type, Dict, Any
from uuid import UUID
import json
import logging

try:
    from redis.asyncio import Redis  # type: ignore
    from redis.exceptions import (  # type: ignore
        RedisError,
        ConnectionError as RedisConnectionError,
        TimeoutError as RedisTimeoutError,
    )
except ImportError:
    try:
        import aioredis  # type: ignore

        Redis = aioredis.Redis
        # Для aioredis исключения могут быть другими
        RedisError = Exception
        RedisConnectionError = Exception
        RedisTimeoutError = Exception
    except ImportError:
        # Если библиотека не установлена, создаем заглушку для типов
        from typing import Any

        Redis = Any  # type: ignore
        RedisError = Exception
        RedisConnectionError = Exception
        RedisTimeoutError = Exception

from .abstract_repository import AbstractRepository
from domain import RedisSerializable

logger = logging.getLogger(__name__)


EntityModel = TypeVar(
    "EntityModel", bound=Union[RedisSerializable, Dict[str, Any], str, bytes]
)


class RedisRepository(AbstractRepository[EntityModel]):
    """Репозиторий для работы с Redis.

    Поддерживает сохранение, получение, обновление и удаление данных по ключу.
    Может работать с объектами RedisSerializable, словарями, строками и байтами.
    """

    def __init__(
        self,
        redis_client: Redis,
        key_prefix: str = "",
        default_ttl: Optional[int] = None,
    ):
        """
        Args:
            redis_client: Экземпляр Redis клиента
            key_prefix: Префикс для всех ключей (по умолчанию пустая строка)
            default_ttl: Время жизни ключей в секундах (по умолчанию без ограничения)
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl

    def _make_key(self, key: Union[UUID, str]) -> str:
        """Формирует ключ Redis с учетом префикса.

        Args:
            key: UUID или строка для ключа

        Returns:
            Полный ключ с префиксом
        """
        key_str = str(key) if isinstance(key, UUID) else key
        if self.key_prefix:
            return f"{self.key_prefix}:{key_str}"
        return key_str

    def _serialize_value(self, value: EntityModel) -> str:
        """Сериализует значение для сохранения в Redis.

        Args:
            value: Значение для сериализации (RedisSerializable, dict, str, bytes)

        Returns:
            Строка JSON или байты
        """
        if isinstance(value, RedisSerializable):
            return value.to_redis_json()
        elif isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False, default=str)
        elif isinstance(value, str):
            return value
        elif isinstance(value, bytes):
            return value.decode("utf-8")
        else:
            return json.dumps(value, ensure_ascii=False, default=str)

    def _deserialize_value(
        self,
        value: Optional[Union[str, bytes]],
        value_type: Optional[Type[EntityModel]] = None,
    ) -> Optional[Union[Dict[str, Any], str, bytes]]:
        """Десериализует значение из Redis.

        Args:
            value: Значение из Redis (может быть строкой или байтами в зависимости от decode_responses)
            value_type: Тип для десериализации (опционально)

        Returns:
            Десериализованное значение
        """
        if value is None:
            return None

        # Если значение - байты, декодируем в строку
        # (если decode_responses=False в Redis клиенте)
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError:
                # Если не удалось декодировать, возвращаем как байты
                return value

        # Если value_type указан и это RedisSerializable, возвращаем словарь
        # (полное восстановление объекта должно быть реализовано на уровне использования)
        if (
            value_type
            and isinstance(value_type, type)
            and issubclass(value_type, RedisSerializable)
        ):
            try:
                data = json.loads(value)
                # Создание экземпляра из словаря (базовая реализация)
                # В реальности может потребоваться более сложная логика
                return data
            except (json.JSONDecodeError, TypeError):
                return None

        # Пытаемся распарсить как JSON, если не получается - возвращаем как строку
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Если не JSON, возвращаем как строку
            return value

    async def save(
        self,
        model: EntityModel,
        key: Optional[Union[UUID, str]] = None,
        ttl: Optional[int] = None,
    ) -> Union[EntityModel, None]:
        """Сохраняет модель в Redis.

        Args:
            model: Модель для сохранения
            key: Ключ для сохранения (опционально, если None - используется из модели)
            ttl: Время жизни в секундах (по умолчанию используется default_ttl)

        Returns:
            Сохраненная модель или None в случае ошибки
        """
        redis_key = None
        try:
            # Определяем ключ
            if key is None:
                # Пытаемся получить ключ из модели
                if isinstance(model, dict) and "id" in model:
                    key = model["id"]
                elif hasattr(model, "id"):
                    key = getattr(model, "id")
                elif hasattr(model, "_id"):
                    key = getattr(model, "_id")
                else:
                    raise ValueError(
                        "Key must be provided or model must have 'id' or '_id' attribute"
                    )

            redis_key = self._make_key(key)
            serialized_value = self._serialize_value(model)

            ttl_to_use = ttl if ttl is not None else self.default_ttl

            # Используем параметр ex в set для более элегантной установки TTL
            if ttl_to_use:
                await self.redis.set(redis_key, serialized_value, ex=ttl_to_use)
            else:
                await self.redis.set(redis_key, serialized_value)

            return model
        except (RedisConnectionError, RedisTimeoutError) as e:
            key_str = (
                redis_key
                if redis_key
                else (str(key) if "key" in locals() else "unknown")
            )
            logger.error(f"Redis connection error while saving key {key_str}: {e}")
            return None
        except RedisError as e:
            key_str = (
                redis_key
                if redis_key
                else (str(key) if "key" in locals() else "unknown")
            )
            logger.error(f"Redis error while saving key {key_str}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while saving to Redis: {e}", exc_info=True)
            return None

    async def get(
        self,
        id: Union[UUID, str],
        value_type: Optional[Type[EntityModel]] = None,
    ) -> Union[EntityModel, None]:
        """Получает значение из Redis по ключу.

        Args:
            id: Ключ для поиска
            value_type: Тип для десериализации (опционально)

        Returns:
            Десериализованное значение или None
        """
        try:
            redis_key = self._make_key(id)
            value = await self.redis.get(redis_key)

            if value is None:
                return None

            return self._deserialize_value(value, value_type)
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.error(f"Redis connection error while getting key {redis_key}: {e}")
            return None
        except RedisError as e:
            logger.error(f"Redis error while getting key {redis_key}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while getting from Redis: {e}", exc_info=True
            )
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[EntityModel, None]:
        """Удаляет значение из Redis по ключу.

        Args:
            id: Ключ для удаления

        Returns:
            Удаленное значение или None
        """
        try:
            redis_key = self._make_key(id)
            value = await self.redis.get(redis_key)

            if value is None:
                return None

            deleted = await self.redis.delete(redis_key)

            # Возвращаем десериализованное значение только если ключ был удален
            if deleted:
                return self._deserialize_value(value)
            return None
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.error(f"Redis connection error while deleting key {id}: {e}")
            return None
        except RedisError as e:
            logger.error(f"Redis error while deleting key {id}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while deleting from Redis: {e}", exc_info=True
            )
            return None

    async def update(
        self,
        id: Union[UUID, str],
        model: EntityModel,
        ttl: Optional[int] = None,
    ) -> Union[EntityModel, None]:
        """Обновляет значение в Redis по ключу.

        Args:
            id: Ключ для обновления
            model: Новое значение для сохранения
            ttl: Время жизни в секундах (по умолчанию используется default_ttl)

        Returns:
            Обновленная модель или None в случае ошибки
        """
        try:
            redis_key = self._make_key(id)
            serialized_value = self._serialize_value(model)

            ttl_to_use = ttl if ttl is not None else self.default_ttl

            # Используем параметр ex в set для более элегантной установки TTL
            if ttl_to_use:
                await self.redis.set(redis_key, serialized_value, ex=ttl_to_use)
            else:
                await self.redis.set(redis_key, serialized_value)

            return model
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.error(f"Redis connection error while updating key {redis_key}: {e}")
            return None
        except RedisError as e:
            logger.error(f"Redis error while updating key {redis_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while updating Redis: {e}", exc_info=True)
            return None

    async def exists(self, id: Union[UUID, str]) -> bool:
        """Проверяет существование ключа в Redis.

        Args:
            id: Ключ для проверки

        Returns:
            True если ключ существует, иначе False
        """
        try:
            redis_key = self._make_key(id)
            # exists возвращает количество существующих ключей (0 или больше)
            result = await self.redis.exists(redis_key)
            return bool(result)
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.error(
                f"Redis connection error while checking existence of key {redis_key}: {e}"
            )
            return False
        except RedisError as e:
            logger.error(
                f"Redis error while checking existence of key {redis_key}: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error while checking key existence: {e}", exc_info=True
            )
            return False

    async def get_ttl(self, id: Union[UUID, str]) -> Optional[int]:
        """Получает оставшееся время жизни ключа в секундах.

        Args:
            id: Ключ

        Returns:
            TTL в секундах, -1 если ключ существует без TTL, None если ключ не существует
        """
        try:
            redis_key = self._make_key(id)
            ttl = await self.redis.ttl(redis_key)
            # ttl возвращает:
            # - положительное число - оставшееся время в секундах
            # - -1 если ключ существует без TTL
            # - -2 если ключ не существует
            if ttl == -2:
                return None
            return ttl
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.error(f"Redis connection error while getting TTL for key {id}: {e}")
            return None
        except RedisError as e:
            logger.error(f"Redis error while getting TTL for key {id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while getting TTL: {e}", exc_info=True)
            return None

    async def set_ttl(self, id: Union[UUID, str], ttl: int) -> bool:
        """Устанавливает время жизни для ключа.

        Args:
            id: Ключ
            ttl: Время жизни в секундах

        Returns:
            True если успешно, иначе False
        """
        try:
            redis_key = self._make_key(id)
            # expire возвращает True если TTL был установлен, False если ключ не существует
            result = await self.redis.expire(redis_key, ttl)
            return bool(result)
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.error(f"Redis connection error while setting TTL for key {id}: {e}")
            return False
        except RedisError as e:
            logger.error(f"Redis error while setting TTL for key {id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while setting TTL: {e}", exc_info=True)
            return False
