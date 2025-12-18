"""Тесты для domain/simulaton.py - класс Simulation"""

import pytest
from unittest.mock import AsyncMock, patch

from domain.simulaton import (
    Simulation,
    SimulationParameters,
    SimulationResults,
    SaleStrategest,
    DealingWithDefects,
)
from domain.warehouse import Warehouse
from domain.supplier import Supplier
from domain.tender import Tender
from domain.process_graph import ProcessGraph
from domain.worker import Worker
from domain.equipment import Equipment
from domain.workplace import Workplace
from domain.lean_improvement import LeanImprovement
from domain.certification import Certification
from domain.logist import Logist
from domain.production_plan import ProductionSchedule
from domain.distribution import DistributionStrategy
from domain.metrics import (
    FactoryMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
)


def create_non_empty_simulation_parameters(step: int = 1, capital: int = 10000000) -> SimulationParameters:
    """Создает параметры симуляции, которые считаются непустыми согласно _is_empty_simulation_parameters."""
    return SimulationParameters(
        step=step,
        capital=capital,
        logist=Logist(worker_id="test_logist", name="Test Logist"),
        suppliers=[Supplier(supplier_id="supplier_1", name="Supplier 1", product_quality=0.9, delivery_period=7, cost=100)],
        backup_suppliers=[Supplier(supplier_id="backup_1", name="Backup Supplier", product_quality=0.8, delivery_period=10, cost=120)],
        materials_warehouse=Warehouse(size=1000, materials={}),
        product_warehouse=Warehouse(size=1000, materials={}),
        processes=ProcessGraph(process_graph_id="test_graph", workplaces=[Workplace(workplace_id="wp1", equipment=Equipment(equipment_id="eq1", name="Test Equipment"), worker=Worker(worker_id="w1", name="Test Worker"))]),
        tenders=[Tender(tender_id="tender_1", quantity_of_products=100)],
        dealing_with_defects=DealingWithDefects.DISPOSE,
        production_improvements=[LeanImprovement(improvement_id="imp1", name="Test Improvement", is_implemented=False)],
        sales_strategy=SaleStrategest.NONE,
        production_schedule=ProductionSchedule(),
        certifications=[Certification(certificate_type="ISO9001", is_obtained=False)],
        lean_improvements=[LeanImprovement(improvement_id="lean1", name="Lean Improvement", is_implemented=False)],
        distribution_strategy=DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED,
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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

    def test_run_simulation_creates_next_parameters_until_limit(self):
        """Тест что run_simulation создает параметры для следующего шага, пока не достигнут лимит результатов."""
        # Создаем симуляцию с параметрами шагов 1, 2 и результатами для шагов 1
        params1 = create_non_empty_simulation_parameters(step=1, capital=10000000)
        params2 = create_non_empty_simulation_parameters(step=2, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params1, params2],
            results=[],
            room_id="room_1",
        )
        # Добавляем результат для шага 1, чтобы следующий результат был для step 2
        result1 = SimulationResults(step=1, profit=0, cost=0, profitability=0.0)
        simulation.results = [result1]

        initial_params_count = len(simulation.parameters)
        simulation.run_simulation()

        # Проверяем, что созданы новые параметры для шага 3
        assert len(simulation.parameters) == initial_params_count + 1
        assert simulation.parameters[-1].step == 3
        # Проверяем, что результат для step 2 был создан
        assert len(simulation.results) == 2

    def test_run_simulation_with_multiple_steps(self):
        """Тест run_simulation для нескольких шагов."""
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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

    def test_run_simulation_with_empty_parameters_list(self):
        """Тест run_simulation с пустым списком параметров."""
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[],
            results=[],
            room_id="room_1",
        )

        # Должно выбросить ValueError
        with pytest.raises(ValueError, match="Отсутвуют параметры для выполнения симуляции"):
            simulation.run_simulation()

        # Результаты не должны быть созданы
        assert len(simulation.results) == 0

    def test_run_simulation_with_empty_simulation_parameters(self):
        """Тест run_simulation с пустыми параметрами симуляции (согласно _is_empty_simulation_parameters)."""
        # Создаем параметры с минимальными значениями, которые считаются пустыми
        empty_params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[empty_params],
            results=[],
            room_id="room_1",
        )

        # Должно выбросить ValueError из-за пустых параметров
        with pytest.raises(ValueError, match="Отсутвуют параметры для выполнения симуляции"):
            simulation.run_simulation()

        # Результаты не должны быть созданы
        assert len(simulation.results) == 0

    def test_run_simulation_uses_latest_parameters(self):
        """Тест что run_simulation использует последние параметры (с максимальным step)."""
        params0 = create_non_empty_simulation_parameters(step=1, capital=10000000)
        params1 = create_non_empty_simulation_parameters(step=2, capital=20000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params0, params1],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        # Проверяем, что результат создается с step параметров, которые использовались для расчета
        result = simulation.results[0]
        assert result.step == 2  # Используются последние параметры со step=2

        # Проверяем, что созданы новые параметры для следующего шага (step=3)
        assert len(simulation.parameters) == 3
        assert simulation.parameters[2].step == 3

    def test_run_simulation_with_suppliers_and_tenders(self):
        """Тест run_simulation с поставщиками и тендерами."""
        # Создаем непустые параметры и добавляем дополнительные поставщики и тендеры для тестирования
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)

        # Добавляем дополнительные поставщики и тендеры
        additional_supplier = Supplier(
            supplier_id="supplier_extra",
            name="Дополнительный поставщик",
            product_quality=0.8,
            reliability=0.9,
            delivery_period=14,
            cost=1200,
        )
        params.suppliers.append(additional_supplier)

        additional_tender = Tender(tender_id="tender_extra", quantity_of_products=200)
        params.tenders.append(additional_tender)

        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        simulation.run_simulation()

        result = simulation.results[0]

        # Проверяем, что метрики созданы
        assert result.procurement_metrics is not None
        # Примечание: supplier_performances пока не реализован, поэтому проверяем только наличие метрики

        assert result.commercial_metrics is not None
        # Примечание: tender_graph пока не реализован, поэтому проверяем только наличие метрики

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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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
        # Проверяем структуру, если данные есть
        if chart:
            assert "load" in chart
            assert "max_capacity" in chart
            assert isinstance(chart["load"], list)
            assert isinstance(chart["max_capacity"], list)

    def test_get_unplanned_repair(self):
        """Тест получения информации о внеплановых ремонтах."""
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
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

    def test_run_simulation_stops_at_step_3(self):
        """Тест что run_simulation выбрасывает ошибку при 4-й попытке запуска."""
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        # Запускаем симуляцию 3 раза успешно
        for _ in range(3):
            simulation.run_simulation()

        # Проверяем, что количество параметров = 4 (шаги 1, 2, 3, 4)
        assert len(simulation.parameters) == 4
        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[0].step == 1
        assert params_by_step[1].step == 2
        assert params_by_step[2].step == 3
        assert params_by_step[3].step == 4

        # Проверяем, что количество результатов = 3
        assert len(simulation.results) == 3
        results_by_step = sorted(simulation.results, key=lambda r: r.step)
        assert results_by_step[0].step == 1
        assert results_by_step[1].step == 2
        assert results_by_step[2].step == 3

        # При 4-й попытке должна быть ошибка
        with pytest.raises(ValueError, match="Максимальное количество шагов"):
            simulation.run_simulation()

        # Проверяем, что состояние не изменилось
        assert len(simulation.parameters) == 4
        assert len(simulation.results) == 3

    def test_run_simulation_multiple_calls_after_step_4(self):
        """Тест что run_simulation выбрасывает ошибку при попытке запустить после step 3."""
        params = create_non_empty_simulation_parameters(step=1, capital=10000000)
        simulation = Simulation(
            capital=10000000,
            simulation_id="test_id",
            parameters=[params],
            results=[],
            room_id="room_1",
        )

        # Запускаем симуляцию 3 раза (до step 3)
        for _ in range(3):
            simulation.run_simulation()

        params_count_after_3 = len(simulation.parameters)
        results_count_after_3 = len(simulation.results)

        # Проверяем, что у нас 4 параметра и 3 результата
        assert params_count_after_3 == 4
        assert results_count_after_3 == 3

        # Запускаем еще 3 раза - все должны выбросить ошибку
        for _ in range(3):
            with pytest.raises(ValueError, match="Максимальное количество шагов"):
                simulation.run_simulation()

        # Проверяем, что количество не изменилось
        assert len(simulation.parameters) == params_count_after_3
        assert len(simulation.results) == results_count_after_3

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

            # Настраиваем параметры для запуска симуляции (пользователь должен добавить эти поля)
            params = simulation.parameters[0]
            params.logist = Logist(worker_id="test_logist", name="Test Logist")
            params.suppliers = [Supplier(supplier_id="supplier_1", name="Supplier 1", product_quality=0.9, delivery_period=7, cost=100)]
            params.backup_suppliers = [Supplier(supplier_id="backup_1", name="Backup Supplier", product_quality=0.8, delivery_period=10, cost=120)]
            params.tenders = [Tender(tender_id="tender_1", quantity_of_products=100, cost=1000)]

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
