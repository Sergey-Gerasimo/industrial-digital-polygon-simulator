"""Фабричные функции для создания доменных объектов симуляции."""

from uuid import uuid4
from dataclasses import replace
from infrastructure.config import app_logger

from sqlalchemy.ext.asyncio import AsyncSession

from domain.simulaton import (
    Simulation,
    SimulationParameters,
    DealingWithDefects,
    SaleStrategest,
)
from domain.certification import Certification
from domain.lean_improvement import LeanImprovement
from domain.warehouse import Warehouse
from domain.process_graph import ProcessGraph
from domain.production_plan import ProductionSchedule
from domain.distribution import DistributionStrategy
from domain.reference_data import Certification as CertificationEnum

from infrastructure.repositories import (
    LeanImprovementRepository,
    WorkplaceRepository,
)


async def create_default_simulation_parameters(
    session: AsyncSession,
    capital: int = 10000000,
) -> SimulationParameters:
    """Создает параметры симуляции с дефолтными значениями из БД.

    - lean_improvements: все улучшения из БД с is_implemented=False
    - certifications: все сертификации из enum с is_obtained=False
    - processes: ProcessGraph со всеми рабочими местами из БД (без worker и equipment, без routes)

    Args:
        session: Асинхронная сессия SQLAlchemy для доступа к репозиториям

    Returns:
        SimulationParameters с дефолтными значениями
    """
    # Получаем все LeanImprovement из БД
    lean_improvement_repo = LeanImprovementRepository(session)
    all_lean_improvements = await lean_improvement_repo.get_all()

    app_logger.info(f"All lean improvements: {all_lean_improvements}")

    # Создаем копии с is_implemented=False
    lean_improvements = [
        replace(improvement, is_implemented=False)
        for improvement in all_lean_improvements
    ]

    # Создаем все сертификации из enum с is_obtained=False
    certifications = [
        Certification(
            certificate_type=cert.value,
            is_obtained=False,
            implementation_cost=0,
            implementation_time_days=0,
        )
        for cert in CertificationEnum
    ]

    # Получаем все Workplace из БД
    workplace_repo = WorkplaceRepository(session)
    all_workplaces = await workplace_repo.get_all()

    # Создаем копии без worker и equipment
    workplaces = [
        replace(
            workplace,
            worker=None,
            equipment=None,
        )
        for workplace in all_workplaces
    ]

    # Создаем ProcessGraph с рабочими местами, но без routes
    processes = ProcessGraph(
        process_graph_id=str(uuid4()),
        workplaces=workplaces,
        routes=[],
    )

    return SimulationParameters(
        logist=None,
        suppliers=list(),
        backup_suppliers=list(),
        materials_warehouse=Warehouse(size=1000, materials={}),
        product_warehouse=Warehouse(size=1000, materials={}),
        processes=processes,
        tenders=list(),
        dealing_with_defects=DealingWithDefects.NONE,
        production_improvements=list(),
        sales_strategy=SaleStrategest.NONE,
        production_schedule=ProductionSchedule(),
        certifications=certifications,
        lean_improvements=lean_improvements,
        distribution_strategy=DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED,
        step=1,
        capital=capital,
    )


async def create_default_simulation(
    session: AsyncSession,
    capital: int,
    room_id: str,
) -> Simulation:
    """Создает симуляцию с дефолтными параметрами.

    Args:
        session: Асинхронная сессия SQLAlchemy для доступа к репозиториям
        capital: начальный капитал симуляции
        room_id: идентификатор комнаты/сессии

    Returns:
        Simulation с дефолтными параметрами и указанными capital и room_id
    """
    # Создаем стандартные параметры симуляции
    default_parameters = await create_default_simulation_parameters(session)

    # Обновляем капитал в параметрах
    default_parameters.capital = capital

    # Генерируем ID симуляции
    simulation_id = str(uuid4())

    # Создаем объект Simulation
    return Simulation(
        capital=capital,
        simulation_id=simulation_id,
        parameters=[default_parameters],
        results=list(),
        room_id=room_id,
        is_completed=False,
    )
