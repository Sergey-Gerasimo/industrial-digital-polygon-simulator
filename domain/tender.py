from enum import Enum
from typing import Optional
from uuid import UUID
from dataclasses import dataclass, field

from .consumer import Consumer
from .base_serializabel import RedisSerializable


class PaymentForm(str, Enum):
    CASH = "cash"
    CREDIT = "credit"
    TRANSFER = "transfer"
    FULL_ADVANCE = "100% аванс"
    PARTIAL_ADVANCE = "50% аванс, 50% по факту"
    ON_DELIVERY = "100% по факту"


@dataclass
class Tender(RedisSerializable):
    """Тендер. Соответствует proto message Tender."""

    tender_id: str = ""  # string в proto
    consumer: Consumer = field(default_factory=lambda: Consumer(name="", type=""))
    cost: int = 0  # uint32 в proto
    quantity_of_products: int = 0  # uint32 в proto
    penalty_per_day: int = field(default=0)  # uint32 в proto
    warranty_years: int = field(default=0)  # uint32 в proto
    payment_form: str = (
        ""  # string в proto (для преобразования используем PaymentForm enum)
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tender):
            return NotImplemented
        return self.tender_id == other.tender_id

    def __hash__(self) -> int:
        return hash(self.tender_id)
