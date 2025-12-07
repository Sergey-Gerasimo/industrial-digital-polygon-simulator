from typing import Dict, Optional
from uuid import UUID
from dataclasses import field, dataclass

from .worker import Worker
from .base_serializabel import RedisSerializable


class Warehouse(RedisSerializable):
    size: int
    loading: int
    materials: Dict[str, int]

    warehouse_id: Optional[UUID] = field(default=None)
    inverntory_worker: Optional[Worker] = field(default=None)

    def set_inventory_worker(self, worker: Worker) -> None:
        self.inverntory_worker = worker
