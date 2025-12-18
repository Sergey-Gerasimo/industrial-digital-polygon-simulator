from datetime import datetime
from typing import Callable, Optional, TypeVar, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from domain.simulaton import Simulation

import grpc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from grpc_generated.simulator_pb2 import (
    # Базовые запросы и ответы
    CreateSimulationRquest,
    GetSimulationRequest,
    SimulationResponse,
    SuccessResponse,
    PingRequest,
    RunSimulationRequest,
    # Конфигурация персонала
    SetLogistRequest,
    SetWarehouseInventoryWorkerRequest,
    SetWorkerOnWorkerplaceRequest,
    UnSetWorkerOnWorkerplaceRequest,
    # Конфигурация поставщиков
    AddSupplierRequest,
    DeleteSupplierRequest,
    # Конфигурация складов
    IncreaseWarehouseSizeRequest,
    # Управление графом процесса
    UpdateProcessGraphRequest,
    # Распределение плана (Производство)
    SetProductionPlanRowRequest,
    # Конфигурация тендеров
    AddTenderRequest,
    RemoveTenderRequest,
    # Общие настройки
    SetDealingWithDefectsRequest,
    SetSalesStrategyRequest,
    SetLeanImprovementStatusRequest,
    # Специфичные настройки по ролям
    SetQualityInspectionRequest,
    SetDeliveryPeriodRequest,
    SetEquipmentMaintenanceIntervalRequest,
    SetCertificationStatusRequest,
    # Методы получения метрик и мониторинга
    GetMetricsRequest,
    FactoryMetricsResponse,
    ProductionMetricsResponse,
    QualityMetricsResponse,
    EngineeringMetricsResponse,
    CommercialMetricsResponse,
    ProcurementMetricsResponse,
    GetAllMetricsRequest,
    AllMetricsResponse,
    # Методы получения данных для вкладок
    GetProductionScheduleRequest,
    ProductionScheduleResponse,
    GetWorkshopPlanRequest,
    WorkshopPlanResponse,
    GetUnplannedRepairRequest,
    UnplannedRepairResponse,
    GetWarehouseLoadChartRequest,
    WarehouseLoadChartResponse,
    GetRequiredMaterialsRequest,
    RequiredMaterialsResponse,
    UnplannedRepair,
    WarehouseLoadChart,
    RequiredMaterial,
    GetAvailableImprovementsRequest,
    AvailableImprovementsResponse,
    GetDefectPoliciesRequest,
    DefectPoliciesResponse,
    # Валидация
    ValidateConfigurationRequest,
    ValidationResponse,
    # Справочные данные
    GetMaterialTypesRequest,
    MaterialTypesResponse,
    GetEquipmentTypesRequest,
    EquipmentTypesResponse,
    GetWorkplaceTypesRequest,
    WorkplaceTypesResponse,
    GetAvailableDefectPoliciesRequest,
    DefectPoliciesListResponse,
    GetAvailableImprovementsListRequest,
    ImprovementsListResponse,
    GetAvailableCertificationsRequest,
    CertificationsListResponse,
    GetAvailableSalesStrategiesRequest,
    SalesStrategiesListResponse,
)
from grpc_generated.simulator_pb2_grpc import SimulationServiceServicer

