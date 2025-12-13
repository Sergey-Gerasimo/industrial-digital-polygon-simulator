from typing import Optional, List, Dict, TYPE_CHECKING
from dataclasses import dataclass, field
from uuid import UUID
from enum import Enum

from .base_serializabel import RedisSerializable

if TYPE_CHECKING:
    from .worker import Worker
    from .equipment import Equipment
    from .process_graph import Route


@dataclass
class ProductionPlanRow(RedisSerializable):
    """Строка производственного плана (соответствует одному тендеру)."""

    tender_id: str = (
        ""  # ID тендера (обязательная привязка, в тендере есть привязка к потребителю)
    )
    product_name: str = ""  # Название продукта

    # Основные поля из продуктового плана
    priority: int = 0  # Приоритет №
    plan_date: str = ""  # План дата (DD.MM)
    dse: str = ""  # ДСЕ (Design-Assembly Unit)
    short_set: str = ""  # Набор (коротк.)
    dse_name: str = ""  # Наименование ДСЕ
    planned_quantity: int = 0  # Кол-во план. (с ТО/без ТО)
    actual_quantity: int = 0  # Кол-во факт.
    remaining_to_produce: int = 0  # Осталось изготовить
    provision_status: str = ""  # Обеспеченность ("Обеспечено" / "Не обеспечено")
    note: str = ""  # Примечание
    planned_completion_date: str = ""  # Плановая дата исполнения (DD.MM.YYYY)
    cost_breakdown: str = ""  # Разрез себестоимости
    order_number: str = ""  # Номер заказа

    def __eq__(self, other: object) -> bool:
        """Сравнение по tender_id."""
        if not isinstance(other, ProductionPlanRow):
            return NotImplemented
        return self.tender_id == other.tender_id

    def __hash__(self) -> int:
        """Хеш по tender_id для использования в множествах и словарях."""
        return hash(self.tender_id)


@dataclass
class ProductionSchedule(RedisSerializable):
    """Объемно-календарный план (таблица строк по тендерам)."""

    rows: list[ProductionPlanRow] = field(default_factory=list)

    def update_row(self, row: ProductionPlanRow) -> None:
        """Обновляет строку в производственном плане.
        Если строка с таким tender_id уже существует, она перезаписывается.
        Для каждого тендера строго одна строка.
        """
        for i, existing_row in enumerate(self.rows):
            if existing_row.tender_id == row.tender_id:
                self.rows[i] = row
                return
        raise ValueError(
            f"Строка с tender_id {row.tender_id} не найдена в производственном плане"
        )

    def set_row(self, row: ProductionPlanRow) -> None:
        """Добавляет строку в производственный план.
        Если строка с таким tender_id уже существует, она перезаписывается.
        Для каждого тендера строго одна строка.
        """
        # Ищем существующую строку с таким tender_id
        for i, existing_row in enumerate(self.rows):
            if existing_row.tender_id == row.tender_id:
                # Перезаписываем существующую строку
                self.rows[i] = row
                return
        # Если строка не найдена, добавляем новую
        self.rows.append(row)
