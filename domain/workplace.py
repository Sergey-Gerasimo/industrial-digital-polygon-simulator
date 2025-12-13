from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass, field

from .worker import Worker
from .equipment import Equipment
from .base_serializabel import RedisSerializable


@dataclass(eq=False)
class Workplace(RedisSerializable):
    """Рабочее место. Соответствует proto message Workplace."""

    workplace_id: str = ""  # string в proto
    workplace_name: str = ""
    required_speciality: str = ""  # string в proto
    required_qualification: int = 0  # uint32 в proto
    required_equipment: str = ""  # string в proto
    worker: Optional[Worker] = field(default=None)
    equipment: Optional[Equipment] = field(default=None)
    required_stages: List[str] = field(default_factory=list)
    is_start_node: bool = field(default=False)
    is_end_node: bool = field(default=False)
    next_workplace_ids: List[str] = field(default_factory=list)

    def __eq__(self, other):
        """Сравнение по workplace_id."""
        if not isinstance(other, Workplace):
            return False
        return self.workplace_id == other.workplace_id

    def __hash__(self):
        """Хэширование по workplace_id."""
        return hash(self.workplace_id)

    def set_worker(self, worker: Worker) -> None:
        if not isinstance(worker, Worker):
            raise ValueError("Рабочий должен быть объектом класса Worker")

        self.worker = worker

    def set_equipmnet(self, equipment: Equipment) -> None:
        if not isinstance(equipment, Equipment):
            raise ValueError("Оборудование должно быть объектом класса Equipment")

        self.equipment = equipment
