"""Доменные сущности для отчетности и метрик (не являются частью производственного плана)."""

from dataclasses import dataclass, field
from typing import List

from .base_serializabel import RedisSerializable


@dataclass
class UnplannedRepair(RedisSerializable):
    """Внеплановый ремонт."""

    @dataclass
    class RepairRecord(RedisSerializable):
        """Запись ремонта."""

        month: str = ""
        repair_cost: int = 0
        equipment_id: str = ""
        reason: str = ""

    repairs: List[RepairRecord] = field(default_factory=list)
    total_repair_cost: int = 0


@dataclass
class RequiredMaterial(RedisSerializable):
    """Требуемый материал. Соответствует proto message RequiredMaterial."""

    material_id: str = ""  # string в proto
    name: str = ""  # string в proto
    has_contracted_supplier: bool = False  # bool в proto
    required_quantity: int = 0  # uint32 в proto
    current_stock: int = 0  # uint32 в proto
