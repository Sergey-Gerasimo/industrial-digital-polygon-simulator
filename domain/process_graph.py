from typing import List, Union, Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from .workplace import Workplace
from .base_serializabel import RedisSerializable

if TYPE_CHECKING:
    from .worker import Worker
    from .equipment import Equipment


@dataclass(eq=False)
class Route(RedisSerializable):
    length: int
    from_workplace: str
    to_workplace: str
    # Дополнительные поля для расчета логистических затрат
    delivery_period: int = 1
    cost: int = 0

    def __eq__(self, other):
        """Сравнение по from_workplace и to_workplace."""
        if not isinstance(other, Route):
            return False
        return (
            self.from_workplace == other.from_workplace
            and self.to_workplace == other.to_workplace
        )

    def __hash__(self):
        """Хэширование по from_workplace и to_workplace."""
        return hash((self.from_workplace, self.to_workplace))


@dataclass
class ProcessGraph(RedisSerializable):
    """Граф процесса. Соответствует proto message ProcessGraph."""

    process_graph_id: str = ""  # string в proto, не UUID
    workplaces: List[Workplace] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)

    def add_route(self, route: Route) -> None:
        self.routes.append(route)

    def get_route(self, from_wp: str, to_wp: str) -> Union[Route, None]:
        for route in self.routes:
            if route.from_workplace == from_wp and route.to_workplace == to_wp:
                return route

    def remover_route(self, from_wp: str, to_wp: str) -> None:
        new_routes = list()

        for route in self.routes:
            if route.from_workplace == from_wp and route.to_workplace == to_wp:
                continue

            new_routes.append(route)

        self.routes = new_routes

    def add_workplace(self, workplace: Workplace) -> None:
        self.workplaces.append(workplace)

    def remove_workplace(self, workplace_id: str):
        new_workplaces = list()

        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                continue

            new_workplaces.append(workplace)

        self.workplaces = new_workplaces

    def set_worker_on_workplace(self, workplace_id: str, worker: "Worker") -> None:
        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                workplace.set_worker(worker)
                break

    def unset_worker_on_workplace(self, workplace_id: str) -> None:
        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                workplace.worker = None
                break

    def set_equipment_on_workplace(
        self, workplace_id: str, equipment: "Equipment"
    ) -> None:
        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                workplace.set_equipmnet(equipment)
                break

    def unset_equipment_on_workplace(self, workplace_id: str) -> None:
        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                workplace.equipment = None
                break

    def set_worker_on_workplace_by_worker_id(
        self, workplace_id: str, worker: "Worker"
    ) -> None:
        """Устанавливает рабочего на рабочее место (set_worker_on_workerplace)."""
        raise NotImplementedError

    def unset_worker_from_workplace_by_worker_id(self, worker_id: str) -> None:
        """Снимает рабочего с рабочего места по ID рабочего (unset_worker_on_workerplace)."""
        raise NotImplementedError

    def set_workplace_as_start_node(self, workplace_id: str) -> None:
        # Сбрасываем все start_node
        for workplace in self.workplaces:
            workplace.is_start_node = False

        # Устанавливаем указанное рабочее место как начальное
        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                workplace.is_start_node = True
                break

    def set_workplace_as_end_node(self, workplace_id: str) -> None:
        # Сбрасываем все end_node
        for workplace in self.workplaces:
            workplace.is_end_node = False

        # Устанавливаем указанное рабочее место как конечное
        for workplace in self.workplaces:
            if str(workplace.workplace_id) == workplace_id:
                workplace.is_end_node = True
                workplace.next_workplace_ids = []  # Конечное не имеет следующих
                break

    def validate(self) -> bool:
        # TODO: придумать как понять что граф нормальный
        ...

    def update(self, workplaces: List[Workplace], routes: List[Route]) -> None:
        """Обновляет граф процесса списком рабочих мест и маршрутов (update_process_graph)."""
        self.workplaces = list(set(workplaces))
        self.routes = list(set(routes))  # убираем удбликаты
