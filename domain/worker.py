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
    ASSEMBLER = "Слесарь-сборщик"
    ENGINEER_TECHNOLOGIST = "Инженер-технолог"
    LOGIST = "Логист"
    QUALITY_CONTROLLER = "Контролер качества"
    WAREHOUSE_KEEPER = "Кладовщик"


@dataclass
class Worker(RedisSerializable):
    """Рабочий. Соответствует proto message Worker."""

    worker_id: str = ""  # string в proto
    name: str = ""
    qualification: int = 0  # uint32 в proto - числовое значение
    specialty: str = ""  # string в proto, не enum
    salary: int = 0  # uint32 в proto

    def set_qualification(self, qualification: int) -> None:
        """Устанавливает квалификацию работника."""
        if qualification < 1 or qualification > 9:
            raise ValueError("Квалификация работника должна быть от 1 до 9")

        self.qualification = qualification

    def __eq__(self, other: object) -> bool:
        """Сравнение по worker_id."""
        if not isinstance(other, Worker):
            return NotImplemented
        return self.worker_id == other.worker_id

    def __hash__(self) -> int:
        """Хеш по worker_id для использования в множествах и словарях."""
        return hash(self.worker_id)
