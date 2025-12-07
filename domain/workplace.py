from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass, field

from .worker import Worker
from .equipment import Equipment
from .base_serializabel import RedisSerializable


@dataclass
class Workplace(RedisSerializable):
    workplace_name: str
    required_speciality: str
    required_qualification: int

    worker: Optional[Worker] = field(default=None)
    equipment: Optional[Equipment] = field(default=None)
    required_stages: List[str] = field(default_factory=list)
    workplace_id: Optional[UUID] = field(default=None)

    def set_worker(self, worker: Worker) -> None:
        self.worker = worker

    def set_equipmnet(self, equipment: Equipment) -> None:
        self.equipment = equipment
