"""Доменная сущность сертификации."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from .base_serializabel import RedisSerializable


@dataclass
class Certification(RedisSerializable):
    """Сертификация. Соответствует proto message Certification."""

    certificate_type: str = ""  # string в proto
    is_obtained: bool = field(
        default=False
    )  # bool в proto эту штуку задает пользователь
    implementation_cost: int = field(default=0)  # uint64 в proto
    implementation_time_days: int = field(default=0)  # uint32 в proto

    def set_is_obtained(self, is_obtained: bool) -> None:
        """Устанавливает статус сертификации."""
        self.is_obtained = is_obtained

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Certification):
            return NotImplemented
        return self.certificate_type == other.certificate_type

    def __hash__(self) -> int:
        return hash(self.certificate_type)
