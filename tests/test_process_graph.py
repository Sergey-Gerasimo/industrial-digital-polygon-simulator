"""Тесты для domain/process_graph.py"""

import pytest
import json

from domain.process_graph import ProcessGraph, Route
from domain.workplace import Workplace
from domain.worker import Worker
from domain.equipment import Equipment


class TestRoute:
    """Тесты для класса Route."""

    def test_route_creation(self):
        """Тест создания маршрута."""
        route = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")

        assert route.length == 10
        assert route.from_workplace == "wp_001"
        assert route.to_workplace == "wp_002"

    def test_route_to_redis_dict(self):
        """Тест сериализации Route в словарь."""
        route = Route(length=15, from_workplace="wp_001", to_workplace="wp_003")

        result = route.to_redis_dict()

        assert isinstance(result, dict)
        assert result["length"] == 15
        assert result["from_workplace"] == "wp_001"
        assert result["to_workplace"] == "wp_003"
        assert result["_type"] == "Route"

    def test_route_to_redis_json(self):
        """Тест сериализации Route в JSON."""
        route = Route(length=20, from_workplace="wp_002", to_workplace="wp_004")

        result = route.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["length"] == 20
        assert parsed["from_workplace"] == "wp_002"
        assert parsed["to_workplace"] == "wp_004"


