from typing import Dict, List, Optional
import uuid
from datetime import datetime
import grpc
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import logging

from grpc_generated.simulator_pb2 import (
    # Основные сообщения
    Supplier,
    Warehouse,
    Worker,
    Logist,
    Equipment,
    Workplace,
    Route,
    ProcessGraph,
    Consumer,
    Tender,
    LeanImprovement,
    Certification,
    # Ответы справочных данных
    MaterialTypesResponse,
    EquipmentTypesResponse,
    WorkplaceTypesResponse,
    DefectPoliciesListResponse,
    ImprovementsListResponse,
    CertificationsListResponse,
    SalesStrategiesListResponse,
    # Базовые ответы
    SuccessResponse,
    GetAllSuppliersResponse,
    GetAllWorkersResponse,
    GetAllLogistsResponse,
    GetAllWorkplacesResponse,
    GetAllConsumersResponse,
    GetAllTendersResponse,
    GetAllEquipmentResopnse,
    GetAllLeanImprovementsResponse,
    GetAvailableLeanImprovementsResponse,
    # Запросы справочных данных
    GetMaterialTypesRequest,
    GetEquipmentTypesRequest,
    GetWorkplaceTypesRequest,
    GetAvailableDefectPoliciesRequest,
    GetAvailableImprovementsListRequest,
    GetAvailableCertificationsRequest,
    GetAvailableSalesStrategiesRequest,
    GetAvailableLeanImprovementsRequest,
    CreateLeanImprovementRequest,
    UpdateLeanImprovementRequest,
    DeleteLeanImprovementRequest,
    GetAllLeanImprovementsRequest,
    # Базовые запросы
    CreateSupplierRequest,
    UpdateSupplierRequest,
    DeleteSupplierRequest,
    GetAllSuppliersRequest,
    GetWarehouseRequest,
    CreateWorkerRequest,
    UpdateWorkerRequest,
    DeleteWorkerRequest,
    GetAllWorkersRequest,
    CreateLogistRequest,
    UpdateLogistRequest,
    DeleteLogistRequest,
    GetAllLogistsRequest,
    CreateWorkplaceRequest,
    UpdateWorkplaceRequest,
    DeleteWorkplaceRequest,
    GetAllWorkplacesRequest,
    GetProcessGraphRequest,
    CreateConsumerRequest,
    UpdateConsumerRequest,
    DeleteConsumerRequest,
    GetAllConsumersRequest,
    CreateTenderRequest,
    UpdateTenderRequest,
    DeleteTenderRequest,
    GetAllTendersRequest,
    CreateEquipmentRequest,
    UpdateEquipmentRequest,
    DeleteEquipmentRequest,
    GetAllEquipmentRequest,
    PingRequest,
)
from grpc_generated.simulator_pb2_grpc import SimulationDatabaseManagerServicer
from application.proto_mappers import domain_process_graph_to_proto
from infrastructure.repositories import (
    SimulationRepository,
    SupplierRepository,
    WorkerRepository,
    EquipmentRepository,
    WorkplaceRepository,
    ConsumerRepository,
    TenderRepository,
    LeanImprovementRepository,
)
from .proto_mappers import (
    domain_supplier_to_proto,
    proto_supplier_to_domain,
    domain_worker_to_proto,
    proto_worker_to_domain,
    domain_equipment_to_proto,
    proto_equipment_to_domain,
    domain_workplace_to_proto,
    proto_workplace_to_domain,
    domain_consumer_to_proto,
    proto_consumer_to_domain,
    domain_tender_to_proto,
    proto_tender_to_domain,
    domain_lean_improvement_to_proto,
    proto_lean_improvement_to_domain,
)
from domain import (
    Qualification,
    ConsumerType,
    SimulationParameters,
    Specialization,
    VehicleType,
    PaymentForm,
    SaleStrategest,
    DealingWithDefects,
    ProductImpruvement,
)
from domain.reference_data import (
    Certification,
    WorkplaceType,
)

logger = logging.getLogger(__name__)


