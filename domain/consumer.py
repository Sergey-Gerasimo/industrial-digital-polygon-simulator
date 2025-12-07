from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID

from .base_serializabel import RedisSerializable


class ConsumerType(Enum):
    GOVERMANT: str = "Государсвенный"
    NOT_GOVERMANT: str = "Частный"


@dataclass
class Consumer(RedisSerializable):
    name: str
    type: ConsumerType

    consumer_id: Optional[UUID] = field(default=None)
