"""Доменная сущность LEAN улучшения."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from .base_serializabel import RedisSerializable


@dataclass
class LeanImprovement(RedisSerializable):
    """LEAN улучшение. Соответствует proto message LeanImprovement."""

    improvement_id: str = ""  # string в proto
    name: str = ""
    is_implemented: bool = field(default=False)  # bool в proto
    implementation_cost: int = field(default=0)  # uint64 в proto
    efficiency_gain: float = field(default=0.0)  # double в proto

    def set_is_implemented(self, is_implemented: bool) -> None:
        """Устанавливает статус реализации улучшения."""
        self.is_implemented = is_implemented

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для Redis."""
        return {
            "improvement_id": str(self.improvement_id) if self.improvement_id else None,
            "name": self.name,
            "is_implemented": self.is_implemented,
            "implementation_cost": self.implementation_cost,
            "efficiency_gain": self.efficiency_gain,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LeanImprovement":
        """Создает объект из словаря Redis."""
        improvement_id = data.get("improvement_id")
        name = data.get("name")
        is_implemented = data.get("is_implemented")
        implementation_cost = data.get("implementation_cost")
        efficiency_gain = data.get("efficiency_gain")
        return cls(
            improvement_id="" if improvement_id is None else improvement_id,
            name="" if name is None else name,
            is_implemented=is_implemented if is_implemented is not None else False,
            implementation_cost=(
                implementation_cost if implementation_cost is not None else 0
            ),
            efficiency_gain=efficiency_gain if efficiency_gain is not None else 0.0,
        )
