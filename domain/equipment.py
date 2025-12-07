from typing import Optional
from uuid import UUID

from dataclasses import dataclass, field
from .base_serializabel import RedisSerializable


@dataclass(frozen=False)
class Equipment(RedisSerializable):
    name: str
    reliability: float
    maintenance_cost: int  # стоимость обслуживания
    cost: int
    repair_cost: int
    repair_time: int

    equipment_id: Optional[UUID] = field(default=None, compare=False)  # получаем из БД
    maintenance_period: Optional[int] = field(
        default=None
    )  # период обслуживания выбирает пользователь

    def set_maintenance_period(self, period: int) -> None:
        self.maintenance_period = period


if __name__ == "__main__":
    equipment = Equipment(
        name="",
        reliability=0.9,
        maintenance_cost=5000,
        cost=0,
        repair_cost=4000,
        repair_time=8,
    )
