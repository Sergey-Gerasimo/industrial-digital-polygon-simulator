from typing import Optional
from uuid import UUID
from dataclasses import field, dataclass

from .base_serializabel import RedisSerializable


@dataclass
class Supplier(RedisSerializable):
    """Поставщик. Соответствует proto message Supplier."""

    supplier_id: str = ""  # string в proto
    name: str = ""
    product_name: str = ""
    material_type: str = ""  # string в proto
    delivery_period: int = 0  # uint32 в proto
    special_delivery_period: int = 0  # uint32 в proto
    reliability: float = 0.0  # double в proto
    product_quality: float = 0.0  # double в proto
    cost: int = 0  # uint32 в proto
    special_delivery_cost: int = 0  # uint32 в proto

    @property
    def is_special_delivery(self) -> bool:
        """Проверяет, является ли поставка специальной."""
        return self.special_delivery_period >= self.delivery_period

    # Поля только для доменной модели (не хранятся в БД и не в proto)
    quality_inspection_enabled: bool = False
    delivery_period_days: int = 7  # период поставок в днях

    def set_quality_inspection(self, inspection_enabled: bool) -> None:
        """Устанавливает контроль качества материалов от поставщика.

        Args:
            inspection_enabled: включить/выключить контроль качества
        """
        self.quality_inspection_enabled = inspection_enabled

    def set_delivery_period(self, delivery_period_days: int) -> None:
        """Устанавливает период поставок в днях."""

        if delivery_period_days < 0:
            raise ValueError("Период поставок не может быть отрицательным")

        self.delivery_period_days = delivery_period_days

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Supplier):
            return NotImplemented
        return self.supplier_id == other.supplier_id

    def __hash__(self) -> int:
        return hash(self.supplier_id)
