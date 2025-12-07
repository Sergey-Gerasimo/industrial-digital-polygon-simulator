from typing import Optional
from uuid import UUID
from dataclasses import field, dataclass

from .base_serializabel import RedisSerializable


@dataclass
class Supplier(RedisSerializable):
    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int

    supplier_id: Optional[UUID] = field(default=None)
