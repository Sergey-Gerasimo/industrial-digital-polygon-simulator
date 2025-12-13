"""Тесты для domain/simulaton.py - класс Simulation"""

import pytest
from unittest.mock import AsyncMock, patch

from domain.simulaton import (
    Simulation,
    SimulationParameters,
    SimulationResults,
    SaleStrategest,
)
from domain.warehouse import Warehouse
from domain.supplier import Supplier
from domain.tender import Tender
from domain.process_graph import ProcessGraph
from domain.worker import Worker
from domain.equipment import Equipment
from domain.workplace import Workplace
from domain.lean_improvement import LeanImprovement
from domain.metrics import (
    FactoryMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
)


class TestSimulation:
    """Тесты для класса Simulation."""

    def test_creation_with_defaults(self):
        """Тест создания Simulation со значениями по умолчанию."""
        simulation = Simulation()

        assert simulation.capital == 0
        assert simulation.simulation_id == ""
        assert simulation.parameters == []
        assert simulation.results == []
        assert simulation.room_id == ""
        assert simulation.is_completed is False

    def test_creation_with_values(self):
        """Тест создания Simulation с заданными значениями."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
            is_completed=False,
        )

        assert simulation.capital == 10000000
        assert simulation.simulation_id == "test_id"
        assert len(simulation.parameters) == 1
        assert simulation.parameters[0].step == 1
        assert simulation.results == []
        assert simulation.room_id == "room_1"
        assert simulation.is_completed is False

    def test_run_simulation_creates_results(self):
        """Тест что run_simulation создает результаты."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        initial_results_count = len(simulation.results)
        simulation.run_simulation()

        # Проверяем, что результаты добавлены
        assert len(simulation.results) == initial_results_count + 1

        # Проверяем структуру результата
        result = simulation.results[0]
        assert isinstance(result, SimulationResults)
        assert result.step == 1
        assert result.profit >= 0
        assert result.cost >= 0
        assert isinstance(result.profitability, float)

    def test_run_simulation_creates_metrics(self):
        """Тест что run_simulation создает все метрики."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        result = simulation.results[0]

        # Проверяем наличие всех метрик
        assert result.factory_metrics is not None
        assert isinstance(result.factory_metrics, FactoryMetrics)

        assert result.production_metrics is not None
        assert isinstance(result.production_metrics, ProductionMetrics)

        assert result.quality_metrics is not None
        assert isinstance(result.quality_metrics, QualityMetrics)

        assert result.engineering_metrics is not None
        assert isinstance(result.engineering_metrics, EngineeringMetrics)

        assert result.commercial_metrics is not None
        assert isinstance(result.commercial_metrics, CommercialMetrics)

        assert result.procurement_metrics is not None
        assert isinstance(result.procurement_metrics, ProcurementMetrics)

    def test_run_simulation_creates_next_parameters_when_step_not_4(self):
        """Тест что run_simulation создает новые параметры если следующий step <= 4."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        initial_params_count = len(simulation.parameters)
        simulation.run_simulation()

        # Проверяем, что созданы новые параметры
        assert len(simulation.parameters) == initial_params_count + 1
        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[1].step == 2

    def test_run_simulation_not_creates_next_parameters_when_step_4(self):
        """Тест что run_simulation не создает новые параметры если следующий step > 4."""
        # Создаем симуляцию с параметрами шагов 1, 2, 3, 4 и результатами для шагов 1, 2, 3
        params1 = SimulationParameters(step=1, capital=10000000)
        params2 = SimulationParameters(step=2, capital=10000000)
        params3 = SimulationParameters(step=3, capital=10000000)
        params4 = SimulationParameters(step=4, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params1, params2, params3, params4],
            results=[],
            room_id="room_1",
        )
        # Добавляем результаты для шагов 1, 2, 3, чтобы следующий результат был для step 4
        result1 = SimulationResults(step=1, profit=0, cost=0, profitability=0.0)
        result2 = SimulationResults(step=2, profit=0, cost=0, profitability=0.0)
        result3 = SimulationResults(step=3, profit=0, cost=0, profitability=0.0)
        simulation.results = [result1, result2, result3]

        initial_params_count = len(simulation.parameters)
        simulation.run_simulation()

        # Проверяем, что новые параметры не созданы (так как следующий step был бы 5)
        assert len(simulation.parameters) == initial_params_count
        # Проверяем, что результат для step 4 был создан
        assert len(simulation.results) == 4

    def test_run_simulation_with_multiple_steps(self):
        """Тест run_simulation для нескольких шагов."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        # Запускаем симуляцию несколько раз
        # Начальное состояние: 1 параметр (step=1), 0 результатов
        simulation.run_simulation()  # После 1-го: 2 параметра (1,2), 1 результат (step=1)
        simulation.run_simulation()  # После 2-го: 3 параметра (1,2,3), 2 результата (1,2)
        simulation.run_simulation()  # После 3-го: 4 параметра (1,2,3,4), 3 результата (1,2,3)

        # Проверяем результаты
        assert len(simulation.results) == 3
        assert len(simulation.parameters) == 4  # 1, 2, 3, 4
        results_by_step = sorted(simulation.results, key=lambda r: r.step)
        assert results_by_step[0].step == 1
        assert results_by_step[1].step == 2
        assert results_by_step[2].step == 3

    def test_run_simulation_with_empty_parameters(self):
        """Тест run_simulation с пустым списком параметров."""
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[],
            results=[],
            room_id="room_1",
        )

        # Должно выбросить ValueError
        with pytest.raises(ValueError, match="нет параметров для выполнения"):
            simulation.run_simulation()

        # Результаты не должны быть созданы
        assert len(simulation.results) == 0

    def test_run_simulation_uses_latest_parameters(self):
        """Тест что run_simulation использует последние параметры (с максимальным step)."""
        params0 = SimulationParameters(step=1, capital=10000000)
        params1 = SimulationParameters(step=2, capital=20000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params0, params1],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        # Проверяем, что результат создается с step=1 (так как len(non_empty_results) = 0, next_result_step = 1)
        # хотя используются последние параметры (params1 со step=2)
        result = simulation.results[0]
        assert result.step == 1

        # Проверяем, что созданы новые параметры для следующего шага (step=3)
        assert len(simulation.parameters) == 3
        assert simulation.parameters[2].step == 3

    def test_run_simulation_with_suppliers_and_tenders(self):
        """Тест run_simulation с поставщиками и тендерами."""
        supplier = Supplier(
            supplier_id="supplier_1",
            name="Поставщик 1",
            product_quality=0.9,
            reliability=0.95,
            cost=1000,
        )
        tender = Tender(tender_id="tender_1", quantity_of_products=100)

        params = SimulationParameters(
            step=1,
            capital=10000000,
            suppliers=[supplier],
            tenders=[tender],
        )
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        result = simulation.results[0]

        # Проверяем, что метрики созданы с учетом данных
        assert result.procurement_metrics is not None
        assert len(result.procurement_metrics.supplier_performances) > 0

        assert result.commercial_metrics is not None
        assert len(result.commercial_metrics.tender_graph) > 0

    def test_validate_configuration_returns_valid_structure(self):
        """Тест что validate_configuration возвращает правильную структуру."""
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[],
            results=[],
            room_id="room_1",
        )

        validation = simulation.validate_configuration()

        # Проверяем структуру ответа
        assert isinstance(validation, dict)
        assert "is_valid" in validation
        assert "errors" in validation
        assert "warnings" in validation

        # Проверяем типы
        assert isinstance(validation["is_valid"], bool)
        assert isinstance(validation["errors"], list)
        assert isinstance(validation["warnings"], list)

    def test_validate_configuration_returns_true(self):
        """Тест что validate_configuration возвращает is_valid=True."""
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[],
            results=[],
            room_id="room_1",
        )

        validation = simulation.validate_configuration()

        assert validation["is_valid"] is True
        assert validation["errors"] == []
        assert validation["warnings"] == []

    def test_get_factory_metrics(self):
        """Тест получения метрик завода."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        factory_metrics = simulation.get_factory_metrics(step=1)
        assert factory_metrics is not None
        assert isinstance(factory_metrics, FactoryMetrics)

    def test_get_factory_metrics_none_for_invalid_step(self):
        """Тест что get_factory_metrics возвращает None для несуществующего step."""
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[],
            results=[],
            room_id="room_1",
        )

        factory_metrics = simulation.get_factory_metrics(step=999)
        assert factory_metrics is None

    def test_get_production_metrics(self):
        """Тест получения метрик производства."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        production_metrics = simulation.get_production_metrics(step=1)
        assert production_metrics is not None
        assert isinstance(production_metrics, ProductionMetrics)

    def test_get_quality_metrics(self):
        """Тест получения метрик качества."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        quality_metrics = simulation.get_quality_metrics(step=1)
        assert quality_metrics is not None
        assert isinstance(quality_metrics, QualityMetrics)

    def test_get_engineering_metrics(self):
        """Тест получения инженерных метрик."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        engineering_metrics = simulation.get_engineering_metrics(step=1)
        assert engineering_metrics is not None
        assert isinstance(engineering_metrics, EngineeringMetrics)

    def test_get_commercial_metrics(self):
        """Тест получения коммерческих метрик."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        commercial_metrics = simulation.get_commercial_metrics(step=1)
        assert commercial_metrics is not None
        assert isinstance(commercial_metrics, CommercialMetrics)

    def test_get_procurement_metrics(self):
        """Тест получения метрик закупок."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        procurement_metrics = simulation.get_procurement_metrics(step=1)
        assert procurement_metrics is not None
        assert isinstance(procurement_metrics, ProcurementMetrics)

    def test_get_procurement_metrics_none_for_invalid_step(self):
        """Тест что get_procurement_metrics возвращает None для несуществующего step."""
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[],
            results=[],
            room_id="room_1",
        )

        procurement_metrics = simulation.get_procurement_metrics(step=999)
        assert procurement_metrics is None

    def test_get_all_metrics(self):
        """Тест получения всех метрик."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        all_metrics = simulation.get_all_metrics(step=1)

        assert isinstance(all_metrics, dict)
        assert "factory" in all_metrics
        assert "production" in all_metrics
        assert "quality" in all_metrics
        assert "engineering" in all_metrics
        assert "commercial" in all_metrics
        assert "procurement" in all_metrics

        # Все метрики должны быть созданы
        assert all_metrics["factory"] is not None
        assert all_metrics["production"] is not None
        assert all_metrics["quality"] is not None
        assert all_metrics["engineering"] is not None
        assert all_metrics["commercial"] is not None
        assert all_metrics["procurement"] is not None

    def test_get_workshop_plan(self):
        """Тест получения плана цеха."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        workshop_plan = simulation.get_workshop_plan(step=1)
        assert workshop_plan is not None
        assert isinstance(workshop_plan, ProcessGraph)

    def test_get_production_schedule(self):
        """Тест получения производственного плана."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        production_schedule = simulation.get_production_schedule(step=1)
        assert production_schedule is not None

    def test_get_warehouse_load_chart(self):
        """Тест получения графика загрузки склада."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        chart = simulation.get_warehouse_load_chart(warehouse_type="materials", step=1)

        assert isinstance(chart, dict)
        assert "load" in chart
        assert "max_capacity" in chart
        assert isinstance(chart["load"], list)
        assert isinstance(chart["max_capacity"], list)

    def test_get_unplanned_repair(self):
        """Тест получения информации о внеплановых ремонтах."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        # По умолчанию unplanned_repair не создается, должно вернуть None
        repair = simulation.get_unplanned_repair(step=1)
        assert repair is None

    def test_run_simulation_stops_at_step_4(self):
        """Тест что run_simulation выбрасывает ошибку при 5-й попытке запуска."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        # Запускаем симуляцию 4 раза успешно
        for _ in range(4):
            simulation.run_simulation()

        # Проверяем, что количество параметров = 4 (шаги 1, 2, 3, 4)
        assert len(simulation.parameters) == 4
        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[0].step == 1
        assert params_by_step[1].step == 2
        assert params_by_step[2].step == 3
        assert params_by_step[3].step == 4

        # Проверяем, что количество результатов = 4
        assert len(simulation.results) == 4
        results_by_step = sorted(simulation.results, key=lambda r: r.step)
        assert results_by_step[0].step == 1
        assert results_by_step[1].step == 2
        assert results_by_step[2].step == 3
        assert results_by_step[3].step == 4

        # При 5-й попытке должна быть ошибка
        with pytest.raises(ValueError, match="Максимальное количество шагов"):
            simulation.run_simulation()

        # Проверяем, что состояние не изменилось
        assert len(simulation.parameters) == 4
        assert len(simulation.results) == 4

    def test_run_simulation_multiple_calls_after_step_4(self):
        """Тест что run_simulation выбрасывает ошибку при попытке запустить после step 4."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        # Запускаем симуляцию 4 раза (до step 4)
        for _ in range(4):
            simulation.run_simulation()

        params_count_after_4 = len(simulation.parameters)
        results_count_after_4 = len(simulation.results)

        # Проверяем, что у нас 4 параметра и 4 результата
        assert params_count_after_4 == 4
        assert results_count_after_4 == 4

        # Запускаем еще 3 раза - все должны выбросить ошибку
        for _ in range(3):
            with pytest.raises(ValueError, match="Максимальное количество шагов"):
                simulation.run_simulation()

        # Проверяем, что количество не изменилось
        assert len(simulation.parameters) == params_count_after_4
        assert len(simulation.results) == results_count_after_4

    @pytest.mark.asyncio
    async def test_create_simulation_via_factory(self):
        """Тест создания симуляции через фабрику create_default_simulation."""
        # Мокаем сессию и репозитории
        mock_session = AsyncMock()
        mock_lean_repo = AsyncMock()
        mock_workplace_repo = AsyncMock()

        # Мокаем данные из БД
        mock_lean_repo.get_all = AsyncMock(
            return_value=[
                LeanImprovement(
                    improvement_id="imp1",
                    name="Улучшение 1",
                    is_implemented=True,
                ),
                LeanImprovement(
                    improvement_id="imp2",
                    name="Улучшение 2",
                    is_implemented=True,
                ),
            ]
        )

        mock_workplace_repo.get_all = AsyncMock(
            return_value=[
                Workplace(workplace_id="wp1", worker=Worker(worker_id="w1")),
                Workplace(workplace_id="wp2", equipment=Equipment(equipment_id="e1")),
            ]
        )

        # Патчим импорты в правильном месте
        with (
            patch(
                "application.simulation_factory.LeanImprovementRepository",
                return_value=mock_lean_repo,
            ),
            patch(
                "application.simulation_factory.WorkplaceRepository",
                return_value=mock_workplace_repo,
            ),
        ):
            from application.simulation_factory import create_default_simulation

            capital = 15000000
            room_id = "test_room_123"

            simulation = await create_default_simulation(
                session=mock_session,
                capital=capital,
                room_id=room_id,
            )

            # Проверяем валидность данных симуляции
            assert isinstance(simulation, Simulation)
            assert simulation.capital == capital
            assert simulation.room_id == room_id
            assert simulation.simulation_id != ""
            assert len(simulation.simulation_id) > 0
            assert simulation.is_completed is False
            assert len(simulation.results) == 0

            # Проверяем валидность параметров
            assert len(simulation.parameters) == 1
            params = simulation.parameters[0]
            assert isinstance(params, SimulationParameters)
            assert params.capital == capital
            assert params.step == 1

            # Проверяем что улучшения созданы с is_implemented=False
            assert len(params.lean_improvements) == 2
            assert all(not imp.is_implemented for imp in params.lean_improvements)

            # Проверяем что рабочие места без worker и equipment
            assert len(params.processes.workplaces) == 2
            assert all(wp.worker is None for wp in params.processes.workplaces)
            assert all(wp.equipment is None for wp in params.processes.workplaces)

            # Проверяем что routes пуст
            assert params.processes.routes == []

            # Сохраняем начальное количество параметров и результатов
            initial_params_count = len(simulation.parameters)
            initial_results_count = len(simulation.results)

            # Вызываем run_simulation
            simulation.run_simulation()

            # Проверяем, что количество параметров увеличилось на 1
            assert len(simulation.parameters) == initial_params_count + 1
            assert simulation.parameters[1].step == 2

            # Проверяем, что количество результатов увеличилось на 1
            assert len(simulation.results) == initial_results_count + 1

        # Проверяем валидность созданного результата
        result = simulation.results[0]
        assert isinstance(result, SimulationResults)
        assert result.step == 1
        assert result.profit >= 0
        assert result.cost >= 0
        assert isinstance(result.profitability, float)

        # Проверяем наличие всех метрик в результате
        assert result.factory_metrics is not None
        assert result.production_metrics is not None
        assert result.quality_metrics is not None
        assert result.engineering_metrics is not None
        assert result.commercial_metrics is not None
        assert result.procurement_metrics is not None
