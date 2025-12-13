from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID

from .base_serializabel import RedisSerializable


class ConsumerType(Enum):
    """Тип потребителя (для внутреннего использования)."""

    GOVERMANT: str = "Государсвенный"
    NOT_GOVERMANT: str = "Частный"


@dataclass
class Consumer(RedisSerializable):
    """Потребитель. Соответствует proto message Consumer."""

    name: str
    type: str  # string в proto, не enum
    consumer_id: Optional[UUID] = field(default=None)
