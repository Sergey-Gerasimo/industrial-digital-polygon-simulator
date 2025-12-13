from dataclasses import dataclass, field
from enum import Enum
from .worker import Worker

from .base_serializabel import RedisSerializable


class VehicleType(str, Enum):
    NONE = "None"
    VAN = "Грузовой фургон"
    TRUCK = "Фура"
    ELECTRIC = "Электрокар"


@dataclass
class Logist(RedisSerializable):
    """Логист. Соответствует proto message Logist."""

    worker_id: str = ""  # string в proto
    name: str = ""
    qualification: int = 0  # uint32 в proto
    specialty: str = ""  # string в proto
    salary: int = 0  # uint32 в proto
    speed: int = 0  # uint32 в proto
    vehicle_type: str = (
        ""  # string в proto (для преобразования используем VehicleType enum)
    )
