from contextlib import redirect_stderr
from typing import List, Union
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from .workplace import Workplace
from .base_serializabel import RedisSerializable


class Route(RedisSerializable):
    length: int
    from_workplace: str
    to_workplace: str


class ProcessGraph(RedisSerializable):
    process_graph_id: [UUID] = field(default_factory=uuid4)
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

    def remove_workplace(self, wp_name: str):
        new_workplaces = list()

        for workplace in self.workplaces:
            if workplace.workplace_name == wp_name:
                continue

            new_workplaces.append(workplace)

        self.workplaces = new_workplaces

    def validate(self) -> bool:
        # TODO: придумать как понять что граф нормальный
        ...