class TestProcessGraph:
    """Тесты для класса ProcessGraph."""

    def test_process_graph_creation_with_defaults(self):
        """Тест создания графа процесса со значениями по умолчанию."""
        graph = ProcessGraph()

        assert graph.process_graph_id == ""
        assert graph.workplaces == []
        assert graph.routes == []

    def test_process_graph_creation_with_values(self):
        """Тест создания графа процесса с заданными значениями."""
        workplace1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        route1 = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")

        graph = ProcessGraph(
            process_graph_id="graph_001",
            workplaces=[workplace1],
            routes=[route1],
        )

        assert graph.process_graph_id == "graph_001"
        assert len(graph.workplaces) == 1
        assert len(graph.routes) == 1
        assert graph.workplaces[0].workplace_id == "wp_001"
        assert graph.routes[0].from_workplace == "wp_001"

    def test_add_route(self):
        """Тест добавления маршрута."""
        graph = ProcessGraph()
        route = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")

        graph.add_route(route)

        assert len(graph.routes) == 1
        assert graph.routes[0] == route
        assert graph.routes[0].length == 10

    def test_add_multiple_routes(self):
        """Тест добавления нескольких маршрутов."""
        graph = ProcessGraph()
        route1 = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        route2 = Route(length=15, from_workplace="wp_002", to_workplace="wp_003")
        route3 = Route(length=20, from_workplace="wp_001", to_workplace="wp_003")

        graph.add_route(route1)
        graph.add_route(route2)
        graph.add_route(route3)

        assert len(graph.routes) == 3
        assert graph.routes[0] == route1
        assert graph.routes[1] == route2
        assert graph.routes[2] == route3

    def test_get_route(self):
        """Тест получения маршрута."""
        graph = ProcessGraph()
        route = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        graph.add_route(route)

        found_route = graph.get_route("wp_001", "wp_002")

        assert found_route is not None
        assert found_route == route
        assert found_route.length == 10

    def test_get_route_not_found(self):
        """Тест получения несуществующего маршрута."""
        graph = ProcessGraph()

        found_route = graph.get_route("wp_001", "wp_002")

        assert found_route is None

    def test_get_route_multiple_routes(self):
        """Тест получения маршрута из нескольких."""
        graph = ProcessGraph()
        route1 = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        route2 = Route(length=15, from_workplace="wp_002", to_workplace="wp_003")
        graph.add_route(route1)
        graph.add_route(route2)

        found_route = graph.get_route("wp_002", "wp_003")

        assert found_route is not None
        assert found_route == route2
        assert found_route.length == 15

    def test_remover_route(self):
        """Тест удаления маршрута (с опечаткой в названии метода)."""
        graph = ProcessGraph()
        route1 = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        route2 = Route(length=15, from_workplace="wp_002", to_workplace="wp_003")
        graph.add_route(route1)
        graph.add_route(route2)

        graph.remover_route("wp_001", "wp_002")

        assert len(graph.routes) == 1
        assert graph.routes[0] == route2

    def test_remover_route_not_found(self):
        """Тест удаления несуществующего маршрута."""
        graph = ProcessGraph()
        route = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        graph.add_route(route)

        graph.remover_route("wp_999", "wp_888")

        assert len(graph.routes) == 1  # Ничего не удалено

    def test_add_workplace(self):
        """Тест добавления рабочего места."""
        graph = ProcessGraph()
        workplace = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")

        graph.add_workplace(workplace)

        assert len(graph.workplaces) == 1
        assert graph.workplaces[0] == workplace
        assert graph.workplaces[0].workplace_id == "wp_001"

    def test_add_multiple_workplaces(self):
        """Тест добавления нескольких рабочих мест."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Рабочее место 2")
        wp3 = Workplace(workplace_id="wp_003", workplace_name="Рабочее место 3")

        graph.add_workplace(wp1)
        graph.add_workplace(wp2)
        graph.add_workplace(wp3)

        assert len(graph.workplaces) == 3
        assert graph.workplaces[0] == wp1
        assert graph.workplaces[1] == wp2
        assert graph.workplaces[2] == wp3

    def test_remove_workplace(self):
        """Тест удаления рабочего места."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Рабочее место 2")
        graph.add_workplace(wp1)
        graph.add_workplace(wp2)

        graph.remove_workplace("wp_001")

        assert len(graph.workplaces) == 1
        assert graph.workplaces[0] == wp2

    def test_remove_workplace_not_found(self):
        """Тест удаления несуществующего рабочего места."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        graph.add_workplace(wp1)

        graph.remove_workplace("wp_999")

        assert len(graph.workplaces) == 1  # Ничего не удалено

    def test_set_worker_on_workplace(self):
        """Тест установки рабочего на рабочее место."""
        graph = ProcessGraph()
        workplace = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        worker = Worker(worker_id="worker_001", name="Рабочий")
        graph.add_workplace(workplace)

        graph.set_worker_on_workplace("wp_001", worker)

        assert workplace.worker == worker
        assert workplace.worker.worker_id == "worker_001"

    def test_set_worker_on_workplace_not_found(self):
        """Тест установки рабочего на несуществующее рабочее место."""
        graph = ProcessGraph()
        worker = Worker(worker_id="worker_001", name="Рабочий")

        # Не должно быть ошибки, просто ничего не происходит
        graph.set_worker_on_workplace("wp_999", worker)

    def test_unset_worker_on_workplace(self):
        """Тест снятия рабочего с рабочего места."""
        graph = ProcessGraph()
        workplace = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        worker = Worker(worker_id="worker_001", name="Рабочий")
        workplace.set_worker(worker)
        graph.add_workplace(workplace)

        graph.unset_worker_on_workplace("wp_001")

        assert workplace.worker is None

    def test_unset_worker_on_workplace_not_found(self):
        """Тест снятия рабочего с несуществующего рабочего места."""
        graph = ProcessGraph()

        # Не должно быть ошибки
        graph.unset_worker_on_workplace("wp_999")

    def test_set_equipment_on_workplace(self):
        """Тест установки оборудования на рабочее место."""
        graph = ProcessGraph()
        workplace = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        equipment = Equipment(equipment_id="equip_001", name="Оборудование")
        graph.add_workplace(workplace)

        graph.set_equipment_on_workplace("wp_001", equipment)

        assert workplace.equipment == equipment
        assert workplace.equipment.equipment_id == "equip_001"

    def test_set_equipment_on_workplace_not_found(self):
        """Тест установки оборудования на несуществующее рабочее место."""
        graph = ProcessGraph()
        equipment = Equipment(equipment_id="equip_001", name="Оборудование")

        # Не должно быть ошибки
        graph.set_equipment_on_workplace("wp_999", equipment)

    def test_unset_equipment_on_workplace(self):
        """Тест снятия оборудования с рабочего места."""
        graph = ProcessGraph()
        workplace = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        equipment = Equipment(equipment_id="equip_001", name="Оборудование")
        workplace.set_equipmnet(equipment)
        graph.add_workplace(workplace)

        graph.unset_equipment_on_workplace("wp_001")

        assert workplace.equipment is None

    def test_unset_equipment_on_workplace_not_found(self):
        """Тест снятия оборудования с несуществующего рабочего места."""
        graph = ProcessGraph()

        # Не должно быть ошибки
        graph.unset_equipment_on_workplace("wp_999")

    def test_set_worker_on_workplace_by_worker_id_not_implemented(self):
        """Тест что метод set_worker_on_workplace_by_worker_id не реализован."""
        graph = ProcessGraph()
        worker = Worker(worker_id="worker_001", name="Рабочий")

        with pytest.raises(NotImplementedError):
            graph.set_worker_on_workplace_by_worker_id("wp_001", worker)

    def test_unset_worker_from_workplace_by_worker_id_not_implemented(self):
        """Тест что метод unset_worker_from_workplace_by_worker_id не реализован."""
        graph = ProcessGraph()

        with pytest.raises(NotImplementedError):
            graph.unset_worker_from_workplace_by_worker_id("worker_001")

    def test_set_workplace_as_start_node(self):
        """Тест установки рабочего места как начального узла."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Рабочее место 2")
        wp1.is_start_node = True  # Устанавливаем одно как начальное
        graph.add_workplace(wp1)
        graph.add_workplace(wp2)

        graph.set_workplace_as_start_node("wp_002")

        # wp_001 больше не начальное
        assert wp1.is_start_node is False
        # wp_002 теперь начальное
        assert wp2.is_start_node is True

    def test_set_workplace_as_start_node_not_found(self):
        """Тест установки несуществующего рабочего места как начального."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        wp1.is_start_node = True
        graph.add_workplace(wp1)

        graph.set_workplace_as_start_node("wp_999")

        # Все рабочие места должны стать не начальными
        assert wp1.is_start_node is False

    def test_set_workplace_as_end_node(self):
        """Тест установки рабочего места как конечного узла."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Рабочее место 2")
        wp1.is_end_node = True  # Устанавливаем одно как конечное
        wp2.next_workplace_ids = ["wp_003"]  # Есть следующие узлы
        graph.add_workplace(wp1)
        graph.add_workplace(wp2)

        graph.set_workplace_as_end_node("wp_002")

        # wp_001 больше не конечное
        assert wp1.is_end_node is False
        # wp_002 теперь конечное
        assert wp2.is_end_node is True
        # Следующие узлы очищены
        assert wp2.next_workplace_ids == []

    def test_set_workplace_as_end_node_not_found(self):
        """Тест установки несуществующего рабочего места как конечного."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        wp1.is_end_node = True
        graph.add_workplace(wp1)

        graph.set_workplace_as_end_node("wp_999")

        # Все рабочие места должны стать не конечными
        assert wp1.is_end_node is False

    def test_update_not_implemented(self):
        """Тест метода update - обновление графа процесса."""
        graph = ProcessGraph()
        workplaces = [
            Workplace(workplace_id="wp_001"),
            Workplace(workplace_id="wp_002"),
        ]
        routes = [
            Route(length=10, from_workplace="wp_001", to_workplace="wp_002"),
            Route(length=15, from_workplace="wp_002", to_workplace="wp_003"),
        ]

        graph.update(workplaces, routes)

        assert len(graph.workplaces) == 2
        assert len(graph.routes) == 2
        # Проверяем наличие элементов через множества (порядок может отличаться после set)
        assert set(graph.workplaces) == set(workplaces)
        assert set(graph.routes) == set(routes)

    def test_process_graph_to_redis_dict(self):
        """Тест сериализации ProcessGraph в словарь."""
        graph = ProcessGraph(process_graph_id="graph_001")
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        route1 = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        graph.add_workplace(wp1)
        graph.add_route(route1)

        result = graph.to_redis_dict()

        assert isinstance(result, dict)
        assert result["process_graph_id"] == "graph_001"
        assert isinstance(result["workplaces"], list)
        assert len(result["workplaces"]) == 1
        assert isinstance(result["routes"], list)
        assert len(result["routes"]) == 1
        assert result["_type"] == "ProcessGraph"

    def test_process_graph_to_redis_json(self):
        """Тест сериализации ProcessGraph в JSON."""
        graph = ProcessGraph(process_graph_id="graph_002")
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место")
        graph.add_workplace(wp1)

        result = graph.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["process_graph_id"] == "graph_002"
        assert isinstance(parsed["workplaces"], list)
        assert len(parsed["workplaces"]) == 1

    def test_complex_scenario(self):
        """Тест комплексного сценария использования."""
        graph = ProcessGraph(process_graph_id="graph_complex")

        # Создаем рабочие места
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Начало")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Середина")
        wp3 = Workplace(workplace_id="wp_003", workplace_name="Конец")

        # Добавляем рабочие места
        graph.add_workplace(wp1)
        graph.add_workplace(wp2)
        graph.add_workplace(wp3)

        # Создаем маршруты
        route1 = Route(length=10, from_workplace="wp_001", to_workplace="wp_002")
        route2 = Route(length=15, from_workplace="wp_002", to_workplace="wp_003")
        graph.add_route(route1)
        graph.add_route(route2)

        # Устанавливаем начальное и конечное узлы
        graph.set_workplace_as_start_node("wp_001")
        graph.set_workplace_as_end_node("wp_003")

        # Устанавливаем рабочего и оборудование
        worker = Worker(worker_id="worker_001", name="Рабочий")
        equipment = Equipment(equipment_id="equip_001", name="Оборудование")
        graph.set_worker_on_workplace("wp_002", worker)
        graph.set_equipment_on_workplace("wp_002", equipment)

        # Проверяем результаты
        assert len(graph.workplaces) == 3
        assert len(graph.routes) == 2
        assert wp1.is_start_node is True
        assert wp2.is_start_node is False
        assert wp3.is_end_node is True
        assert wp2.worker == worker
        assert wp2.equipment == equipment

        # Удаляем маршрут
        graph.remover_route("wp_001", "wp_002")
        assert len(graph.routes) == 1

        # Снимаем рабочего
        graph.unset_worker_on_workplace("wp_002")
        assert wp2.worker is None

        # Удаляем рабочее место
        graph.remove_workplace("wp_002")
        assert len(graph.workplaces) == 2

    def test_multiple_start_nodes_reset(self):
        """Тест что при установке нового начального узла старые сбрасываются."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Рабочее место 2")
        wp3 = Workplace(workplace_id="wp_003", workplace_name="Рабочее место 3")
        graph.add_workplace(wp1)
        graph.add_workplace(wp2)
        graph.add_workplace(wp3)

        # Устанавливаем первое как начальное
        graph.set_workplace_as_start_node("wp_001")
        assert wp1.is_start_node is True
        assert wp2.is_start_node is False
        assert wp3.is_start_node is False

        # Устанавливаем второе как начальное
        graph.set_workplace_as_start_node("wp_002")
        assert wp1.is_start_node is False  # Сброшено
        assert wp2.is_start_node is True
        assert wp3.is_start_node is False

        # Устанавливаем третье как начальное
        graph.set_workplace_as_start_node("wp_003")
        assert wp1.is_start_node is False
        assert wp2.is_start_node is False  # Сброшено
        assert wp3.is_start_node is True

    def test_multiple_end_nodes_reset(self):
        """Тест что при установке нового конечного узла старые сбрасываются."""
        graph = ProcessGraph()
        wp1 = Workplace(workplace_id="wp_001", workplace_name="Рабочее место 1")
        wp2 = Workplace(workplace_id="wp_002", workplace_name="Рабочее место 2")
        wp3 = Workplace(workplace_id="wp_003", workplace_name="Рабочее место 3")
        graph.add_workplace(wp1)
        graph.add_workplace(wp2)
        graph.add_workplace(wp3)

        # Устанавливаем первое как конечное
        graph.set_workplace_as_end_node("wp_001")
        assert wp1.is_end_node is True
        assert wp2.is_end_node is False
        assert wp3.is_end_node is False

        # Устанавливаем второе как конечное
        graph.set_workplace_as_end_node("wp_002")
        assert wp1.is_end_node is False  # Сброшено
        assert wp2.is_end_node is True
        assert wp3.is_end_node is False

        # Устанавливаем третье как конечное
        graph.set_workplace_as_end_node("wp_003")
        assert wp1.is_end_node is False
        assert wp2.is_end_node is False  # Сброшено
        assert wp3.is_end_node is True
