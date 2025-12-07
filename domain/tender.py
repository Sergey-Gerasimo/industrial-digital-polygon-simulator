from typing import Optional
from uuid import UUID
from dataclasses import dataclass, field

from .consumer import Consumer
from .base_serializabel import RedisSerializable


@dataclass
class Tender(RedisSerializable):
    consumer: Consumer
    cost: int
    quantity_of_products: int
    name: str
    tender_id: Optional[UUID] = field(default=None)