from infrastructure.repositories import (
    SimulationRepository,
    WorkerRepository,
    SupplierRepository,
    TenderRepository,
    EquipmentRepository,
)
from application.proto_mappers import (
    domain_simulation_to_proto,
    proto_simulation_to_domain,
    domain_factory_metrics_obj_to_proto,
    domain_production_metrics_obj_to_proto,
    domain_quality_metrics_obj_to_proto,
    domain_engineering_metrics_obj_to_proto,
    domain_commercial_metrics_obj_to_proto,
    domain_procurement_metrics_obj_to_proto,
    proto_process_graph_to_domain,
    proto_production_plan_row_to_domain,
)
from application.simulation_factory import create_default_simulation
from domain.simulaton import SimulationParameters

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SimulationServiceImpl(SimulationServiceServicer):
    """Реализация сервиса симуляции с использованием принципов DDD."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    # -----------------------------------------------------------------
    #          Базовые методы работы с симуляцией
    # -----------------------------------------------------------------

    async def _load_simulation(
        self, session: AsyncSession, simulation_id: str, context
    ):
        """Загружает симуляцию из БД."""
        from domain import Simulation

        try:
            repo = SimulationRepository(session)
            simulation = await repo.get(simulation_id)

            if simulation is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Симуляция с ID {simulation_id} не найдена")
                return None

            return simulation
        except Exception as e:
            logger.error(f"Error loading simulation: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка при загрузке симуляции: {str(e)}")
            return None

    async def _save_simulation(self, session: AsyncSession, simulation, context):
        """Сохраняет симуляцию в БД."""
        try:
            repo = SimulationRepository(session)
            saved = await repo.save(simulation)

            if saved is None:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Ошибка при сохранении симуляции")
                return None

            return saved
        except Exception as e:
            logger.error(f"Error saving simulation: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка при сохранении симуляции: {str(e)}")
            return None

    def _get_simulation_parameters(self, simulation) -> SimulationParameters:
        """Возвращает последние параметры симуляции (с максимальным step)."""
        if not simulation.parameters:
            raise ValueError("У симуляции нет параметров")
        return max(simulation.parameters, key=lambda p: p.step)

    async def _update_and_save(
        self,
        simulation_id: str,
        update_func: Callable,
        context,
    ) -> SimulationResponse:
        """Универсальный метод для загрузки, обновления и сохранения симуляции."""
        async with self.session_factory() as session:
            try:
                simulation = await self._load_simulation(
                    session, simulation_id, context
                )
                if simulation is None:
                    return SimulationResponse()

                # Выполняем обновление (может выбросить ValueError)
                update_func(simulation)

                saved = await self._save_simulation(session, simulation, context)
                if saved is None:
                    return SimulationResponse()

                # Коммитим изменения перед возвратом
                await session.commit()

                # Возвращаем обновленную симуляцию по ID
                return await self._build_simulation_response(session, simulation_id)
            except ValueError:
                # Пробрасываем ValueError наверх для обработки в вызывающем методе
                await session.rollback()
                raise
            except Exception as e:
                await session.rollback()
                logger.error(f"Error in _update_and_save: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении симуляции: {str(e)}")
                return SimulationResponse()

    async def _build_simulation_response(
        self, session: AsyncSession, simulation_id: Optional[str] = None
    ) -> SimulationResponse:
        """Формирует ответ с симуляцией(ями).

        Args:
            session: Асинхронная сессия БД
            simulation_id: Опциональный ID симуляции. Если указан, возвращает только эту симуляцию.
                          Если не указан, возвращает последнюю из всех симуляций.
        """
        if simulation_id:
            # Возвращаем конкретную симуляцию по ID
            repo = SimulationRepository(session)
            simulation = await repo.get(simulation_id)
            if simulation:
                proto_simulation = domain_simulation_to_proto(simulation)
                return SimulationResponse(
                    simulations=proto_simulation,
                    timestamp=datetime.now().isoformat(),
                )
            else:
                return SimulationResponse(timestamp=datetime.now().isoformat())
        else:
            # Возвращаем последнюю симуляцию из всех
            repo = SimulationRepository(session)
            all_simulations = await repo.get_all()

            if all_simulations:
                proto_simulation = domain_simulation_to_proto(all_simulations[-1])
                return SimulationResponse(
                    simulations=proto_simulation,
                    timestamp=datetime.now().isoformat(),
                )
            else:
                return SimulationResponse(timestamp=datetime.now().isoformat())

    # -----------------------------------------------------------------
    #          Базовые методы симуляции
    # -----------------------------------------------------------------

    async def create_simulation(
        self, request: CreateSimulationRquest, context
    ) -> SimulationResponse:
        """Создает новую симуляцию."""
        async with self.session_factory() as session:
            try:
                # Получаем room_id из метаданных gRPC, если доступно, иначе используем пустую строку
                room_id = ""
                if context and hasattr(context, "invocation_metadata"):
                    metadata = dict(context.invocation_metadata())
                    room_id = metadata.get("room-id", "")

                # Используем дефолтный капитал (можно позже добавить в request)
                capital = 10000000  # 10 миллионов по умолчанию

                # Используем фабрику для создания симуляции с дефолтными параметрами
                simulation = await create_default_simulation(
                    session=session,
                    capital=capital,
                    room_id=room_id,
                )

                logger.info(f"Simulation created: {simulation}")

                saved = await self._save_simulation(session, simulation, context)

                if saved is None:
                    return SimulationResponse()

                # Возвращаем созданную симуляцию по ID
                return await self._build_simulation_response(
                    session, saved.simulation_id
                )
            except Exception as e:
                logger.error(f"Error creating simulation: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании симуляции: {str(e)}")
                return SimulationResponse()

    async def get_simulation(
        self, request: GetSimulationRequest, context
    ) -> SimulationResponse:
        """Получает симуляцию по ID."""
        async with self.session_factory() as session:
            try:
                simulation = await self._load_simulation(
                    session, request.simulation_id, context
                )
                if simulation is None:
                    return SimulationResponse()

                proto_simulation = domain_simulation_to_proto(simulation)
                return SimulationResponse(
                    simulations=proto_simulation,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting simulation: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении симуляции: {str(e)}")
                return SimulationResponse()

    async def run_simulation(
        self, request: RunSimulationRequest, context
    ) -> SimulationResponse:
        """Запускает одну итерацию симуляции.

        Максимальное количество шагов симуляции - 4 (шаги 1, 2, 3, 4).
        При попытке запустить симуляцию в 5-й и далее раз возвращается ошибка.
        """
        try:
            # Запускаем симуляцию (все проверки выполняются в доменном классе)
            # _update_and_save создает свою сессию, поэтому не нужно создавать еще одну
            return await self._update_and_save(
                request.simulation_id,
                lambda sim: sim.run_simulation(),
                context,
            )
        except ValueError as e:
            # Обрабатываем бизнес-ошибки из доменного класса
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(str(e))
            return SimulationResponse()
        except Exception as e:
            logger.error(f"Error running simulation: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка при запуске симуляции: {str(e)}")
            return SimulationResponse()

    # -----------------------------------------------------------------
    #          Конфигурация персонала
    # -----------------------------------------------------------------

    async def set_logist(
        self, request: SetLogistRequest, context
    ) -> SimulationResponse:
        """Устанавливает логиста для симуляции."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            worker_repo = WorkerRepository(session)
            logist = await worker_repo.get(request.worker_id)

            if logist is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Логист с ID {request.worker_id} не найден")
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            params.set_logist(logist)
            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def set_warehouse_inventory_worker(
        self, request: SetWarehouseInventoryWorkerRequest, context
    ) -> SimulationResponse:
        """Устанавливает складского работника для симуляции."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            worker_repo = WorkerRepository(session)
            worker = await worker_repo.get(request.worker_id)

            if worker is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Работник с ID {request.worker_id} не найден")
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            if request.warehouse_type == 1:  # WAREHOUSE_TYPE_MATERIALS
                params.set_material_warehouse_inventory_worker(worker)
            elif request.warehouse_type == 2:  # WAREHOUSE_TYPE_PRODUCTS
                params.set_product_warehouse_inventory_worker(worker)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def set_worker_on_workerplace(
        self, request: SetWorkerOnWorkerplaceRequest, context
    ) -> SimulationResponse:
        """Устанавливает работника на рабочее место."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            worker_repo = WorkerRepository(session)
            worker = await worker_repo.get(request.worker_id)

            if worker is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Работник с ID {request.worker_id} не найден")
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            # Используем метод ProcessGraph, так как в SimulationParameters нет метода для этого
            # Это допустимо, так как processes - это часть SimulationParameters
            params.processes.set_worker_on_workplace(request.workplace_id, worker)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def unset_worker_on_workerplace(
        self, request: UnSetWorkerOnWorkerplaceRequest, context
    ) -> SimulationResponse:
        """Убирает работника с рабочего места."""

        def unset_worker(sim):
            # Получаем параметры напрямую из симуляции
            if not sim.parameters:
                raise ValueError("У симуляции нет параметров")
            params = max(sim.parameters, key=lambda p: p.step)
            params.processes.unset_worker_on_workplace(request.worker_id)

        return await self._update_and_save(
            request.simulation_id,
            unset_worker,
            context,
        )

    # -----------------------------------------------------------------
    #          Конфигурация поставщиков
    # -----------------------------------------------------------------

    async def add_supplier(
        self, request: AddSupplierRequest, context
    ) -> SimulationResponse:
        """Добавляет поставщика к симуляции."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            supplier_repo = SupplierRepository(session)
            supplier = await supplier_repo.get(request.supplier_id)

            if supplier is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Поставщик с ID {request.supplier_id} не найден")
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            if request.is_backup:
                params.add_backup_supplier(supplier)
            else:
                params.add_supplier(supplier)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def delete_supplier(
        self, request: DeleteSupplierRequest, context
    ) -> SimulationResponse:
        """Удаляет поставщика из симуляции."""

        def remove_supplier(sim):
            # Получаем параметры напрямую из симуляции
            if not sim.parameters:
                raise ValueError("У симуляции нет параметров")
            params = max(sim.parameters, key=lambda p: p.step)
            params.remove_supplier(request.supplier_id)
            params.remove_backup_supplier(request.supplier_id)

        return await self._update_and_save(
            request.simulation_id,
            remove_supplier,
            context,
        )

    # -----------------------------------------------------------------
    #          Конфигурация складов
    # -----------------------------------------------------------------

    async def increase_warehouse_size(
        self, request: IncreaseWarehouseSizeRequest, context
    ) -> SimulationResponse:
        """Увеличивает размер склада."""

        def update_size(sim):
            # Получаем параметры напрямую из симуляции
            if not sim.parameters:
                raise ValueError("У симуляции нет параметров")
            params = max(sim.parameters, key=lambda p: p.step)
            if request.warehouse_type == 1:  # WAREHOUSE_TYPE_MATERIALS
                params.increase_material_warehouse_size(request.size)
            elif request.warehouse_type == 2:  # WAREHOUSE_TYPE_PRODUCTS
                params.increase_product_warehouse_size(request.size)

        return await self._update_and_save(request.simulation_id, update_size, context)

    # -----------------------------------------------------------------
    #          Управление графом процесса
    # -----------------------------------------------------------------

    async def update_process_graph(
        self, request: UpdateProcessGraphRequest, context
    ) -> SimulationResponse:
        """Обновляет граф процесса."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            process_graph = proto_process_graph_to_domain(request.process_graph)
            params = self._get_simulation_parameters(simulation)
            params.set_process_graph(process_graph)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    # -----------------------------------------------------------------
    #          Распределение производственного плана
    # -----------------------------------------------------------------

    async def set_production_plan_row(
        self, request: SetProductionPlanRowRequest, context
    ) -> SimulationResponse:
        """Устанавливает/обновляет строку производственного плана."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            row = proto_production_plan_row_to_domain(request.row)
            params = self._get_simulation_parameters(simulation)
            # Используем метод из SimulationParameters вместо прямого доступа к production_schedule
            params.set_production_plan_row(row)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    # -----------------------------------------------------------------
    #          Конфигурация тендеров
    # -----------------------------------------------------------------

    async def add_tender(
        self, request: AddTenderRequest, context
    ) -> SimulationResponse:
        """Добавляет тендер к симуляции."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            tender_repo = TenderRepository(session)
            tender = await tender_repo.get(request.tender_id)

            if tender is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Тендер с ID {request.tender_id} не найден")
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            params.add_tender(tender)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def delete_tender(
        self, request: RemoveTenderRequest, context
    ) -> SimulationResponse:
        """Удаляет тендер из симуляции."""

        def remove_tender(sim):
            # Получаем параметры напрямую из симуляции
            if not sim.parameters:
                raise ValueError("У симуляции нет параметров")
            params = max(sim.parameters, key=lambda p: p.step)
            params.remove_tender(request.tender_id)

        return await self._update_and_save(
            request.simulation_id,
            remove_tender,
            context,
        )

    # -----------------------------------------------------------------
    #          Общие настройки
    # -----------------------------------------------------------------

    async def set_dealing_with_defects(
        self, request: SetDealingWithDefectsRequest, context
    ) -> SimulationResponse:
        """Устанавливает политику работы с дефектами."""
        from domain import DealingWithDefects

        def update_policy(sim):
            try:
                policy = DealingWithDefects(request.dealing_with_defects)
            except (ValueError, KeyError):
                policy = DealingWithDefects.NONE
            # Получаем параметры напрямую из симуляции
            if not sim.parameters:
                raise ValueError("У симуляции нет параметров")
            params = max(sim.parameters, key=lambda p: p.step)
            params.set_dealing_with_defects(policy)

        return await self._update_and_save(
            request.simulation_id, update_policy, context
        )

    async def set_sales_strategy(
        self, request: SetSalesStrategyRequest, context
    ) -> SimulationResponse:
        """Устанавливает стратегию продаж."""

        def update_strategy(sim):
            # Получаем параметры напрямую из симуляции
            if not sim.parameters:
                raise ValueError("У симуляции нет параметров")
            params = max(sim.parameters, key=lambda p: p.step)
            params.set_sales_strategy(request.strategy)

        return await self._update_and_save(
            request.simulation_id, update_strategy, context
        )

    async def set_lean_improvement_status(
        self, request: SetLeanImprovementStatusRequest, context
    ) -> SimulationResponse:
        """Устанавливает статус LEAN улучшения."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            params.set_lean_improvement_status(request.name, request.is_implemented)

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    # -----------------------------------------------------------------
    #          Специфичные настройки по ролям
    # -----------------------------------------------------------------

    async def set_quality_inspection(
        self, request: SetQualityInspectionRequest, context
    ) -> SimulationResponse:
        """Устанавливает проверку качества для материалов от поставщика."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            # Устанавливаем контроль качества напрямую в сущности поставщика
            params = self._get_simulation_parameters(simulation)
            params.set_quality_inspection(
                request.supplier_id,
                request.inspection_enabled,
            )

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def set_delivery_period(
        self, request: SetDeliveryPeriodRequest, context
    ) -> SimulationResponse:
        """Устанавливает период поставок в днях для поставщика."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            # Устанавливаем период поставок напрямую в сущности поставщика
            params = self._get_simulation_parameters(simulation)
            params.set_delivery_period(
                request.supplier_id,
                request.delivery_period_days,
            )

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    async def set_equipment_maintenance_interval(
        self, request: SetEquipmentMaintenanceIntervalRequest, context
    ) -> SimulationResponse:
        """Устанавливает интервал обслуживания оборудования.

        Примечание: интервалы обслуживания хранятся в Equipment на каждом рабочем месте,
        а не в SimulationParameters. Этот метод требует реализации для поиска и обновления
        соответствующего оборудования в processes.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details(
            "Интервалы обслуживания хранятся в Equipment. "
            "Используйте обновление ProcessGraph для изменения оборудования."
        )
        return SimulationResponse()

    async def set_certification_status(
        self, request: SetCertificationStatusRequest, context
    ) -> SimulationResponse:
        """Устанавливает статус сертификации."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return SimulationResponse()

            params = self._get_simulation_parameters(simulation)
            # Используем метод из SimulationParameters
            try:
                params.set_certification_status(
                    request.certificate_type, request.is_obtained
                )
            except ValueError:
                # Если сертификация не найдена, это ошибка конфигурации
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(
                    f"Сертификация с типом '{request.certificate_type}' не найдена"
                )
                return SimulationResponse()

            saved = await self._save_simulation(session, simulation, context)
            if saved is None:
                return SimulationResponse()

            # Возвращаем обновленную симуляцию по ID
            return await self._build_simulation_response(session, request.simulation_id)

    # -----------------------------------------------------------------
    #          Методы получения метрик и мониторинга
    # -----------------------------------------------------------------

    async def get_factory_metrics(
        self, request: GetMetricsRequest, context
    ) -> FactoryMetricsResponse:
        """Получает метрики завода."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return FactoryMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return FactoryMetricsResponse()

            try:
                metrics = simulation.get_factory_metrics(step=step)
                if metrics is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Метрики завода для шага {step} не найдены")
                    return FactoryMetricsResponse()

                proto_metrics = domain_factory_metrics_obj_to_proto(metrics)
                return FactoryMetricsResponse(
                    metrics=proto_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting factory metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении метрик: {str(e)}")
                return FactoryMetricsResponse()

    async def get_production_metrics(
        self, request: GetMetricsRequest, context
    ) -> ProductionMetricsResponse:
        """Получает метрики производства."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return ProductionMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return ProductionMetricsResponse()

            try:
                metrics = simulation.get_production_metrics(step=step)
                if metrics is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Метрики производства для шага {step} не найдены"
                    )
                    return ProductionMetricsResponse()

                proto_metrics = domain_production_metrics_obj_to_proto(metrics)
                return ProductionMetricsResponse(
                    metrics=proto_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting production metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении метрик: {str(e)}")
                return ProductionMetricsResponse()

    async def get_quality_metrics(
        self, request: GetMetricsRequest, context
    ) -> QualityMetricsResponse:
        """Получает метрики качества."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return QualityMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return QualityMetricsResponse()

            try:
                metrics = simulation.get_quality_metrics(step=step)
                if metrics is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Метрики качества для шага {step} не найдены")
                    return QualityMetricsResponse()

                proto_metrics = domain_quality_metrics_obj_to_proto(metrics)
                return QualityMetricsResponse(
                    metrics=proto_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting quality metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении метрик: {str(e)}")
                return QualityMetricsResponse()

    async def get_engineering_metrics(
        self, request: GetMetricsRequest, context
    ) -> EngineeringMetricsResponse:
        """Получает метрики инженерии."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return EngineeringMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return EngineeringMetricsResponse()

            try:
                metrics = simulation.get_engineering_metrics(step=step)
                if metrics is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Инженерные метрики для шага {step} не найдены"
                    )
                    return EngineeringMetricsResponse()

                proto_metrics = domain_engineering_metrics_obj_to_proto(metrics)
                return EngineeringMetricsResponse(
                    metrics=proto_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting engineering metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении метрик: {str(e)}")
                return EngineeringMetricsResponse()

    async def get_commercial_metrics(
        self, request: GetMetricsRequest, context
    ) -> CommercialMetricsResponse:
        """Получает метрики коммерции."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return CommercialMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return CommercialMetricsResponse()

            try:
                metrics = simulation.get_commercial_metrics(step=step)
                if metrics is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Коммерческие метрики для шага {step} не найдены"
                    )
                    return CommercialMetricsResponse()

                proto_metrics = domain_commercial_metrics_obj_to_proto(metrics)
                return CommercialMetricsResponse(
                    metrics=proto_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting commercial metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении метрик: {str(e)}")
                return CommercialMetricsResponse()

    async def get_procurement_metrics(
        self, request: GetMetricsRequest, context
    ) -> ProcurementMetricsResponse:
        """Получает метрики закупок."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return ProcurementMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return ProcurementMetricsResponse()

            try:
                metrics = simulation.get_procurement_metrics(step=step)
                if metrics is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Метрики закупок для шага {step} не найдены")
                    return ProcurementMetricsResponse()

                proto_metrics = domain_procurement_metrics_obj_to_proto(metrics)
                return ProcurementMetricsResponse(
                    metrics=proto_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting procurement metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении метрик: {str(e)}")
                return ProcurementMetricsResponse()

    async def get_all_metrics(
        self, request: GetAllMetricsRequest, context
    ) -> AllMetricsResponse:
        """Получает все метрики."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return AllMetricsResponse()

            step = request.step
            if step == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Параметр step обязателен и должен быть больше 0")
                return AllMetricsResponse()

            try:
                factory_metrics_domain = simulation.get_factory_metrics(step=step)
                production_metrics_domain = simulation.get_production_metrics(step=step)
                quality_metrics_domain = simulation.get_quality_metrics(step=step)
                engineering_metrics_domain = simulation.get_engineering_metrics(
                    step=step
                )
                commercial_metrics_domain = simulation.get_commercial_metrics(step=step)
                procurement_metrics_domain = simulation.get_procurement_metrics(
                    step=step
                )

                if (
                    factory_metrics_domain is None
                    or production_metrics_domain is None
                    or quality_metrics_domain is None
                    or engineering_metrics_domain is None
                    or commercial_metrics_domain is None
                    or procurement_metrics_domain is None
                ):
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Метрики для шага {step} не найдены")
                    return AllMetricsResponse()

                factory_metrics = domain_factory_metrics_obj_to_proto(
                    factory_metrics_domain
                )
                production_metrics = domain_production_metrics_obj_to_proto(
                    production_metrics_domain
                )
                quality_metrics = domain_quality_metrics_obj_to_proto(
                    quality_metrics_domain
                )
                engineering_metrics = domain_engineering_metrics_obj_to_proto(
                    engineering_metrics_domain
                )
                commercial_metrics = domain_commercial_metrics_obj_to_proto(
                    commercial_metrics_domain
                )
                procurement_metrics = domain_procurement_metrics_obj_to_proto(
                    procurement_metrics_domain
                )

                return AllMetricsResponse(
                    factory=factory_metrics,
                    production=production_metrics,
                    quality=quality_metrics,
                    engineering=engineering_metrics,
                    commercial=commercial_metrics,
                    procurement=procurement_metrics,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting all metrics: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении всех метрик: {str(e)}")
                return AllMetricsResponse()

    # -----------------------------------------------------------------
    #          Методы получения данных для вкладок
    # -----------------------------------------------------------------

    async def get_production_schedule(
        self, request: GetProductionScheduleRequest, context
    ) -> ProductionScheduleResponse:
        """Получает производственное расписание."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return ProductionScheduleResponse()

            # Получаем последний step из parameters для получения актуального производственного плана
            if not simulation.parameters:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Параметры симуляции не найдены")
                return ProductionScheduleResponse()

            last_step = max(p.step for p in simulation.parameters)
            production_schedule = simulation.get_production_schedule(last_step)
            if production_schedule is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Производственный план не найден")
                return ProductionScheduleResponse()

            from application.proto_mappers import domain_production_schedule_to_proto

            proto_schedule = domain_production_schedule_to_proto(production_schedule)

            return ProductionScheduleResponse(
                schedule=proto_schedule,
                timestamp=datetime.now().isoformat(),
            )

    async def get_workshop_plan(
        self, request: GetWorkshopPlanRequest, context
    ) -> WorkshopPlanResponse:
        """Получает план цеха (возвращает processes)."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return WorkshopPlanResponse()

            # Получаем последний step из parameters для получения актуального плана цеха
            if not simulation.parameters:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Параметры симуляции не найдены")
                return WorkshopPlanResponse()

            last_step = max(p.step for p in simulation.parameters)
            workshop_plan = simulation.get_workshop_plan(last_step)
            if workshop_plan is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("План цеха не найден")
                return WorkshopPlanResponse()

            from application.proto_mappers import domain_process_graph_to_proto

            proto_workshop_plan = domain_process_graph_to_proto(workshop_plan)

            return WorkshopPlanResponse(
                workshop_plan=proto_workshop_plan,
                timestamp=datetime.now().isoformat(),
            )

    async def get_unplanned_repair(
        self, request: GetUnplannedRepairRequest, context
    ) -> UnplannedRepairResponse:
        """Получает данные о внеплановом ремонте."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return UnplannedRepairResponse()

            # Получаем данные о внеплановом ремонте через метод из Simulation
            # Получаем последний step из parameters
            if not simulation.parameters:
                return UnplannedRepairResponse(
                    unplanned_repair=None,
                    timestamp=datetime.now().isoformat(),
                )

            last_step = max(p.step for p in simulation.parameters)
            unplanned_repair_domain = simulation.get_unplanned_repair(last_step)

            # Если данных нет, возвращаем None
            if unplanned_repair_domain is None:
                return UnplannedRepairResponse(
                    unplanned_repair=None,
                    timestamp=datetime.now().isoformat(),
                )

            # Преобразуем доменный объект в proto (если маппер существует)
            # Пока возвращаем None, так как UnplannedRepair может не быть реализован
            return UnplannedRepairResponse(
                unplanned_repair=None,
                timestamp=datetime.now().isoformat(),
            )

    async def get_warehouse_load_chart(
        self, request: GetWarehouseLoadChartRequest, context
    ) -> WarehouseLoadChartResponse:
        """Получает график загрузки склада."""
        import random

        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return WarehouseLoadChartResponse()

            # Получаем график загрузки склада через метод из Simulation
            # Определяем тип склада из warehouse_id
            warehouse_type = (
                "materials"
                if request.warehouse_id.endswith("materials")
                else "products"
            )

            # Получаем последний step из parameters
            if not simulation.parameters:
                return WarehouseLoadChartResponse(
                    chart=None,
                    timestamp=datetime.now().isoformat(),
                )

            last_step = max(p.step for p in simulation.parameters)
            chart_data = simulation.get_warehouse_load_chart(warehouse_type, last_step)

            if not chart_data:
                return WarehouseLoadChartResponse(
                    chart=None,
                    timestamp=datetime.now().isoformat(),
                )

            # Преобразуем данные из домена в proto формат
            load_over_time = chart_data.get("load", [])
            max_capacity_over_time = chart_data.get("max_capacity", [])

            data_points = []
            for i, (load, max_cap) in enumerate(
                zip(load_over_time, max_capacity_over_time)
            ):
                data_points.append(
                    WarehouseLoadChart.LoadPoint(
                        timestamp=f"2024-01-{i+1:02d}",
                        load=load,
                        max_capacity=max_cap,
                    )
                )

            chart = WarehouseLoadChart(
                data_points=data_points, warehouse_id=request.warehouse_id
            )

            return WarehouseLoadChartResponse(
                chart=chart,
                timestamp=datetime.now().isoformat(),
            )

    async def get_required_materials(
        self, request: GetRequiredMaterialsRequest, context
    ) -> RequiredMaterialsResponse:
        """Получает список необходимых материалов."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return RequiredMaterialsResponse()

            # Получаем требуемые материалы через метод из SimulationParameters
            if not simulation.parameters:
                return RequiredMaterialsResponse(
                    materials=[],
                    timestamp=datetime.now().isoformat(),
                )

            params = max(simulation.parameters, key=lambda p: p.step)
            required_materials = params.get_required_materials()

            from application.proto_mappers import domain_required_material_to_proto

            proto_materials = [
                domain_required_material_to_proto(mat) for mat in required_materials
            ]

            return RequiredMaterialsResponse(
                materials=proto_materials,
                timestamp=datetime.now().isoformat(),
            )

    async def get_available_improvements(
        self, request: GetAvailableImprovementsRequest, context
    ) -> AvailableImprovementsResponse:
        """Получает доступные улучшения."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return AvailableImprovementsResponse()

            # Используем метод из SimulationParameters для получения доступных улучшений
            if not simulation.parameters:
                return AvailableImprovementsResponse(
                    improvements=[],
                    timestamp=datetime.now().isoformat(),
                )

            params = max(simulation.parameters, key=lambda p: p.step)
            improvement_names = params.get_available_improvements()

            # Преобразуем имена улучшений в proto LeanImprovement объекты
            # Берем полные объекты из production_improvements для преобразования
            from application.proto_mappers import domain_lean_improvement_to_proto

            proto_improvements = []
            improvement_names_set = set(improvement_names)
            for imp in params.production_improvements:
                if imp.name in improvement_names_set:
                    proto_improvements.append(domain_lean_improvement_to_proto(imp))

            return AvailableImprovementsResponse(
                improvements=proto_improvements,
                timestamp=datetime.now().isoformat(),
            )

    async def get_defect_policies(
        self, request: GetDefectPoliciesRequest, context
    ) -> DefectPoliciesResponse:
        """Получает политики работы с дефектами."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return DefectPoliciesResponse()

            # Используем метод из SimulationParameters для получения политик дефектов
            if not simulation.parameters:
                return DefectPoliciesResponse(
                    available_policies=[],
                    current_policy="",
                    timestamp=datetime.now().isoformat(),
                )

            params = max(simulation.parameters, key=lambda p: p.step)
            available_policies, current_policy = params.get_defect_policies()

            return DefectPoliciesResponse(
                available_policies=available_policies,
                current_policy=current_policy,
                timestamp=datetime.now().isoformat(),
            )

    # -----------------------------------------------------------------
    #          Валидация
    # -----------------------------------------------------------------

    async def validate_configuration(
        self, request: ValidateConfigurationRequest, context
    ) -> ValidationResponse:
        """Валидирует конфигурацию симуляции."""
        async with self.session_factory() as session:
            simulation = await self._load_simulation(
                session, request.simulation_id, context
            )
            if simulation is None:
                return ValidationResponse(
                    is_valid=False,
                    errors=[f"Симуляция с ID {request.simulation_id} не найдена"],
                    warnings=[],
                    timestamp=datetime.now().isoformat(),
                )

            try:
                result = simulation.validate_configuration()
                return ValidationResponse(
                    is_valid=result.get("is_valid", False),
                    errors=result.get("errors", []),
                    warnings=result.get("warnings", []),
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error validating configuration: {e}", exc_info=True)
                return ValidationResponse(
                    is_valid=False,
                    errors=[f"Ошибка при валидации: {str(e)}"],
                    warnings=[],
                    timestamp=datetime.now().isoformat(),
                )

    # -----------------------------------------------------------------
    #          Справочные данные
    # -----------------------------------------------------------------

    async def get_material_types(
        self, request: GetMaterialTypesRequest, context
    ) -> MaterialTypesResponse:
        """Получение типов материалов."""
        async with self.session_factory() as session:
            try:
                repo = SupplierRepository(session)
                material_types = await repo.get_distinct_product_names()
                return MaterialTypesResponse(
                    material_types=material_types,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting material types: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении типов материалов: {str(e)}")
                return MaterialTypesResponse(
                    material_types=[],
                    timestamp=datetime.now().isoformat(),
                )

    async def get_equipment_types(
        self, request: GetEquipmentTypesRequest, context
    ) -> EquipmentTypesResponse:
        """Получение типов оборудования."""
        async with self.session_factory() as session:
            try:
                repo = EquipmentRepository(session)
                equipment_types = await repo.get_distinct_equipment_types()
                return EquipmentTypesResponse(
                    equipment_types=equipment_types,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error getting equipment types: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(
                    f"Ошибка при получении типов оборудования: {str(e)}"
                )
                return EquipmentTypesResponse(
                    equipment_types=[],
                    timestamp=datetime.now().isoformat(),
                )

    async def get_workplace_types(
        self, request: GetWorkplaceTypesRequest, context
    ) -> WorkplaceTypesResponse:
        """Получение типов рабочих мест."""
        from domain.reference_data import WorkplaceType

        return WorkplaceTypesResponse(
            workplace_types=[wt.value for wt in WorkplaceType],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_defect_policies(
        self, request: GetAvailableDefectPoliciesRequest, context
    ) -> DefectPoliciesListResponse:
        """Получение доступных политик работы с браком."""
        from domain import DealingWithDefects

        policies = [
            policy.value
            for policy in DealingWithDefects
            if policy != DealingWithDefects.NONE
        ]
        return DefectPoliciesListResponse(
            policies=policies,
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_improvements_list(
        self, request: GetAvailableImprovementsListRequest, context
    ) -> ImprovementsListResponse:
        """Получение доступных LEAN улучшений."""
        from domain import ProductImpruvement

        improvements = [
            improvement.value
            for improvement in ProductImpruvement
            if improvement != ProductImpruvement.NONE
        ]
        return ImprovementsListResponse(
            improvements=improvements,
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_certifications(
        self, request: GetAvailableCertificationsRequest, context
    ) -> CertificationsListResponse:
        """Получение доступных сертификаций."""
        from domain.reference_data import Certification

        return CertificationsListResponse(
            certifications=[cert.value for cert in Certification],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_sales_strategies(
        self, request: GetAvailableSalesStrategiesRequest, context
    ) -> SalesStrategiesListResponse:
        """Получение доступных стратегий продаж."""
        from domain import SaleStrategest

        strategies = [
            strategy.value
            for strategy in SaleStrategest
            if strategy != SaleStrategest.NONE
        ]
        return SalesStrategiesListResponse(
            strategies=strategies,
            timestamp=datetime.now().isoformat(),
        )

    async def ping(self, request: PingRequest, context) -> SuccessResponse:
        """Проверка работоспособности сервиса."""
        return SuccessResponse(
            success=True,
            message="Simulation service is running",
            timestamp=datetime.now().isoformat(),
        )
