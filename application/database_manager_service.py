from typing import Dict, List, Optional
import uuid
from datetime import datetime
import grpc
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
    ProductionPlanAssignment,
    DistributionStrategy,
    SimulationParameters,
    SimulationResults,
    Simulation,
    FactoryMetrics,
    WarehouseMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
    ProductionSchedule,
    WorkshopPlan,
    UnplannedRepair,
    SpaghettiDiagram,
    RequiredMaterial,
    QualityInspection,
    DeliverySchedule,
    Certification,
    LeanImprovement,
    WarehouseLoadChart,
    OperationTimingChart,
    DowntimeChart,
    ModelMasteryChart,
    ProjectProfitabilityChart,
    # Ответы справочных данных
    ReferenceDataResponse,
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
    # Запросы справочных данных
    GetReferenceDataRequest,
    GetMaterialTypesRequest,
    GetEquipmentTypesRequest,
    GetWorkplaceTypesRequest,
    GetAvailableDefectPoliciesRequest,
    GetAvailableImprovementsListRequest,
    GetAvailableCertificationsRequest,
    GetAvailableSalesStrategiesRequest,
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


class SimulationDatabaseManagerImpl(SimulationDatabaseManagerServicer):
    def __init__(self) -> None:
        self.suppliers: Dict[str, Supplier] = {}
        self.workers: Dict[str, Worker] = {}
        self.logists: Dict[str, Logist] = {}
        self.workplaces: Dict[str, Workplace] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.tenders: Dict[str, Tender] = {}
        self.equipment: Dict[str, Equipment] = {}
        self._init_test_data()

    def _init_test_data(self):
        """Инициализация тестовых данных."""
        # Тестовые поставщики
        self.suppliers["supplier_001"] = Supplier(
            supplier_id="supplier_001",
            name="ООО 'МеталлПром'",
            product_name="Листовой металл",
            delivery_period=5,
            special_delivery_period=2,
            reliability=0.92,
            product_quality=0.88,
            cost=120000,
            special_delivery_cost=200000,
        )

        self.suppliers["supplier_002"] = Supplier(
            supplier_id="supplier_002",
            name="АО 'Электроника'",
            product_name="Электронные компоненты",
            delivery_period=7,
            special_delivery_period=3,
            reliability=0.85,
            product_quality=0.90,
            cost=95000,
            special_delivery_cost=180000,
        )

        # Тестовые рабочие
        self.workers["worker_001"] = Worker(
            worker_id="worker_001",
            name="Иванов Иван Иванович",
            qualification=5,
            specialty="Слесарь-сборщик",
            salary=75000,
        )

        self.workers["worker_002"] = Worker(
            worker_id="worker_002",
            name="Петров Петр Петрович",
            qualification=7,
            specialty="Инженер-технолог",
            salary=105000,
        )

        # Тестовые логисты
        self.logists["logist_001"] = Logist(
            worker_id="logist_001",
            name="Смирнов Александр Сергеевич",
            qualification=7,
            specialty="Логистика",
            salary=95000,
            speed=70,
            vehicle_type="Грузовой фургон",
        )

        # Тестовое оборудование
        self.equipment["equipment_001"] = Equipment(
            equipment_id="equipment_001",
            name="Токарный станок ЧПУ",
            reliability=0.95,
            maintenance_period=30,
            maintenance_cost=50000,
            cost=1500000,
            repair_cost=300000,
            repair_time=5,
        )

        self.equipment["equipment_002"] = Equipment(
            equipment_id="equipment_002",
            name="Фрезерный станок",
            reliability=0.92,
            maintenance_period=25,
            maintenance_cost=45000,
            cost=1200000,
            repair_cost=250000,
            repair_time=4,
        )

        # Тестовые рабочие места (обновлены с новыми полями)
        self.workplaces["workplace_001"] = Workplace(
            workplace_id="workplace_001",
            workplace_name="Слесарный участок №1",
            required_speciality="Слесарь",
            required_qualification=4,
            required_stages=["Склад", "Подготовка"],
            is_start_node=False,
            is_end_node=False,
            next_workplace_ids=["workplace_002"],
        )

        self.workplaces["workplace_002"] = Workplace(
            workplace_id="workplace_002",
            workplace_name="Сборочный участок",
            required_speciality="Сборщик",
            required_qualification=5,
            required_stages=["workplace_001"],
            is_start_node=True,  # Начальный узел
            is_end_node=False,
            next_workplace_ids=["workplace_003"],
        )

        self.workplaces["workplace_003"] = Workplace(
            workplace_id="workplace_003",
            workplace_name="Контроль качества",
            required_speciality="Контролер",
            required_qualification=4,
            required_stages=["workplace_002"],
            is_start_node=False,
            is_end_node=True,  # Конечный узел
            next_workplace_ids=[],
        )

        # Тестовые заказчики
        self.consumers["consumer_001"] = Consumer(
            consumer_id="consumer_001",
            name="ООО 'Промышленные Технологии'",
            type="Государственная",
        )

        self.consumers["consumer_002"] = Consumer(
            consumer_id="consumer_002",
            name="ЗАО 'Спутниковые Системы'",
            type="Частная",
        )

        # Тестовые тендеры (обновлены с новыми полями)
        tender_001 = Tender(
            tender_id="tender_001",
            cost=3500000,
            quantity_of_products=15,
            penalty_per_day=1000000,  # 1 млн руб/день
            warranty_years=3,
            payment_form="50% аванс, 50% по факту",
        )
        tender_001.consumer.CopyFrom(self.consumers["consumer_001"])
        self.tenders["tender_001"] = tender_001

        tender_002 = Tender(
            tender_id="tender_002",
            cost=5200000,
            quantity_of_products=25,
            penalty_per_day=1500000,
            warranty_years=5,
            payment_form="100% по факту выполнения",
        )
        tender_002.consumer.CopyFrom(self.consumers["consumer_002"])
        self.tenders["tender_002"] = tender_002

    # -----------------------------------------------------------------
    #          Методы для поставщиков
    # -----------------------------------------------------------------

    async def create_supplier(
        self, request: CreateSupplierRequest, context
    ) -> Supplier:
        supplier_id = f"supplier_{uuid.uuid4().hex[:8]}"

        supplier = Supplier(
            supplier_id=supplier_id,
            name=request.name,
            product_name=request.product_name,
            delivery_period=request.delivery_period,
            special_delivery_period=request.special_delivery_period,
            reliability=request.reliability,
            product_quality=request.product_quality,
            cost=request.cost,
            special_delivery_cost=request.special_delivery_cost,
        )

        self.suppliers[supplier_id] = supplier
        return supplier

    async def update_supplier(
        self, request: UpdateSupplierRequest, context
    ) -> Supplier:
        if request.supplier_id not in self.suppliers:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Поставщик с ID {request.supplier_id} не найден")
            return Supplier()

        supplier = self.suppliers[request.supplier_id]

        # Обновляем поля
        if request.name:
            supplier.name = request.name
        if request.product_name:
            supplier.product_name = request.product_name
        if request.delivery_period:
            supplier.delivery_period = request.delivery_period
        if request.special_delivery_period:
            supplier.special_delivery_period = request.special_delivery_period
        if request.reliability:
            supplier.reliability = request.reliability
        if request.product_quality:
            supplier.product_quality = request.product_quality
        if request.cost:
            supplier.cost = request.cost
        if request.special_delivery_cost:
            supplier.special_delivery_cost = request.special_delivery_cost

        return supplier

    async def delete_supplier(
        self, request: DeleteSupplierRequest, context
    ) -> SuccessResponse:
        if request.supplier_id not in self.suppliers:
            return SuccessResponse(
                success=False,
                message=f"Поставщик с ID {request.supplier_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.suppliers[request.supplier_id]

        return SuccessResponse(
            success=True,
            message=f"Поставщик {request.supplier_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_suppliers(
        self, request: GetAllSuppliersRequest, context
    ) -> GetAllSuppliersResponse:
        return GetAllSuppliersResponse(
            suppliers=list(self.suppliers.values()),
            total_count=len(self.suppliers),
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
                qualification=3,
                specialty="Кладовщик",
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
        worker_id = f"worker_{uuid.uuid4().hex[:8]}"

        worker = Worker(
            worker_id=worker_id,
            name=request.name,
            qualification=request.qualification,
            specialty=request.specialty,
            salary=request.salary,
        )

        self.workers[worker_id] = worker
        return worker

    async def update_worker(self, request: UpdateWorkerRequest, context) -> Worker:
        if request.worker_id not in self.workers:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Рабочий с ID {request.worker_id} не найден")
            return Worker()

        worker = self.workers[request.worker_id]

        # Обновляем поля
        if request.name:
            worker.name = request.name
        if request.qualification:
            worker.qualification = request.qualification
        if request.specialty:
            worker.specialty = request.specialty
        if request.salary:
            worker.salary = request.salary

        return worker

    async def delete_worker(
        self, request: DeleteWorkerRequest, context
    ) -> SuccessResponse:
        if request.worker_id not in self.workers:
            return SuccessResponse(
                success=False,
                message=f"Рабочий с ID {request.worker_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.workers[request.worker_id]

        return SuccessResponse(
            success=True,
            message=f"Рабочий {request.worker_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_workers(
        self, request: GetAllWorkersRequest, context
    ) -> GetAllWorkersResponse:
        return GetAllWorkersResponse(
            workers=list(self.workers.values()),
            total_count=len(self.workers),
        )

    # -----------------------------------------------------------------
    #          Методы для логистов
    # -----------------------------------------------------------------

    async def create_logist(self, request: CreateLogistRequest, context) -> Logist:
        logist_id = f"logist_{uuid.uuid4().hex[:8]}"

        logist = Logist(
            worker_id=logist_id,
            name=request.name,
            qualification=request.qualification,
            specialty=request.specialty,
            salary=request.salary,
            speed=request.speed,
            vehicle_type=request.vehicle_type,
        )

        self.logists[logist_id] = logist
        return logist

    async def update_logist(self, request: UpdateLogistRequest, context) -> Logist:
        if request.worker_id not in self.logists:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Логист с ID {request.worker_id} не найден")
            return Logist()

        logist = self.logists[request.worker_id]

        # Обновляем поля
        if request.name:
            logist.name = request.name
        if request.qualification:
            logist.qualification = request.qualification
        if request.specialty:
            logist.specialty = request.specialty
        if request.salary:
            logist.salary = request.salary
        if request.speed:
            logist.speed = request.speed
        if request.vehicle_type:
            logist.vehicle_type = request.vehicle_type

        return logist

    async def delete_logist(
        self, request: DeleteLogistRequest, context
    ) -> SuccessResponse:
        if request.worker_id not in self.logists:
            return SuccessResponse(
                success=False,
                message=f"Логист с ID {request.worker_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.logists[request.worker_id]

        return SuccessResponse(
            success=True,
            message=f"Логист {request.worker_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_logists(
        self, request: GetAllLogistsRequest, context
    ) -> GetAllLogistsResponse:
        return GetAllLogistsResponse(
            logists=list(self.logists.values()),
            total_count=len(self.logists),
        )

    # -----------------------------------------------------------------
    #          Методы для рабочих мест
    # -----------------------------------------------------------------

    async def create_workplace(
        self, request: CreateWorkplaceRequest, context
    ) -> Workplace:
        workplace_id = f"workplace_{uuid.uuid4().hex[:8]}"

        # Получаем работника если указан
        worker = None
        if request.worker_id and request.worker_id in self.workers:
            worker = self.workers[request.worker_id]

        workplace = Workplace(
            workplace_id=workplace_id,
            workplace_name=request.workplace_name,
            required_speciality=request.required_speciality,
            required_qualification=request.required_qualification,
            required_stages=list(request.required_stages),
            is_start_node=False,
            is_end_node=False,
            next_workplace_ids=[],
        )
        if worker:
            workplace.worker.CopyFrom(worker)
        # equipment остается пустым (по умолчанию)

        self.workplaces[workplace_id] = workplace
        return workplace

    async def update_workplace(
        self, request: UpdateWorkplaceRequest, context
    ) -> Workplace:
        if request.workplace_id not in self.workplaces:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Рабочее место с ID {request.workplace_id} не найдено")
            return Workplace()

        workplace = self.workplaces[request.workplace_id]

        # Обновляем поля
        if request.workplace_name:
            workplace.workplace_name = request.workplace_name
        if request.required_speciality:
            workplace.required_speciality = request.required_speciality
        if request.required_qualification:
            workplace.required_qualification = request.required_qualification

        # Обновляем работника если указан
        if request.worker_id:
            if request.worker_id in self.workers:
                workplace.worker.CopyFrom(self.workers[request.worker_id])
            else:
                workplace.worker.CopyFrom(Worker())

        if request.required_stages:
            workplace.required_stages.clear()
            workplace.required_stages.extend(request.required_stages)

        return workplace

    async def delete_workplace(
        self, request: DeleteWorkplaceRequest, context
    ) -> SuccessResponse:
        if request.workplace_id not in self.workplaces:
            return SuccessResponse(
                success=False,
                message=f"Рабочее место с ID {request.workplace_id} не найдено",
                timestamp=datetime.now().isoformat(),
            )

        del self.workplaces[request.workplace_id]

        return SuccessResponse(
            success=True,
            message=f"Рабочее место {request.workplace_id} успешно удалено",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_workplaces(
        self, request: GetAllWorkplacesRequest, context
    ) -> GetAllWorkplacesResponse:
        return GetAllWorkplacesResponse(
            workplaces=list(self.workplaces.values()),
            total_count=len(self.workplaces),
        )

    # -----------------------------------------------------------------
    #          Методы для карты процесса
    # -----------------------------------------------------------------

    async def get_process_graph(
        self, request: GetProcessGraphRequest, context
    ) -> ProcessGraph:
        # Создаем маршруты между рабочими местами
        routes = []
        for workplace_id, workplace in self.workplaces.items():
            for next_workplace_id in workplace.next_workplace_ids:
                if next_workplace_id in self.workplaces:
                    routes.append(
                        Route(
                            length=10,  # Стандартная длина
                            from_workplace=workplace_id,
                            to_workplace=next_workplace_id,
                        )
                    )

        return ProcessGraph(
            process_graph_id=request.process_graph_id,
            workplaces=list(self.workplaces.values()),
            routes=routes,
        )

    # -----------------------------------------------------------------
    #          Методы для заказчиков
    # -----------------------------------------------------------------

    async def create_consumer(
        self, request: CreateConsumerRequest, context
    ) -> Consumer:
        consumer_id = f"consumer_{uuid.uuid4().hex[:8]}"

        consumer = Consumer(
            consumer_id=consumer_id,
            name=request.name,
            type=request.type,
        )

        self.consumers[consumer_id] = consumer
        return consumer

    async def update_consumer(
        self, request: UpdateConsumerRequest, context
    ) -> Consumer:
        if request.consumer_id not in self.consumers:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Заказчик с ID {request.consumer_id} не найден")
            return Consumer()

        consumer = self.consumers[request.consumer_id]

        # Обновляем поля
        if request.name:
            consumer.name = request.name
        if request.type:
            consumer.type = request.type

        return consumer

    async def delete_consumer(
        self, request: DeleteConsumerRequest, context
    ) -> SuccessResponse:
        if request.consumer_id not in self.consumers:
            return SuccessResponse(
                success=False,
                message=f"Заказчик с ID {request.consumer_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.consumers[request.consumer_id]

        return SuccessResponse(
            success=True,
            message=f"Заказчик {request.consumer_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_consumers(
        self, request: GetAllConsumersRequest, context
    ) -> GetAllConsumersResponse:
        return GetAllConsumersResponse(
            consumers=list(self.consumers.values()),
            total_count=len(self.consumers),
        )

    # -----------------------------------------------------------------
    #          Методы для тендеров
    # -----------------------------------------------------------------

    async def create_tender(self, request: CreateTenderRequest, context) -> Tender:
        tender_id = f"tender_{uuid.uuid4().hex[:8]}"

        # Получаем заказчика
        consumer = None
        if request.consumer_id in self.consumers:
            consumer = self.consumers[request.consumer_id]
        else:
            # Создаем временного заказчика
            consumer = Consumer(
                consumer_id=request.consumer_id,
                name="Временный заказчик",
                type="Коммерческая",
            )

        tender = Tender(
            tender_id=tender_id,
            cost=request.cost,
            quantity_of_products=request.quantity_of_products,
            penalty_per_day=request.penalty_per_day if request.penalty_per_day else 0,
            warranty_years=request.warranty_years if request.warranty_years else 1,
            payment_form=request.payment_form if request.payment_form else "",
        )
        tender.consumer.CopyFrom(consumer)

        self.tenders[tender_id] = tender
        return tender

    async def update_tender(self, request: UpdateTenderRequest, context) -> Tender:
        if request.tender_id not in self.tenders:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Тендер с ID {request.tender_id} не найден")
            return Tender()

        tender = self.tenders[request.tender_id]

        # Обновляем поля
        if request.consumer_id:
            if request.consumer_id in self.consumers:
                tender.consumer.CopyFrom(self.consumers[request.consumer_id])
        if request.cost:
            tender.cost = request.cost
        if request.quantity_of_products:
            tender.quantity_of_products = request.quantity_of_products
        if request.penalty_per_day:
            tender.penalty_per_day = request.penalty_per_day
        if request.warranty_years:
            tender.warranty_years = request.warranty_years
        if request.payment_form:
            tender.payment_form = request.payment_form

        return tender

    async def delete_tender(
        self, request: DeleteTenderRequest, context
    ) -> SuccessResponse:
        if request.tender_id not in self.tenders:
            return SuccessResponse(
                success=False,
                message=f"Тендер с ID {request.tender_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.tenders[request.tender_id]

        return SuccessResponse(
            success=True,
            message=f"Тендер {request.tender_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_tenders(
        self, request: GetAllTendersRequest, context
    ) -> GetAllTendersResponse:
        return GetAllTendersResponse(
            tenders=list(self.tenders.values()),
            total_count=len(self.tenders),
        )

    # -----------------------------------------------------------------
    #          Методы для оборудования
    # -----------------------------------------------------------------

    async def create_equipment(
        self, request: CreateEquipmentRequest, context
    ) -> Equipment:
        equipment_id = f"equipment_{uuid.uuid4().hex[:8]}"

        equipment = Equipment(
            equipment_id=equipment_id,
            name=request.name,
            reliability=request.reliability,
            maintenance_period=request.maintenance_period,
            maintenance_cost=request.maintenance_cost,
            cost=request.cost,
            repair_cost=request.repair_cost,
            repair_time=request.repair_time,
        )

        self.equipment[equipment_id] = equipment
        return equipment

    async def update_equipment(
        self, request: UpdateEquipmentRequest, context
    ) -> Equipment:
        if request.equipment_id not in self.equipment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Оборудование с ID {request.equipment_id} не найдено")
            return Equipment()

        equipment = self.equipment[request.equipment_id]

        # Обновляем поля
        if request.name:
            equipment.name = request.name
        if request.reliability:
            equipment.reliability = request.reliability
        if request.maintenance_period:
            equipment.maintenance_period = request.maintenance_period
        if request.maintenance_cost:
            equipment.maintenance_cost = request.maintenance_cost
        if request.cost:
            equipment.cost = request.cost
        if request.repair_cost:
            equipment.repair_cost = request.repair_cost
        if request.repair_time:
            equipment.repair_time = request.repair_time

        return equipment

    async def delete_equipment(
        self, request: DeleteEquipmentRequest, context
    ) -> SuccessResponse:
        if request.equipment_id not in self.equipment:
            return SuccessResponse(
                success=False,
                message=f"Оборудование с ID {request.equipment_id} не найдено",
                timestamp=datetime.now().isoformat(),
            )

        del self.equipment[request.equipment_id]

        return SuccessResponse(
            success=True,
            message=f"Оборудование {request.equipment_id} успешно удалено",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_equipment(
        self, request: GetAllEquipmentRequest, context
    ) -> GetAllEquipmentResopnse:
        return GetAllEquipmentResopnse(
            equipments=list(self.equipment.values()),
            total_count=len(self.equipment),
        )

    # -----------------------------------------------------------------
    #          Новые методы для справочных данных
    # -----------------------------------------------------------------

    async def get_reference_data(
        self, request: GetReferenceDataRequest, context
    ) -> ReferenceDataResponse:
        """Получение всех справочных данных."""
        data_type = request.data_type.lower() if request.data_type else "all"

        response = ReferenceDataResponse(timestamp=datetime.now().isoformat())

        # Стратегии продаж
        if data_type in ["all", "sales_strategies"]:
            response.sales_strategies.extend(
                [
                    ReferenceDataResponse.SalesStrategyItem(
                        id="strategy_01",
                        name="Низкие цены",
                        description="Стратегия низких цен для привлечения клиентов",
                        growth_forecast=0.15,
                        unit_cost=85000,
                        market_impact="Высокий",
                        trend_direction="↑",
                    ),
                    ReferenceDataResponse.SalesStrategyItem(
                        id="strategy_02",
                        name="Дифференциация",
                        description="Уникальные продукты с повышенным качеством",
                        growth_forecast=0.10,
                        unit_cost=120000,
                        market_impact="Средний",
                        trend_direction="→",
                    ),
                    ReferenceDataResponse.SalesStrategyItem(
                        id="strategy_03",
                        name="Премиум",
                        description="Высококачественные продукты для премиум-сегмента",
                        growth_forecast=0.08,
                        unit_cost=180000,
                        market_impact="Низкий",
                        trend_direction="↑",
                    ),
                ]
            )

        # Политики работы с браком
        if data_type in ["all", "defect_policies"]:
            response.defect_policies.extend(
                [
                    ReferenceDataResponse.DefectPolicyItem(
                        id="policy_01",
                        name="Утилизировать",
                        description="Полная утилизация бракованной продукции",
                    ),
                    ReferenceDataResponse.DefectPolicyItem(
                        id="policy_02",
                        name="Переделать",
                        description="Исправление брака и повторная обработка",
                    ),
                    ReferenceDataResponse.DefectPolicyItem(
                        id="policy_03",
                        name="Продать как есть",
                        description="Продажа брака по сниженной цене",
                    ),
                ]
            )

        # Сертификации
        if data_type in ["all", "certifications"]:
            response.certifications.extend(
                [
                    ReferenceDataResponse.CertificationItem(
                        id="cert_01",
                        name="ГОСТ Р",
                        description="Российский государственный стандарт",
                        implementation_cost=500000,
                        implementation_time_days=90,
                    ),
                    ReferenceDataResponse.CertificationItem(
                        id="cert_02",
                        name="ISO 9001",
                        description="Международный стандарт качества",
                        implementation_cost=750000,
                        implementation_time_days=120,
                    ),
                    ReferenceDataResponse.CertificationItem(
                        id="cert_03",
                        name="Евростандарт",
                        description="Европейские стандарты качества",
                        implementation_cost=1000000,
                        implementation_time_days=180,
                    ),
                ]
            )

        # LEAN улучшения
        if data_type in ["all", "improvements"]:
            response.improvements.extend(
                [
                    ReferenceDataResponse.ImprovementItem(
                        id="improvement_01",
                        name="5S система",
                        description="Система организации рабочего места",
                        implementation_cost=200000,
                        efficiency_gain=0.15,
                    ),
                    ReferenceDataResponse.ImprovementItem(
                        id="improvement_02",
                        name="Канбан",
                        description="Система управления производством",
                        implementation_cost=350000,
                        efficiency_gain=0.20,
                    ),
                    ReferenceDataResponse.ImprovementItem(
                        id="improvement_03",
                        name="Всеобщее обслуживание оборудования",
                        description="Система технического обслуживания",
                        implementation_cost=500000,
                        efficiency_gain=0.12,
                    ),
                ]
            )

        # Типы компаний
        if data_type in ["all", "company_types"]:
            response.company_types.extend(
                [
                    ReferenceDataResponse.CompanyTypeItem(
                        id="company_type_01",
                        name="Государственная",
                        description="Государственные предприятия и организации",
                    ),
                    ReferenceDataResponse.CompanyTypeItem(
                        id="company_type_02",
                        name="Частная",
                        description="Частные компании и предприятия",
                    ),
                    ReferenceDataResponse.CompanyTypeItem(
                        id="company_type_03",
                        name="Иностранная",
                        description="Иностранные компании и представительства",
                    ),
                ]
            )

        # Специализации работников
        if data_type in ["all", "specialties"]:
            response.specialties.extend(
                [
                    ReferenceDataResponse.SpecialtyItem(
                        id="specialty_01",
                        name="Слесарь-сборщик",
                        description="Сборка и слесарные работы",
                    ),
                    ReferenceDataResponse.SpecialtyItem(
                        id="specialty_02",
                        name="Инженер-технолог",
                        description="Разработка технологических процессов",
                    ),
                    ReferenceDataResponse.SpecialtyItem(
                        id="specialty_03",
                        name="Логист",
                        description="Организация логистики и транспорта",
                    ),
                    ReferenceDataResponse.SpecialtyItem(
                        id="specialty_04",
                        name="Контролер качества",
                        description="Контроль качества продукции",
                    ),
                ]
            )

        # Типы транспорта
        if data_type in ["all", "vehicle_types"]:
            response.vehicle_types.extend(
                [
                    ReferenceDataResponse.VehicleTypeItem(
                        id="vehicle_01",
                        name="Грузовой фургон",
                        description="Малотоннажный транспорт",
                        speed_modifier=10,  # 1.0 * 10 для uint32
                    ),
                    ReferenceDataResponse.VehicleTypeItem(
                        id="vehicle_02",
                        name="Фура",
                        description="Крупнотоннажный транспорт",
                        speed_modifier=8,  # 0.8 * 10 для uint32
                    ),
                    ReferenceDataResponse.VehicleTypeItem(
                        id="vehicle_03",
                        name="Электрокар",
                        description="Электрический транспорт",
                        speed_modifier=12,  # 1.2 * 10 для uint32
                    ),
                ]
            )

        # Размеры юнитов
        if data_type in ["all", "unit_sizes"]:
            response.unit_sizes.extend(
                [
                    ReferenceDataResponse.UnitSizeItem(
                        id="1U",
                        name="1U",
                        description="Стандартный размер 1U",
                    ),
                    ReferenceDataResponse.UnitSizeItem(
                        id="2U",
                        name="2U",
                        description="Двойной размер 2U",
                    ),
                    ReferenceDataResponse.UnitSizeItem(
                        id="3U",
                        name="3U",
                        description="Тройной размер 3U",
                    ),
                    ReferenceDataResponse.UnitSizeItem(
                        id="6U",
                        name="6U",
                        description="Размер 6U для крупных систем",
                    ),
                ]
            )

        # Модели продукции
        if data_type in ["all", "product_models"]:
            response.product_models.extend(
                [
                    ReferenceDataResponse.ProductModelItem(
                        id="model_01",
                        name="Спутник связи",
                        description="Спутник для телекоммуникаций",
                        unit_size="3U",
                    ),
                    ReferenceDataResponse.ProductModelItem(
                        id="model_02",
                        name="Научный спутник",
                        description="Спутник для научных исследований",
                        unit_size="2U",
                    ),
                    ReferenceDataResponse.ProductModelItem(
                        id="model_03",
                        name="Навигационный спутник",
                        description="Спутник для навигационных систем",
                        unit_size="6U",
                    ),
                ]
            )

        # Формы оплаты
        if data_type in ["all", "payment_forms"]:
            response.payment_forms.extend(
                [
                    ReferenceDataResponse.PaymentFormItem(
                        id="payment_01",
                        name="100% аванс",
                        description="Полная предоплата",
                    ),
                    ReferenceDataResponse.PaymentFormItem(
                        id="payment_02",
                        name="50% аванс, 50% по факту",
                        description="Частичная предоплата",
                    ),
                    ReferenceDataResponse.PaymentFormItem(
                        id="payment_03",
                        name="100% по факту",
                        description="Оплата после выполнения",
                    ),
                ]
            )

        # Типы рабочих мест
        if data_type in ["all", "workplace_types"]:
            response.workplace_types.extend(
                [
                    ReferenceDataResponse.WorkplaceTypeItem(
                        id="workplace_type_01",
                        name="Слесарный участок",
                        description="Участок слесарных работ",
                        required_specialty="Слесарь",
                        required_qualification=4,
                        compatible_equipment=["Токарный станок", "Фрезерный станок"],
                    ),
                    ReferenceDataResponse.WorkplaceTypeItem(
                        id="workplace_type_02",
                        name="Сборочный участок",
                        description="Участок сборки",
                        required_specialty="Сборщик",
                        required_qualification=5,
                        compatible_equipment=["Сборочный стол", "Конвейер"],
                    ),
                    ReferenceDataResponse.WorkplaceTypeItem(
                        id="workplace_type_03",
                        name="Контроль качества",
                        description="Участок контроля качества",
                        required_specialty="Контролер",
                        required_qualification=4,
                        compatible_equipment=[
                            "Измерительное оборудование",
                            "Микроскоп",
                        ],
                    ),
                ]
            )

        return response

    async def get_material_types(
        self, request: GetMaterialTypesRequest, context
    ) -> MaterialTypesResponse:
        """Получение типов материалов."""
        return MaterialTypesResponse(
            material_types=[
                MaterialTypesResponse.MaterialType(
                    material_id="material_01",
                    name="Листовой металл",
                    description="Металлический лист различной толщины",
                    unit="кг",
                    average_price=150,
                ),
                MaterialTypesResponse.MaterialType(
                    material_id="material_02",
                    name="Электронные компоненты",
                    description="Микросхемы, резисторы, конденсаторы",
                    unit="шт",
                    average_price=75,
                ),
                MaterialTypesResponse.MaterialType(
                    material_id="material_03",
                    name="Пластик ABS",
                    description="Технический пластик для корпусов",
                    unit="кг",
                    average_price=120,
                ),
                MaterialTypesResponse.MaterialType(
                    material_id="material_04",
                    name="Крепежные изделия",
                    description="Болты, гайки, винты",
                    unit="кг",
                    average_price=85,
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def get_equipment_types(
        self, request: GetEquipmentTypesRequest, context
    ) -> EquipmentTypesResponse:
        """Получение типов оборудования."""
        return EquipmentTypesResponse(
            equipment_types=[
                EquipmentTypesResponse.EquipmentType(
                    equipment_type_id="equipment_type_01",
                    name="Токарный станок ЧПУ",
                    description="ЧПУ станок для токарной обработки",
                    base_reliability=0.95,
                    base_maintenance_cost=50000,
                    base_cost=1500000,
                    compatible_workplaces=["workplace_type_01"],
                ),
                EquipmentTypesResponse.EquipmentType(
                    equipment_type_id="equipment_type_02",
                    name="Фрезерный станок",
                    description="Станок для фрезерной обработки",
                    base_reliability=0.92,
                    base_maintenance_cost=45000,
                    base_cost=1200000,
                    compatible_workplaces=["workplace_type_01"],
                ),
                EquipmentTypesResponse.EquipmentType(
                    equipment_type_id="equipment_type_03",
                    name="Сборочный стол",
                    description="Стол для сборки изделий",
                    base_reliability=0.98,
                    base_maintenance_cost=10000,
                    base_cost=250000,
                    compatible_workplaces=["workplace_type_02"],
                ),
                EquipmentTypesResponse.EquipmentType(
                    equipment_type_id="equipment_type_04",
                    name="Измерительный комплекс",
                    description="Комплекс для контроля качества",
                    base_reliability=0.96,
                    base_maintenance_cost=30000,
                    base_cost=800000,
                    compatible_workplaces=["workplace_type_03"],
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def get_workplace_types(
        self, request: GetWorkplaceTypesRequest, context
    ) -> WorkplaceTypesResponse:
        """Получение типов рабочих мест."""
        return WorkplaceTypesResponse(
            workplace_types=[
                WorkplaceTypesResponse.WorkplaceType(
                    workplace_type_id="workplace_type_01",
                    name="Слесарный участок",
                    description="Участок для слесарных и механических работ",
                    required_specialty="Слесарь",
                    required_qualification=4,
                    compatible_equipment_types=[
                        "equipment_type_01",
                        "equipment_type_02",
                    ],
                ),
                WorkplaceTypesResponse.WorkplaceType(
                    workplace_type_id="workplace_type_02",
                    name="Сборочный участок",
                    description="Участок для сборки готовых изделий",
                    required_specialty="Сборщик",
                    required_qualification=5,
                    compatible_equipment_types=["equipment_type_03"],
                ),
                WorkplaceTypesResponse.WorkplaceType(
                    workplace_type_id="workplace_type_03",
                    name="Контроль качества",
                    description="Участок для контроля качества продукции",
                    required_specialty="Контролер",
                    required_qualification=4,
                    compatible_equipment_types=["equipment_type_04"],
                ),
                WorkplaceTypesResponse.WorkplaceType(
                    workplace_type_id="workplace_type_04",
                    name="Склад материалов",
                    description="Склад для хранения материалов и комплектующих",
                    required_specialty="Кладовщик",
                    required_qualification=3,
                    compatible_equipment_types=[],
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_defect_policies(
        self, request: GetAvailableDefectPoliciesRequest, context
    ) -> DefectPoliciesListResponse:
        """Получение доступных политик работы с браком."""
        return DefectPoliciesListResponse(
            policies=[
                DefectPoliciesListResponse.DefectPolicyOption(
                    id="policy_01",
                    name="Утилизировать",
                    description="Полная утилизация бракованной продукции",
                    cost_multiplier=1.0,
                    quality_impact=0.0,
                    time_impact=0.1,
                ),
                DefectPoliciesListResponse.DefectPolicyOption(
                    id="policy_02",
                    name="Переделать",
                    description="Исправление брака и повторная обработка",
                    cost_multiplier=1.5,
                    quality_impact=0.8,
                    time_impact=0.3,
                ),
                DefectPoliciesListResponse.DefectPolicyOption(
                    id="policy_03",
                    name="Продать как есть",
                    description="Продажа брака по сниженной цене",
                    cost_multiplier=0.6,
                    quality_impact=0.5,
                    time_impact=0.0,
                ),
                DefectPoliciesListResponse.DefectPolicyOption(
                    id="policy_04",
                    name="Вернуть поставщику",
                    description="Возврат бракованных материалов поставщику",
                    cost_multiplier=0.8,
                    quality_impact=0.9,
                    time_impact=0.2,
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_improvements_list(
        self, request: GetAvailableImprovementsListRequest, context
    ) -> ImprovementsListResponse:
        """Получение доступных LEAN улучшений."""
        return ImprovementsListResponse(
            improvements=[
                ImprovementsListResponse.ImprovementOption(
                    id="improvement_01",
                    name="5S система",
                    description="Система организации рабочего места (Сортировка, Соблюдение порядка, Содержание в чистоте, Стандартизация, Совершенствование)",
                    implementation_cost=200000,
                    implementation_time_days=30,
                    efficiency_gain=0.15,
                    quality_improvement=0.10,
                    cost_reduction=0.05,
                ),
                ImprovementsListResponse.ImprovementOption(
                    id="improvement_02",
                    name="Канбан",
                    description="Система управления производством 'точно в срок'",
                    implementation_cost=350000,
                    implementation_time_days=60,
                    efficiency_gain=0.20,
                    quality_improvement=0.08,
                    cost_reduction=0.10,
                ),
                ImprovementsListResponse.ImprovementOption(
                    id="improvement_03",
                    name="Всеобщее обслуживание оборудования",
                    description="Система технического обслуживания оборудования с участием всех сотрудников",
                    implementation_cost=500000,
                    implementation_time_days=90,
                    efficiency_gain=0.12,
                    quality_improvement=0.15,
                    cost_reduction=0.08,
                ),
                ImprovementsListResponse.ImprovementOption(
                    id="improvement_04",
                    name="Система подачи предложений",
                    description="Система сбора и реализации улучшающих предложений от сотрудников",
                    implementation_cost=150000,
                    implementation_time_days=45,
                    efficiency_gain=0.10,
                    quality_improvement=0.12,
                    cost_reduction=0.06,
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_certifications(
        self, request: GetAvailableCertificationsRequest, context
    ) -> CertificationsListResponse:
        """Получение доступных сертификаций."""
        return CertificationsListResponse(
            certifications=[
                CertificationsListResponse.CertificationOption(
                    id="cert_01",
                    name="ГОСТ Р",
                    description="Российский государственный стандарт качества",
                    implementation_cost=500000,
                    implementation_time_days=90,
                    market_access_improvement=0.40,
                    quality_recognition=0.35,
                    government_access=0.50,
                ),
                CertificationsListResponse.CertificationOption(
                    id="cert_02",
                    name="ISO 9001",
                    description="Международный стандарт системы менеджмента качества",
                    implementation_cost=750000,
                    implementation_time_days=120,
                    market_access_improvement=0.60,
                    quality_recognition=0.70,
                    government_access=0.30,
                ),
                CertificationsListResponse.CertificationOption(
                    id="cert_03",
                    name="Евростандарт CE",
                    description="Европейские стандарты качества и безопасности",
                    implementation_cost=1000000,
                    implementation_time_days=180,
                    market_access_improvement=0.80,
                    quality_recognition=0.85,
                    government_access=0.20,
                ),
                CertificationsListResponse.CertificationOption(
                    id="cert_04",
                    name="ISO 14001",
                    description="Международный стандарт системы экологического менеджмента",
                    implementation_cost=600000,
                    implementation_time_days=100,
                    market_access_improvement=0.50,
                    quality_recognition=0.40,
                    government_access=0.40,
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_sales_strategies(
        self, request: GetAvailableSalesStrategiesRequest, context
    ) -> SalesStrategiesListResponse:
        """Получение доступных стратегий продаж."""
        return SalesStrategiesListResponse(
            strategies=[
                SalesStrategiesListResponse.SalesStrategyOption(
                    id="strategy_01",
                    name="Низкие цены",
                    description="Стратегия низких цен для привлечения клиентов и захвата рынка",
                    growth_forecast=0.15,
                    unit_cost=85000,
                    market_impact="Высокий - быстрое увеличение доли рынка",
                    trend_direction="↑",
                    compatible_product_models=["model_01", "model_02"],
                ),
                SalesStrategiesListResponse.SalesStrategyOption(
                    id="strategy_02",
                    name="Дифференциация",
                    description="Уникальные продукты с повышенным качеством и функциональностью",
                    growth_forecast=0.10,
                    unit_cost=120000,
                    market_impact="Средний - стабильный рост в премиум-сегменте",
                    trend_direction="→",
                    compatible_product_models=["model_02", "model_03"],
                ),
                SalesStrategiesListResponse.SalesStrategyOption(
                    id="strategy_03",
                    name="Премиум",
                    description="Высококачественные продукты для премиум-сегмента с максимальной маржой",
                    growth_forecast=0.08,
                    unit_cost=180000,
                    market_impact="Низкий - специализированный сегмент",
                    trend_direction="↑",
                    compatible_product_models=["model_03"],
                ),
                SalesStrategiesListResponse.SalesStrategyOption(
                    id="strategy_04",
                    name="Фокусировка",
                    description="Концентрация на конкретном рыночном сегменте или нише",
                    growth_forecast=0.12,
                    unit_cost=95000,
                    market_impact="Высокий - лидерство в узком сегменте",
                    trend_direction="↑",
                    compatible_product_models=["model_01", "model_02", "model_03"],
                ),
            ],
            timestamp=datetime.now().isoformat(),
        )

    async def ping(self, request: PingRequest, context) -> SuccessResponse:
        return SuccessResponse(
            success=True,
            message="Database manager service is running",
            timestamp=datetime.now().isoformat(),
        )
