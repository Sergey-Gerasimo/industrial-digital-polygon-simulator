from typing import Any, Dict, Type, TypeVar, Optional
from dataclasses import dataclass, fields, asdict, is_dataclass
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import json


T = TypeVar("T", bound="RedisSerializable")


class RedisSerializable:
    def _serialize_value(self, value: Any) -> Any:
        """Рекурсивная сериализация значения для JSON"""
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, UUID):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, bytes):
            return value.hex()
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple, set)):
            return [self._serialize_value(item) for item in value]
        elif hasattr(value, "to_redis_dict"):
            # Рекурсивная сериализация вложенных объектов
            return value.to_redis_dict()
        elif is_dataclass(value):
            # Автоматическая сериализация вложенных датаклассов
            return {
                f.name: self._serialize_value(getattr(value, f.name))
                for f in fields(value)
            }
        else:
            return str(value)

    def to_redis_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        if not is_dataclass(self):
            raise TypeError(f"{self.__class__.__name__} is not a dataclass")

        result = {}
        for field in fields(self):
            value = getattr(self, field.name)

            if exclude_none and value is None:
                continue

            result[field.name] = self._serialize_value(value)

        result["_type"] = self.__class__.__name__

        return result

    def to_redis_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(
            self.to_redis_dict(exclude_none=True),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )
