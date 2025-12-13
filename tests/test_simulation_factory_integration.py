"""Интеграционные тесты для application/simulation_factory.py"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import AsyncSessionLocal
from infrastructure.repositories import (
    LeanImprovementRepository,
    WorkplaceRepository,
)
from application.simulation_factory import (
    create_default_simulation,
    create_default_simulation_parameters,
)
from domain.simulaton import (
    Simulation,
    SimulationParameters,
    SimulationResults,
)
from domain.metrics import (
    FactoryMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
)


@pytest_asyncio.fixture
async def async_session():
    """Создает асинхронную сессию для интеграционных тестов."""
    async with AsyncSessionLocal() as session:
        yield session


class TestSimulationFactoryIntegration:
    """Интеграционные тесты для фабрики симуляций."""

    @pytest.mark.asyncio
    async def test_create_default_simulation_parameters(self, async_session):
        """Интеграционный тест создания параметров симуляции через фабрику."""
        params = await create_default_simulation_parameters(
            session=async_session,
            capital=15000000,
        )

        # Проверяем валидность данных
        assert isinstance(params, SimulationParameters)
        assert params.capital == 15000000
        assert params.step == 1

        # Проверяем что есть улучшения (из БД)
        assert isinstance(params.lean_improvements, list)

        # Проверяем что есть сертификации
        assert isinstance(params.certifications, list)
        assert len(params.certifications) > 0

        # Проверяем что есть рабочие места (из БД)
        assert isinstance(params.processes.workplaces, list)

        # Проверяем что у рабочих мест нет worker и equipment
        for wp in params.processes.workplaces:
            assert wp.worker is None
            assert wp.equipment is None

        # Проверяем что routes пуст
        assert len(params.processes.routes) == 0

        # Проверяем что у улучшений is_implemented=False
        for improvement in params.lean_improvements:
            assert improvement.is_implemented is False

        # Проверяем что у сертификаций is_obtained=False
        for cert in params.certifications:
            assert cert.is_obtained is False

    @pytest.mark.asyncio
    async def test_create_default_simulation(self, async_session):
        """Интеграционный тест создания симуляции через фабрику."""
        capital = 20000000
        room_id = "integration_test_room_123"

        simulation = await create_default_simulation(
            session=async_session,
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
        assert isinstance(params.lean_improvements, list)
        assert all(not imp.is_implemented for imp in params.lean_improvements)

        # Проверяем что рабочие места без worker и equipment
        assert isinstance(params.processes.workplaces, list)
        assert all(wp.worker is None for wp in params.processes.workplaces)
        assert all(wp.equipment is None for wp in params.processes.workplaces)

        # Проверяем что routes пуст
        assert params.processes.routes == []

    @pytest.mark.asyncio
    async def test_create_simulation_and_run_multiple_times(self, async_session):
        """Интеграционный тест: создание симуляции и запуск несколько раз."""
        capital = 20000000
        room_id = "integration_test_room_run"

        simulation = await create_default_simulation(
            session=async_session,
            capital=capital,
            room_id=room_id,
        )

        # Сохраняем начальное количество параметров и результатов
        initial_params_count = len(simulation.parameters)
        initial_results_count = len(simulation.results)

        # Вызываем run_simulation
        simulation.run_simulation()

        # Проверяем, что количество параметров увеличилось на 1
        assert len(simulation.parameters) == initial_params_count + 1
        # Находим параметры с step=2
        step_2_params = [p for p in simulation.parameters if p.step == 2]
        assert len(step_2_params) == 1
        # Проверяем что параметры отсортированы правильно
        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[1].step == 2

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

    @pytest.mark.asyncio
    async def test_run_simulation_stops_at_step_4_integration(self, async_session):
        """Интеграционный тест: run_simulation выбрасывает ошибку при 5-й попытке."""
        capital = 20000000
        room_id = "integration_test_room_step4"

        simulation = await create_default_simulation(
            session=async_session,
            capital=capital,
            room_id=room_id,
        )

        # Запускаем симуляцию 4 раза успешно
        for _ in range(4):
            simulation.run_simulation()

        # Проверяем, что количество параметров = 4 (шаги 1, 2, 3, 4)
        assert len(simulation.parameters) == 4
        # Сортируем по step для проверки
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
