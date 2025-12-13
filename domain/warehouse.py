from typing import Dict, Optional
from uuid import UUID
from dataclasses import field, dataclass

from .worker import Worker
from .base_serializabel import RedisSerializable


@dataclass
class Warehouse(RedisSerializable):
    """Склад. Соответствует proto message Warehouse."""

    warehouse_id: str = ""  # string в proto
    inventory_worker: Optional[Worker] = field(default=None)
    size: int = 0  # uint32 в proto
    materials: Dict[str, int] = field(
        default_factory=dict
    )  # map<string, uint32> в proto

    @property
    def is_full(self) -> bool:
        """Проверяет, заполнен ли склад."""
        return self.loading >= self.size

    @property
    def loading(self) -> int:
        """Получает загрузку склада."""
        return sum(self.materials.values())

    def set_inventory_worker(self, worker: Worker) -> None:
        """Устанавливает кладовщика на склад (set_warehouse_inventory_worker)."""
        self.inventory_worker = worker

    def increase_size(self, size: int) -> None:
        """Увеличивает размер склада (increase_warehouse_size)."""
        self.size += size

    def decrease_size(self, size: int) -> None:
        """Уменьшает размер склада (decrease_warehouse_size)."""
        self.size = max(0, self.size - size)

    def add_material(self, material: str, quantity: int) -> None:
        """Добавляет материал на склад (add_warehouse_material)."""

        if quantity < 0:
            raise ValueError(
                f"Количество материала {material} не может быть отрицательным"
            )

        # Проверяем общую загрузку склада после добавления материала ПЕРЕД изменением словаря
        current_loading = self.loading  # текущая общая загрузка
        # Вычисляем новую общую загрузку: текущая загрузка + добавляемое количество
        new_loading = current_loading + quantity

        if new_loading > self.size:
            raise ValueError(f"На складе нет места")

        # Только после успешной проверки добавляем материал в словарь
        if material not in self.materials:
            self.materials[material] = 0

        self.materials[material] += quantity

    def remove_material(self, material: str, quantity: int) -> None:
        """Удаляет материал со склада (remove_warehouse_material)."""

        if material not in self.materials:
            raise ValueError(f"Материал {material} не найден на складе")

        if self.materials[material] < quantity:
            raise ValueError(f"На складе нет {quantity} материала {material}")

        self.materials[material] -= quantity
