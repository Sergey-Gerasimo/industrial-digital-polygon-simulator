from typing import Optional
from uuid import UUID

from dataclasses import dataclass, field
from .base_serializabel import RedisSerializable


@dataclass(frozen=False)
class Equipment(RedisSerializable):
    """Оборудование. Соответствует proto message Equipment."""

    equipment_id: str = ""  # string в proto
    name: str = ""
    equipment_type: str = ""  # string в proto
    reliability: float = 0.0  # double в proto
    maintenance_period: int = 0  # uint32 в proto - обязательное поле
    maintenance_cost: int = 0  # uint32 в proto, стоимость обслуживания
    cost: int = 0  # uint32 в proto
    repair_cost: int = 0  # uint32 в proto
    repair_time: int = 0  # uint32 в proto

    def set_maintenance_period(self, period: int) -> None:
        self.maintenance_period = period

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Equipment):
            return NotImplemented
        return self.equipment_id == other.equipment_id

    def __hash__(self) -> int:
        return hash(self.equipment_id)


if __name__ == "__main__":
    equipment = Equipment(
        name="",
        reliability=0.9,
        maintenance_cost=5000,
        cost=0,
        repair_cost=4000,
        repair_time=8,
    )
