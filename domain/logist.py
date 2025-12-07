from dataclasses import dataclass, field
from enum import Enum
from .worker import Worker

from .base_serializabel import RedisSerializable


class VehicleType(str, Enum):
    NONE = "None"


@dataclass
class Logist(Worker):
    speed: int = field(default=0)
    vehicle_type: VehicleType = field(default=VehicleType.NONE)