class SimulationDatabaseManagerImpl(SimulationDatabaseManagerServicer):
    """Сервис управления базой данных симуляции с использованием DI паттерна."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """
        Args:
            session_factory: Фабрика для создания асинхронных сессий SQLAlchemy
        """
        self.session_factory = session_factory

    # -----------------------------------------------------------------
    #          Методы для поставщиков
    # -----------------------------------------------------------------

    async def create_supplier(
        self, request: CreateSupplierRequest, context
    ) -> Supplier:
        """Создает нового поставщика."""
        async with self.session_factory() as session:
            try:
                # Преобразуем proto запрос в доменную сущность
                domain_supplier = proto_supplier_to_domain(
                    Supplier(
                        supplier_id="",  # Будет создан в репозитории
                        name=request.name,
                        product_name=request.product_name,
                        material_type=request.material_type,
                        delivery_period=request.delivery_period,
                        special_delivery_period=request.special_delivery_period,
                        reliability=request.reliability,
                        product_quality=request.product_quality,
                        cost=request.cost,
                        special_delivery_cost=request.special_delivery_cost,
                    )
                )

                # Сохраняем через репозиторий
                repo = SupplierRepository(session)
                saved_supplier = await repo.save(domain_supplier)

                if saved_supplier is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании поставщика")
                    return Supplier()

                # Преобразуем в proto и возвращаем
                return domain_supplier_to_proto(saved_supplier)
            except Exception as e:
                logger.error(f"Error creating supplier: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании поставщика: {str(e)}")
                return Supplier()

    async def update_supplier(
        self, request: UpdateSupplierRequest, context
    ) -> Supplier:
        """Обновляет существующего поставщика."""
        async with self.session_factory() as session:
            try:
                repo = SupplierRepository(session)
                existing_supplier = await repo.get(request.supplier_id)

                if existing_supplier is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Поставщик с ID {request.supplier_id} не найден"
                    )
                    return Supplier()

                # Преобразуем существующего поставщика в proto для обновления
                existing_proto = domain_supplier_to_proto(existing_supplier)

                # Обновляем поля в proto объекте
                if request.name:
                    existing_proto.name = request.name
                if request.product_name:
                    existing_proto.product_name = request.product_name
                if request.material_type:
                    existing_proto.material_type = request.material_type
                if request.delivery_period:
                    existing_proto.delivery_period = request.delivery_period
                if request.special_delivery_period:
                    existing_proto.special_delivery_period = (
                        request.special_delivery_period
                    )
                if request.reliability:
                    existing_proto.reliability = request.reliability
                if request.product_quality:
                    existing_proto.product_quality = request.product_quality
                if request.cost:
                    existing_proto.cost = request.cost
                if request.special_delivery_cost:
                    existing_proto.special_delivery_cost = request.special_delivery_cost

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_supplier_to_domain(existing_proto)
                updated_supplier = await repo.save(updated_domain)

                if updated_supplier is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении поставщика")
                    return Supplier()

                return domain_supplier_to_proto(updated_supplier)
            except Exception as e:
                logger.error(f"Error updating supplier: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении поставщика: {str(e)}")
                return Supplier()

    async def delete_supplier(
        self, request: DeleteSupplierRequest, context
    ) -> SuccessResponse:
        """Удаляет поставщика."""
        async with self.session_factory() as session:
            try:
                repo = SupplierRepository(session)
                deleted_supplier = await repo.delete(request.supplier_id)

                if deleted_supplier is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Поставщик с ID {request.supplier_id} не найден",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Поставщик {request.supplier_id} успешно удален",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting supplier: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении поставщика: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_suppliers(
        self, request: GetAllSuppliersRequest, context
    ) -> GetAllSuppliersResponse:
        """Получает всех поставщиков."""
        async with self.session_factory() as session:
            try:
                repo = SupplierRepository(session)
                domain_suppliers = await repo.get_all()

                proto_suppliers = [
                    domain_supplier_to_proto(s) for s in domain_suppliers
                ]

                return GetAllSuppliersResponse(
                    suppliers=proto_suppliers,
                    total_count=len(proto_suppliers),
                )
            except Exception as e:
                logger.error(f"Error getting all suppliers: {e}", exc_info=True)
                return GetAllSuppliersResponse(
                    suppliers=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для складов
    # -----------------------------------------------------------------

    async def get_warehouse(self, request: GetWarehouseRequest, context) -> Warehouse:
        # Возвращаем тестовый склад
        return Warehouse(
            warehouse_id=request.warehouse_id,
            inventory_worker=Worker(
                worker_id="worker_warehouse_001",
                name="Сидоров Сидор Сидорович",
                qualification=Qualification.III.value,  # int в proto
                specialty=Specialization.WAREHOUSE_KEEPER.value,  # string в proto
                salary=45000,
            ),
            size=800,
            loading=320,
            materials={
                "Металл": 150,
                "Пластик": 100,
                "Электроника": 70,
                "Крепеж": 200,
            },
        )

    # -----------------------------------------------------------------
    #          Методы для рабочих
    # -----------------------------------------------------------------

    async def create_worker(self, request: CreateWorkerRequest, context) -> Worker:
        """Создает нового работника."""
        async with self.session_factory() as session:
            try:
                # Преобразуем proto запрос в доменную сущность
                domain_worker = proto_worker_to_domain(
                    Worker(
                        worker_id="",
                        name=request.name,
                        qualification=request.qualification,
                        specialty=request.specialty,
                        salary=request.salary,
                    )
                )

                repo = WorkerRepository(session)
                saved_worker = await repo.save(domain_worker)

                if saved_worker is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании работника")
                    return Worker()

                return domain_worker_to_proto(saved_worker)
            except Exception as e:
                logger.error(f"Error creating worker: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании работника: {str(e)}")
                return Worker()

    async def update_worker(self, request: UpdateWorkerRequest, context) -> Worker:
        """Обновляет существующего работника."""
        async with self.session_factory() as session:
            try:
                repo = WorkerRepository(session)
                existing_worker = await repo.get(request.worker_id)

                if existing_worker is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Рабочий с ID {request.worker_id} не найден")
                    return Worker()

                # Преобразуем существующего работника в proto для обновления
                existing_proto = domain_worker_to_proto(existing_worker)

                # Обновляем поля в proto объекте
                if request.name:
                    existing_proto.name = request.name
                if request.qualification:
                    existing_proto.qualification = request.qualification
                if request.specialty:
                    existing_proto.specialty = request.specialty
                if request.salary:
                    existing_proto.salary = request.salary

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_worker_to_domain(existing_proto)
                updated_worker = await repo.save(updated_domain)

                if updated_worker is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении работника")
                    return Worker()

                return domain_worker_to_proto(updated_worker)
            except Exception as e:
                logger.error(f"Error updating worker: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении работника: {str(e)}")
                return Worker()

    async def delete_worker(
        self, request: DeleteWorkerRequest, context
    ) -> SuccessResponse:
        """Удаляет работника."""
        async with self.session_factory() as session:
            try:
                repo = WorkerRepository(session)
                deleted_worker = await repo.delete(request.worker_id)

                if deleted_worker is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Рабочий с ID {request.worker_id} не найден",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Рабочий {request.worker_id} успешно удален",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting worker: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении работника: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_workers(
        self, request: GetAllWorkersRequest, context
    ) -> GetAllWorkersResponse:
        """Получает всех работников (исключая логистов)."""
        async with self.session_factory() as session:
            try:
                repo = WorkerRepository(session)
                # Фильтруем только работников с type="worker"
                domain_workers = await repo.get_all(worker_type="worker")

                proto_workers = [domain_worker_to_proto(w) for w in domain_workers]

                return GetAllWorkersResponse(
                    workers=proto_workers,
                    total_count=len(proto_workers),
                )
            except Exception as e:
                logger.error(f"Error getting all workers: {e}", exc_info=True)
                return GetAllWorkersResponse(
                    workers=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для логистов
    # -----------------------------------------------------------------
    # Примечание: Logist наследуется от Worker, поэтому используем WorkerRepository
    # и преобразуем Worker в Logist при необходимости

    async def create_logist(self, request: CreateLogistRequest, context) -> Logist:
        """Создает нового логиста (используется как Worker)."""
        # Логист хранится как Worker, но с дополнительными полями
        # Для упрощения используем Worker, но можно расширить при необходимости
        async with self.session_factory() as session:
            try:
                from domain import Logist as DomainLogist

                domain_logist = proto_worker_to_domain(
                    Worker(
                        worker_id="",
                        name=request.name,
                        qualification=request.qualification,
                        specialty=request.specialty,
                        salary=request.salary,
                    )
                )
                # Валидация speed: максимальное значение для int32 в PostgreSQL
                MAX_SPEED = 2147483647  # Максимальное значение int32
                speed = request.speed
                if speed > MAX_SPEED:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(
                        f"Значение speed ({speed}) превышает максимально допустимое ({MAX_SPEED})"
                    )
                    return Logist()

                # vehicle_type теперь строка в домене
                vehicle_type_str = request.vehicle_type or ""

                # Убеждаемся, что qualification - int
                qualification_int = (
                    domain_logist.qualification.value
                    if hasattr(domain_logist.qualification, "value")
                    else domain_logist.qualification
                )

                logist = DomainLogist(
                    worker_id=domain_logist.worker_id,
                    name=domain_logist.name,
                    qualification=qualification_int,  # int в домене
                    specialty=domain_logist.specialty,  # в домене это specialty, не specialization
                    salary=domain_logist.salary,
                    speed=speed,
                    vehicle_type=vehicle_type_str,  # строка в домене
                )

                logger.debug(
                    f"Creating logist: name={logist.name}, speed={logist.speed}, "
                    f"vehicle_type={logist.vehicle_type}, type={type(logist).__name__}"
                )

                repo = WorkerRepository(session)
                # Сохраняем как Worker (логист наследуется от Worker)
                saved_entity = await repo.save(logist)

                logger.debug(
                    f"Saved logist entity: type={type(saved_entity).__name__}, "
                    f"worker_id={saved_entity.worker_id if saved_entity else None}"
                )

                if saved_entity is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании логиста")
                    return Logist()

                # Проверяем, что логист действительно сохранился в БД
                # Используем новую сессию для проверки (имитируем следующий запрос)
                if saved_entity.worker_id:
                    verify_worker = await repo.get(saved_entity.worker_id)
                    if verify_worker is None:
                        logger.warning(
                            f"Logist {saved_entity.worker_id} was saved but not found immediately after"
                        )

                # Репозиторий должен вернуть Logist, если type="logist" в БД
                # Если вернулся Worker, преобразуем в Logist
                if not isinstance(saved_entity, DomainLogist):
                    # Преобразуем Worker в Logist, используя данные из оригинального logist
                    # Убеждаемся, что qualification - int
                    qualification_int = (
                        saved_entity.qualification.value
                        if hasattr(saved_entity.qualification, "value")
                        else saved_entity.qualification
                    )
                    saved_logist = DomainLogist(
                        worker_id=saved_entity.worker_id,
                        name=saved_entity.name,
                        qualification=qualification_int,  # int в домене
                        specialty=saved_entity.specialty,
                        salary=saved_entity.salary,
                        speed=logist.speed,
                        vehicle_type=logist.vehicle_type,
                    )
                else:
                    saved_logist = saved_entity

                # Преобразуем в proto
                from .proto_mappers import domain_logist_to_proto

                return domain_logist_to_proto(saved_logist)
            except Exception as e:
                logger.error(f"Error creating logist: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании логиста: {str(e)}")
                return Logist()

    async def update_logist(self, request: UpdateLogistRequest, context) -> Logist:
        """Обновляет логиста."""
        async with self.session_factory() as session:
            try:
                from domain import Logist as DomainLogist

                repo = WorkerRepository(session)
                # Получаем через репозиторий
                existing_worker = await repo.get(request.worker_id)

                if existing_worker is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Логист с ID {request.worker_id} не найден")
                    return Logist()

                # Проверяем, что это действительно логист
                if not isinstance(existing_worker, DomainLogist):
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details(
                        f"Работник с ID {request.worker_id} не является логистом"
                    )
                    return Logist()

                # Используем существующую доменную сущность
                logist = existing_worker

                # Обновляем поля
                if request.name:
                    logist.name = request.name
                if request.qualification:
                    # qualification теперь int в домене, не enum
                    logist.qualification = request.qualification
                if request.specialty:
                    logist.specialty = request.specialty  # в домене это specialty
                if request.salary:
                    logist.salary = request.salary
                if request.speed is not None:
                    # Валидация speed: максимальное значение для int32 в PostgreSQL
                    MAX_SPEED = 2147483647  # Максимальное значение int32
                    if request.speed > MAX_SPEED:
                        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                        context.set_details(
                            f"Значение speed ({request.speed}) превышает максимально допустимое ({MAX_SPEED})"
                        )
                        return Logist()
                    logist.speed = request.speed
                if request.vehicle_type:
                    # vehicle_type теперь строка в домене
                    logist.vehicle_type = request.vehicle_type

                # Сохраняем изменения
                updated_entity = await repo.save(logist)

                if updated_entity is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении логиста")
                    return Logist()

                # Репозиторий должен вернуть Logist, если type="logist" в БД
                # Если вернулся Worker, преобразуем в Logist
                if not isinstance(updated_entity, DomainLogist):
                    # Убеждаемся, что qualification - int
                    qualification_int = (
                        updated_entity.qualification.value
                        if hasattr(updated_entity.qualification, "value")
                        else updated_entity.qualification
                    )
                    updated_logist = DomainLogist(
                        worker_id=updated_entity.worker_id,
                        name=updated_entity.name,
                        qualification=qualification_int,  # int в домене
                        specialty=updated_entity.specialty,  # в домене это specialty
                        salary=updated_entity.salary,
                        speed=logist.speed,
                        vehicle_type=logist.vehicle_type,  # строка в домене
                    )
                else:
                    # Убеждаемся, что qualification - int (может прийти как enum из репозитория)
                    if hasattr(updated_entity.qualification, "value"):
                        updated_entity.qualification = (
                            updated_entity.qualification.value
                        )
                    updated_logist = updated_entity

                from .proto_mappers import domain_logist_to_proto

                return domain_logist_to_proto(updated_logist)
            except Exception as e:
                logger.error(f"Error updating logist: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении логиста: {str(e)}")
                return Logist()

    async def delete_logist(
        self, request: DeleteLogistRequest, context
    ) -> SuccessResponse:
        """Удаляет логиста."""
        async with self.session_factory() as session:
            try:
                repo = WorkerRepository(session)
                deleted_worker = await repo.delete(request.worker_id)

                if deleted_worker is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Логист с ID {request.worker_id} не найден",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Логист {request.worker_id} успешно удален",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting logist: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении логиста: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_logists(
        self, request: GetAllLogistsRequest, context
    ) -> GetAllLogistsResponse:
        """Получает всех логистов."""
        async with self.session_factory() as session:
            try:
                from .proto_mappers import domain_logist_to_proto

                # Используем репозиторий для получения логистов
                repo = WorkerRepository(session)
                domain_logists = await repo.get_all(worker_type="logist")

                logger.debug(
                    f"Found {len(domain_logists)} logists in database using repository"
                )

                # Преобразуем в proto сообщения
                proto_logists = [
                    domain_logist_to_proto(logist) for logist in domain_logists
                ]

                logger.debug(f"Returning {len(proto_logists)} logists")
                return GetAllLogistsResponse(
                    logists=proto_logists,
                    total_count=len(proto_logists),
                )
            except Exception as e:
                logger.error(f"Error getting all logists: {e}", exc_info=True)
                return GetAllLogistsResponse(
                    logists=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для рабочих мест
    # -----------------------------------------------------------------

    async def create_workplace(
        self, request: CreateWorkplaceRequest, context
    ) -> Workplace:
        """Создает новое рабочее место."""
        async with self.session_factory() as session:
            try:
                # CreateWorkplaceRequest не содержит worker_id и equipment_id
                # Рабочее место создается без привязки к worker/equipment
                # Эти поля устанавливаются только во время симуляции

                # Создаем временный proto объект из request для использования маппера
                workplace_proto = Workplace(
                    workplace_id="",
                    workplace_name=request.workplace_name,
                    required_speciality=request.required_speciality,
                    required_qualification=request.required_qualification,
                    required_equipment=request.required_equipment or "",
                    required_stages=request.required_stages,
                )

                # Преобразуем proto в доменную сущность через маппер
                domain_workplace = proto_workplace_to_domain(workplace_proto)

                repo = WorkplaceRepository(session)
                saved_workplace = await repo.save(domain_workplace)

                if saved_workplace is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании рабочего места")
                    return Workplace()

                return domain_workplace_to_proto(saved_workplace)
            except Exception as e:
                logger.error(f"Error creating workplace: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании рабочего места: {str(e)}")
                return Workplace()

    async def update_workplace(
        self, request: UpdateWorkplaceRequest, context
    ) -> Workplace:
        """Обновляет рабочее место."""
        async with self.session_factory() as session:
            try:
                repo = WorkplaceRepository(session)
                existing_workplace = await repo.get(request.workplace_id)

                if existing_workplace is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Рабочее место с ID {request.workplace_id} не найдено"
                    )
                    return Workplace()

                # Преобразуем существующее рабочее место в proto для обновления
                existing_proto = domain_workplace_to_proto(existing_workplace)

                # Обновляем поля в proto объекте
                if request.workplace_name:
                    existing_proto.workplace_name = request.workplace_name
                if request.required_speciality:
                    existing_proto.required_speciality = request.required_speciality
                if request.required_qualification:
                    existing_proto.required_qualification = (
                        request.required_qualification
                    )
                if request.required_equipment:
                    existing_proto.required_equipment = request.required_equipment
                if request.required_stages:
                    existing_proto.required_stages[:] = request.required_stages

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_workplace_to_domain(existing_proto)

                updated_workplace = await repo.save(updated_domain)

                if updated_workplace is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении рабочего места")
                    return Workplace()

                return domain_workplace_to_proto(updated_workplace)
            except Exception as e:
                logger.error(f"Error updating workplace: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении рабочего места: {str(e)}")
                return Workplace()

    async def delete_workplace(
        self, request: DeleteWorkplaceRequest, context
    ) -> SuccessResponse:
        """Удаляет рабочее место."""
        async with self.session_factory() as session:
            try:
                repo = WorkplaceRepository(session)
                deleted_workplace = await repo.delete(request.workplace_id)

                if deleted_workplace is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Рабочее место с ID {request.workplace_id} не найдено",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Рабочее место {request.workplace_id} успешно удалено",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting workplace: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении рабочего места: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_workplaces(
        self, request: GetAllWorkplacesRequest, context
    ) -> GetAllWorkplacesResponse:
        """Получает все рабочие места."""
        async with self.session_factory() as session:
            try:
                repo = WorkplaceRepository(session)
                domain_workplaces = await repo.get_all()

                proto_workplaces = [
                    domain_workplace_to_proto(w) for w in domain_workplaces
                ]

                return GetAllWorkplacesResponse(
                    workplaces=proto_workplaces,
                    total_count=len(proto_workplaces),
                )
            except Exception as e:
                logger.error(f"Error getting all workplaces: {e}", exc_info=True)
                return GetAllWorkplacesResponse(
                    workplaces=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для карты процесса
    # -----------------------------------------------------------------

    async def get_process_graph(
        self, request: GetProcessGraphRequest, context
    ) -> ProcessGraph:
        """Получает граф процесса из рабочих мест в БД."""
        async with self.session_factory() as session:
            try:
                # Получаем все рабочие места из БД
                repo = SimulationRepository(session)
                simulation = await repo.get(request.simulation_id)
                if simulation is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Симуляция с ID {request.simulation_id} не найдена"
                    )
                    return domain_process_graph_to_proto(ProcessGraph())

                for parameter in simulation.parameters:
                    if parameter.step == request.step:
                        return domain_process_graph_to_proto(parameter.processes)

            except Exception as e:
                logger.error(f"Error getting process graph: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при получении графа процесса: {str(e)}")
                return domain_process_graph_to_proto(
                    ProcessGraph(
                        process_graph_id=request.process_graph_id,
                        workplaces=[],
                        routes=[],
                    )
                )

    # -----------------------------------------------------------------
    #          Методы для заказчиков
    # -----------------------------------------------------------------

    async def create_consumer(
        self, request: CreateConsumerRequest, context
    ) -> Consumer:
        """Создает нового заказчика."""
        async with self.session_factory() as session:
            try:
                domain_consumer = proto_consumer_to_domain(
                    Consumer(
                        consumer_id="",
                        name=request.name,
                        type=request.type,
                    )
                )

                repo = ConsumerRepository(session)
                saved_consumer = await repo.save(domain_consumer)

                if saved_consumer is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании заказчика")
                    return Consumer()

                return domain_consumer_to_proto(saved_consumer)
            except Exception as e:
                logger.error(f"Error creating consumer: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании заказчика: {str(e)}")
                return Consumer()

    async def update_consumer(
        self, request: UpdateConsumerRequest, context
    ) -> Consumer:
        """Обновляет заказчика."""
        async with self.session_factory() as session:
            try:
                repo = ConsumerRepository(session)
                existing_consumer = await repo.get(request.consumer_id)

                if existing_consumer is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Заказчик с ID {request.consumer_id} не найден"
                    )
                    return Consumer()

                # Преобразуем существующего заказчика в proto для обновления
                existing_proto = domain_consumer_to_proto(existing_consumer)

                # Обновляем поля в proto объекте
                if request.name:
                    existing_proto.name = request.name
                if request.type:
                    existing_proto.type = request.type

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_consumer_to_domain(existing_proto)
                updated_consumer = await repo.save(updated_domain)

                if updated_consumer is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении заказчика")
                    return Consumer()

                return domain_consumer_to_proto(updated_consumer)
            except Exception as e:
                logger.error(f"Error updating consumer: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении заказчика: {str(e)}")
                return Consumer()

    async def delete_consumer(
        self, request: DeleteConsumerRequest, context
    ) -> SuccessResponse:
        """Удаляет заказчика."""
        async with self.session_factory() as session:
            try:
                repo = ConsumerRepository(session)
                deleted_consumer = await repo.delete(request.consumer_id)

                if deleted_consumer is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Заказчик с ID {request.consumer_id} не найден",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Заказчик {request.consumer_id} успешно удален",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting consumer: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении заказчика: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_consumers(
        self, request: GetAllConsumersRequest, context
    ) -> GetAllConsumersResponse:
        """Получает всех заказчиков."""
        async with self.session_factory() as session:
            try:
                repo = ConsumerRepository(session)
                domain_consumers = await repo.get_all()

                proto_consumers = [
                    domain_consumer_to_proto(c) for c in domain_consumers
                ]

                return GetAllConsumersResponse(
                    consumers=proto_consumers,
                    total_count=len(proto_consumers),
                )
            except Exception as e:
                logger.error(f"Error getting all consumers: {e}", exc_info=True)
                return GetAllConsumersResponse(
                    consumers=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для тендеров
    # -----------------------------------------------------------------

    async def create_tender(self, request: CreateTenderRequest, context) -> Tender:
        """Создает новый тендер."""
        async with self.session_factory() as session:
            try:
                # Получаем заказчика
                consumer_repo = ConsumerRepository(session)
                consumer = await consumer_repo.get(request.consumer_id)

                if consumer is None:
                    # Создаем временного заказчика, если не найден
                    consumer = await consumer_repo.save(
                        proto_consumer_to_domain(
                            Consumer(
                                consumer_id=request.consumer_id,
                                name="Временный заказчик",
                                type=ConsumerType.NOT_GOVERMANT.value,  # string в proto
                            )
                        )
                    )

                # Создаем временный proto объект из request для использования маппера
                tender_proto = Tender(
                    tender_id="",
                    consumer=domain_consumer_to_proto(consumer),
                    cost=request.cost,
                    quantity_of_products=request.quantity_of_products,
                    penalty_per_day=(
                        request.penalty_per_day if request.penalty_per_day else 0
                    ),
                    warranty_years=(
                        request.warranty_years if request.warranty_years else 0
                    ),
                    payment_form=request.payment_form if request.payment_form else "",
                )

                # Преобразуем proto в доменную сущность через маппер
                domain_tender = proto_tender_to_domain(tender_proto)

                repo = TenderRepository(session)
                saved_tender = await repo.save(domain_tender)

                if saved_tender is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании тендера")
                    return Tender()

                return domain_tender_to_proto(saved_tender)
            except Exception as e:
                logger.error(f"Error creating tender: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании тендера: {str(e)}")
                return Tender()

    async def update_tender(self, request: UpdateTenderRequest, context) -> Tender:
        """Обновляет тендер."""
        async with self.session_factory() as session:
            try:
                repo = TenderRepository(session)
                existing_tender = await repo.get(request.tender_id)

                if existing_tender is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(f"Тендер с ID {request.tender_id} не найден")
                    return Tender()

                # Преобразуем существующий тендер в proto для обновления
                existing_proto = domain_tender_to_proto(existing_tender)

                # Обновляем поля в proto объекте
                if request.consumer_id:
                    consumer_repo = ConsumerRepository(session)
                    consumer = await consumer_repo.get(request.consumer_id)
                    if consumer:
                        existing_proto.consumer.CopyFrom(
                            domain_consumer_to_proto(consumer)
                        )

                if request.cost:
                    existing_proto.cost = request.cost
                if request.quantity_of_products:
                    existing_proto.quantity_of_products = request.quantity_of_products
                if request.penalty_per_day:
                    existing_proto.penalty_per_day = request.penalty_per_day
                if request.warranty_years:
                    existing_proto.warranty_years = request.warranty_years
                if request.payment_form:
                    existing_proto.payment_form = request.payment_form

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_tender_to_domain(existing_proto)
                updated_tender = await repo.save(updated_domain)

                if updated_tender is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении тендера")
                    return Tender()

                return domain_tender_to_proto(updated_tender)
            except Exception as e:
                logger.error(f"Error updating tender: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении тендера: {str(e)}")
                return Tender()

    async def delete_tender(
        self, request: DeleteTenderRequest, context
    ) -> SuccessResponse:
        """Удаляет тендер."""
        async with self.session_factory() as session:
            try:
                repo = TenderRepository(session)
                deleted_tender = await repo.delete(request.tender_id)

                if deleted_tender is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Тендер с ID {request.tender_id} не найден",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Тендер {request.tender_id} успешно удален",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting tender: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении тендера: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_tenders(
        self, request: GetAllTendersRequest, context
    ) -> GetAllTendersResponse:
        """Получает все тендеры."""
        async with self.session_factory() as session:
            try:
                repo = TenderRepository(session)
                domain_tenders = await repo.get_all()

                proto_tenders = [domain_tender_to_proto(t) for t in domain_tenders]

                return GetAllTendersResponse(
                    tenders=proto_tenders,
                    total_count=len(proto_tenders),
                )
            except Exception as e:
                logger.error(f"Error getting all tenders: {e}", exc_info=True)
                return GetAllTendersResponse(
                    tenders=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для оборудования
    # -----------------------------------------------------------------

    async def create_equipment(
        self, request: CreateEquipmentRequest, context
    ) -> Equipment:
        """Создает новое оборудование."""
        async with self.session_factory() as session:
            try:
                domain_equipment = proto_equipment_to_domain(
                    Equipment(
                        equipment_id="",
                        name=request.name,
                        equipment_type=request.equipment_type,
                        reliability=request.reliability,
                        maintenance_period=(
                            request.maintenance_period
                            if request.maintenance_period
                            else None
                        ),
                        maintenance_cost=request.maintenance_cost,
                        cost=request.cost,
                        repair_cost=request.repair_cost,
                        repair_time=request.repair_time,
                    )
                )

                repo = EquipmentRepository(session)
                saved_equipment = await repo.save(domain_equipment)

                if saved_equipment is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании оборудования")
                    return Equipment()

                return domain_equipment_to_proto(saved_equipment)
            except Exception as e:
                logger.error(f"Error creating equipment: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании оборудования: {str(e)}")
                return Equipment()

    async def update_equipment(
        self, request: UpdateEquipmentRequest, context
    ) -> Equipment:
        """Обновляет оборудование."""
        async with self.session_factory() as session:
            try:
                repo = EquipmentRepository(session)
                existing_equipment = await repo.get(request.equipment_id)

                if existing_equipment is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"Оборудование с ID {request.equipment_id} не найдено"
                    )
                    return Equipment()

                # Преобразуем существующее оборудование в proto для обновления
                existing_proto = domain_equipment_to_proto(existing_equipment)

                # Обновляем поля в proto объекте
                if request.name:
                    existing_proto.name = request.name
                if request.equipment_type:
                    existing_proto.equipment_type = request.equipment_type
                if request.reliability:
                    existing_proto.reliability = request.reliability
                if request.maintenance_period:
                    existing_proto.maintenance_period = request.maintenance_period
                if request.maintenance_cost:
                    existing_proto.maintenance_cost = request.maintenance_cost
                if request.cost:
                    existing_proto.cost = request.cost
                if request.repair_cost:
                    existing_proto.repair_cost = request.repair_cost
                if request.repair_time:
                    existing_proto.repair_time = request.repair_time

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_equipment_to_domain(existing_proto)
                updated_equipment = await repo.save(updated_domain)

                if updated_equipment is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении оборудования")
                    return Equipment()

                return domain_equipment_to_proto(updated_equipment)
            except Exception as e:
                logger.error(f"Error updating equipment: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении оборудования: {str(e)}")
                return Equipment()

    async def delete_equipment(
        self, request: DeleteEquipmentRequest, context
    ) -> SuccessResponse:
        """Удаляет оборудование."""
        async with self.session_factory() as session:
            try:
                repo = EquipmentRepository(session)
                deleted_equipment = await repo.delete(request.equipment_id)

                if deleted_equipment is None:
                    return SuccessResponse(
                        success=False,
                        message=f"Оборудование с ID {request.equipment_id} не найдено",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"Оборудование {request.equipment_id} успешно удалено",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting equipment: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении оборудования: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_equipment(
        self, request: GetAllEquipmentRequest, context
    ) -> GetAllEquipmentResopnse:
        """Получает все оборудование."""
        async with self.session_factory() as session:
            try:
                repo = EquipmentRepository(session)
                domain_equipments = await repo.get_all()

                proto_equipments = [
                    domain_equipment_to_proto(e) for e in domain_equipments
                ]

                return GetAllEquipmentResopnse(
                    equipments=proto_equipments,
                    total_count=len(proto_equipments),
                )
            except Exception as e:
                logger.error(f"Error getting all equipment: {e}", exc_info=True)
                return GetAllEquipmentResopnse(
                    equipments=[],
                    total_count=0,
                )

    # -----------------------------------------------------------------
    #          Методы для справочных данных
    # -----------------------------------------------------------------

    async def get_available_material_types(
        self, request: GetMaterialTypesRequest, context
    ) -> MaterialTypesResponse:
        """Получение типов материалов - возвращает уникальные имена товаров из Supplier.product_name."""
        async with self.session_factory() as session:
            try:
                # Используем репозиторий для получения уникальных значений
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

    async def get_available_equipment_types(
        self, request: GetEquipmentTypesRequest, context
    ) -> EquipmentTypesResponse:
        """Получение типов оборудования - возвращает уникальные типы из Equipment.equipment_type."""
        async with self.session_factory() as session:
            try:
                # Используем репозиторий для получения уникальных значений
                repo = EquipmentRepository(session)
                equipment_types_list = await repo.get_distinct_equipment_types()

                return EquipmentTypesResponse(
                    equipment_types=equipment_types_list,
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

    async def get_available_workplace_types(
        self, request: GetWorkplaceTypesRequest, context
    ) -> WorkplaceTypesResponse:
        """Получение типов рабочих мест."""
        return WorkplaceTypesResponse(
            workplace_types=[wt.value for wt in WorkplaceType],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_defect_policies(
        self, request: GetAvailableDefectPoliciesRequest, context
    ) -> DefectPoliciesListResponse:
        """Получение доступных политик работы с браком."""
        # Исключаем NONE из списка
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
        # Исключаем NONE из списка
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
        return CertificationsListResponse(
            certifications=[cert.value for cert in Certification],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_sales_strategies(
        self, request: GetAvailableSalesStrategiesRequest, context
    ) -> SalesStrategiesListResponse:
        """Получение доступных стратегий продаж."""
        # Исключаем NONE из списка
        strategies = [
            strategy.value
            for strategy in SaleStrategest
            if strategy != SaleStrategest.NONE
        ]
        return SalesStrategiesListResponse(
            strategies=strategies,
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_lean_improvements(
        self, request: GetAvailableLeanImprovementsRequest, context
    ) -> GetAvailableLeanImprovementsResponse:
        """Получение доступных LEAN улучшений из БД."""
        async with self.session_factory() as session:
            try:
                repo = LeanImprovementRepository(session)
                domain_improvements = await repo.get_all()

                proto_improvements = [
                    domain_lean_improvement_to_proto(imp) for imp in domain_improvements
                ]

                return GetAvailableLeanImprovementsResponse(
                    improvements=proto_improvements,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(
                    f"Error getting available lean improvements: {e}", exc_info=True
                )
                return GetAvailableLeanImprovementsResponse(
                    improvements=[],
                    timestamp=datetime.now().isoformat(),
                )

    # -----------------------------------------------------------------
    #          Методы для LEAN улучшений (CRUD)
    # -----------------------------------------------------------------

    async def create_lean_improvement(
        self, request: CreateLeanImprovementRequest, context
    ) -> LeanImprovement:
        """Создает новое LEAN улучшение."""
        async with self.session_factory() as session:
            try:
                # Преобразуем proto запрос в доменную сущность
                domain_improvement = proto_lean_improvement_to_domain(
                    LeanImprovement(
                        improvement_id="",
                        name=request.name,
                        is_implemented=request.is_implemented,
                        implementation_cost=request.implementation_cost,
                        efficiency_gain=request.efficiency_gain,
                    )
                )

                repo = LeanImprovementRepository(session)
                saved_improvement = await repo.save(domain_improvement)

                if saved_improvement is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при создании LEAN улучшения")
                    return LeanImprovement()

                return domain_lean_improvement_to_proto(saved_improvement)
            except Exception as e:
                logger.error(f"Error creating lean improvement: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при создании LEAN улучшения: {str(e)}")
                return LeanImprovement()

    async def update_lean_improvement(
        self, request: UpdateLeanImprovementRequest, context
    ) -> LeanImprovement:
        """Обновляет LEAN улучшение."""
        async with self.session_factory() as session:
            try:
                repo = LeanImprovementRepository(session)
                existing_improvement = await repo.get(request.improvement_id)

                if existing_improvement is None:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details(
                        f"LEAN улучшение с ID {request.improvement_id} не найдено"
                    )
                    return LeanImprovement()

                # Преобразуем существующее улучшение в proto для обновления
                existing_proto = domain_lean_improvement_to_proto(existing_improvement)

                # Обновляем поля в proto объекте
                if request.name:
                    existing_proto.name = request.name
                existing_proto.is_implemented = request.is_implemented
                if request.implementation_cost:
                    existing_proto.implementation_cost = request.implementation_cost
                if request.efficiency_gain:
                    existing_proto.efficiency_gain = request.efficiency_gain

                # Преобразуем обновленный proto обратно в доменную сущность
                updated_domain = proto_lean_improvement_to_domain(existing_proto)
                updated_improvement = await repo.save(updated_domain)

                if updated_improvement is None:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Ошибка при обновлении LEAN улучшения")
                    return LeanImprovement()

                return domain_lean_improvement_to_proto(updated_improvement)
            except Exception as e:
                logger.error(f"Error updating lean improvement: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Ошибка при обновлении LEAN улучшения: {str(e)}")
                return LeanImprovement()

    async def delete_lean_improvement(
        self, request: DeleteLeanImprovementRequest, context
    ) -> SuccessResponse:
        """Удаляет LEAN улучшение."""
        async with self.session_factory() as session:
            try:
                repo = LeanImprovementRepository(session)
                deleted_improvement = await repo.delete(request.improvement_id)

                if deleted_improvement is None:
                    return SuccessResponse(
                        success=False,
                        message=f"LEAN улучшение с ID {request.improvement_id} не найдено",
                        timestamp=datetime.now().isoformat(),
                    )

                return SuccessResponse(
                    success=True,
                    message=f"LEAN улучшение {request.improvement_id} успешно удалено",
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                logger.error(f"Error deleting lean improvement: {e}", exc_info=True)
                return SuccessResponse(
                    success=False,
                    message=f"Ошибка при удалении LEAN улучшения: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )

    async def get_all_lean_improvements(
        self, request: GetAllLeanImprovementsRequest, context
    ) -> GetAllLeanImprovementsResponse:
        """Получает все LEAN улучшения."""
        async with self.session_factory() as session:
            try:
                repo = LeanImprovementRepository(session)
                domain_improvements = await repo.get_all()

                proto_improvements = [
                    domain_lean_improvement_to_proto(imp) for imp in domain_improvements
                ]

                return GetAllLeanImprovementsResponse(
                    improvements=proto_improvements,
                    total_count=len(proto_improvements),
                )
            except Exception as e:
                logger.error(f"Error getting all lean improvements: {e}", exc_info=True)
                return GetAllLeanImprovementsResponse(
                    improvements=[],
                    total_count=0,
                )

    async def ping(self, request: PingRequest, context) -> SuccessResponse:
        return SuccessResponse(
            success=True,
            message="Database manager service is running",
            timestamp=datetime.now().isoformat(),
        )
