from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
from uuid import UUID

from .base_serializabel import RedisSerializable


class Qualification(int, Enum):
    I = 1
    II = 2
    III = 3
    IV = 4
    V = 5
    VI = 6
    VII = 7
    VIII = 8
    IX = 9


class Specialization(str, Enum):
    NONE = "none"


@dataclass
class Worker(RedisSerializable):
    name: str
    qualification: Qualification
    specialization: str  # надо бы изменить потом на список специализаций и добавить enum или запись в БД о видах специализации
    salary: int

    worker_id: Optional[UUID] = field(default=None)
