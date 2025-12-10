from datetime import datetime
from typing import Dict, List, Optional
import uuid
import random

import grpc
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
    # Конфигурация процесса
    AddProcessRouteRequest,
    DeleteProcesRouteRequest,
    SetEquipmentOnWorkplaceRequst,
    UnSetEquipmentOnWorkplaceRequst,
    # Управление картой процесса (Инженеринг)
    ConfigureWorkplaceInGraphRequest,
    RemoveWorkplaceFromGraphRequest,
    SetWorkplaceAsStartNodeRequest,
    SetWorkplaceAsEndNodeRequest,
    UpdateProcessGraphRequest,
    # Распределение плана (Производство)
    DistributeProductionPlanRequest,
    ProductionPlanDistributionResponse,
    GetProductionPlanDistributionRequest,
    UpdateProductionAssignmentRequest,
    UpdateWorkshopPlanRequest,
    # Конфигурация тендеров
    AddTenderRequest,
    RemoveTenderRequest,
    # Общие настройки
    SetDealingWithDefectsRequest,
    SetHasCertificationRequest,
    AddProductionImprovementRequest,
    DeleteProductionImprovementRequest,
    SetSalesStrategyRequest,
    # Специфичные настройки по ролям
    SetQualityInspectionRequest,
    SetDeliveryScheduleRequest,
    SetEquipmentMaintenanceIntervalRequest,
    UpdateProductionScheduleRequest,
    SetCertificationStatusRequest,
    SetLeanImprovementStatusRequest,
    SetSalesStrategyWithDetailsRequest,
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
    GetAvailableImprovementsRequest,
    AvailableImprovementsResponse,
    GetDefectPoliciesRequest,
    DefectPoliciesResponse,
    GetSimulationHistoryRequest,
    SimulationHistoryResponse,
    # Пошаговая симуляция
    RunSimulationStepRequest,
    SimulationStepResponse,
    # Валидация
    ValidateConfigurationRequest,
    ValidationResponse,
    # Справочные данные
    GetReferenceDataRequest,
    ReferenceDataResponse,
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
    # Основные сообщения
    Simulation,
    SimulationParameters,
    SimulationResults,
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
)
from grpc_generated.simulator_pb2_grpc import SimulationServiceServicer


class SimulationServiceImpl(SimulationServiceServicer):
    def __init__(self):
        self.simulations: Dict[str, Simulation] = {}
        self.simulation_history: Dict[str, List[SimulationStepResponse]] = {}
        self._init_test_data()

    def _init_test_data(self):
        """Инициализация тестовых данных."""
        # Создаем тестового работника
        test_worker = Worker(
            worker_id="worker_001",
            name="Иванов Иван Иванович",
            qualification=5,
            specialty="Слесарь-сборщик",
            salary=75000,
        )

        # Создаем тестового логиста
        test_logist = Logist(
            worker_id="logist_001",
            name="Петров Петр Петрович",
            qualification=6,
            specialty="Логистика",
            salary=90000,
            speed=60,
            vehicle_type="Газель",
        )

        # Создаем тестовое оборудование
        test_equipment = Equipment(
            equipment_id="equipment_001",
            name="Токарный станок ЧПУ",
            reliability=0.95,
            maintenance_period=30,
            maintenance_cost=50000,
            cost=1500000,
            repair_cost=300000,
            repair_time=5,
        )

        # Создаем тестовые рабочие места (с новыми полями)
        test_workplace_1 = Workplace(
            workplace_id="workplace_001",
            workplace_name="Слесарный участок",
            required_speciality="Слесарь",
            required_qualification=4,
            worker=test_worker,
            equipment=test_equipment,
            required_stages=["Подготовка"],
            is_start_node=True,
            is_end_node=False,
            next_workplace_ids=["workplace_002"],
        )

        test_workplace_2 = Workplace(
            workplace_id="workplace_002",
            workplace_name="Сборочный участок",
            required_speciality="Сборщик",
            required_qualification=5,
            worker=Worker(),
            equipment=Equipment(),
            required_stages=["workplace_001"],
            is_start_node=False,
            is_end_node=False,
            next_workplace_ids=["workplace_003"],
        )

        test_workplace_3 = Workplace(
            workplace_id="workplace_003",
            workplace_name="Контроль качества",
            required_speciality="Контролер",
            required_qualification=4,
            worker=Worker(),
            equipment=Equipment(),
            required_stages=["workplace_002"],
            is_start_node=False,
            is_end_node=True,
            next_workplace_ids=[],
        )

        # Создаем тестового заказчика
        test_consumer = Consumer(
            consumer_id="consumer_001",
            name="ООО 'Промышленные системы'",
            type="Государственная",
        )

        # Создаем тестового поставщика
        test_supplier = Supplier(
            supplier_id="supplier_001",
            name="ООО 'МеталлТрейд'",
            product_name="Сталь листовая",
            delivery_period=5,
            special_delivery_period=2,
            reliability=0.95,
            product_quality=0.92,
            cost=150000,
            special_delivery_cost=250000,
        )

        # Создаем тестовый производственный план
        test_production_schedule = ProductionSchedule(
            schedule_items=[
                ProductionSchedule.ScheduleItem(
                    item_id="item_001",
                    priority=1,
                    plan_number="П-001",
                    plan_date="2024-01-15",
                    product_name="Спутник связи",
                    planned_quantity=10,
                    actual_quantity=0,
                    remaining_to_produce=10,
                    planned_completion_date="2024-03-15",
                    order_number="ЗАК-001",
                    tender_id="tender_001",
                ),
                ProductionSchedule.ScheduleItem(
                    item_id="item_002",
                    priority=2,
                    plan_number="П-002",
                    plan_date="2024-01-20",
                    product_name="Научный спутник",
                    planned_quantity=5,
                    actual_quantity=0,
                    remaining_to_produce=5,
                    planned_completion_date="2024-04-10",
                    order_number="ЗАК-002",
                    tender_id="tender_002",
                ),
            ]
        )

        # Создаем тестовый план цеха
        test_workshop_plan = WorkshopPlan(
            workplace_nodes=[
                WorkshopPlan.WorkplaceNode(
                    workplace_id="workplace_001",
                    assigned_worker=test_worker,
                    assigned_equipment=test_equipment,
                    maintenance_interval=30,
                    is_start_node=True,
                    is_end_node=False,
                    assigned_schedule_items=["item_001", "item_002"],
                    max_capacity_per_day=2,
                    current_utilization=0.75,
                ),
            ],
            logistic_routes=[
                Route(
                    length=10,
                    from_workplace="workplace_001",
                    to_workplace="workplace_002",
                ),
                Route(
                    length=15,
                    from_workplace="workplace_002",
                    to_workplace="workplace_003",
                ),
            ],
            production_schedule_id="schedule_001",
        )

        # Создаем тестовую симуляцию
        simulation_id = "test_simulation_001"

        simulation = Simulation(
            capital=5000000,
            step=1,
            simulation_id=simulation_id,
            parameters=SimulationParameters(
                logist=test_logist,
                suppliers=[test_supplier],
                backup_suppliers=[
                    Supplier(
                        supplier_id="backup_supplier_001",
                        name="Резервный поставщик 'СтройМатериалы'",
                        product_name="Крепежные изделия",
                        delivery_period=10,
                        special_delivery_period=4,
                        reliability=0.75,
                        product_quality=0.85,
                        cost=120000,
                        special_delivery_cost=200000,
                    )
                ],
                materials_warehouse=Warehouse(
                    warehouse_id="warehouse_materials_1",
                    inventory_worker=test_worker,
                    size=1000,
                    loading=350,
                    materials={
                        "Сталь листовая": 200,
                        "Электронные компоненты": 100,
                        "Крепеж": 150,
                    },
                ),
                product_warehouse=Warehouse(
                    warehouse_id="warehouse_products_1",
                    inventory_worker=test_worker,
                    size=500,
                    loading=120,
                    materials={
                        "Готовые станки": 50,
                        "Комплектующие": 70,
                    },
                ),
                processes=ProcessGraph(
                    process_graph_id="process_graph_1",
                    workplaces=[test_workplace_1, test_workplace_2, test_workplace_3],
                    routes=[
                        Route(
                            length=10,
                            from_workplace="workplace_001",
                            to_workplace="workplace_002",
                        ),
                        Route(
                            length=15,
                            from_workplace="workplace_002",
                            to_workplace="workplace_003",
                        ),
                    ],
                ),
                tenders=[
                    Tender(
                        tender_id="tender_001",
                        consumer=test_consumer,
                        cost=2500000,
                        quantity_of_products=10,
                        penalty_per_day=1000000,
                        warranty_years=3,
                        payment_form="50% аванс, 50% по факту",
                    ),
                ],
                dealing_with_defects="Ремонтировать на месте",
                has_certification=True,
                production_improvements=["Автоматизация склада", "Внедрение ERP"],
                sales_strategy="Агрессивная",
                sales_growth_forecast=0.15,
                unit_production_cost=85000,
                certifications=[
                    Certification(
                        certificate_type="ГОСТ Р",
                        is_obtained=True,
                        implementation_cost=500000,
                        implementation_time_days=90,
                    )
                ],
                lean_improvements=[
                    LeanImprovement(
                        improvement_id="improvement_001",
                        name="5S система",
                        is_implemented=True,
                        implementation_cost=200000,
                        efficiency_gain=0.15,
                    )
                ],
                production_assignments={
                    "item_001": ProductionPlanAssignment(
                        schedule_item_id="item_001",
                        workplace_id="workplace_001",
                        assigned_quantity=5,
                        assigned_worker_id="worker_001",
                        assigned_equipment_id="equipment_001",
                        completion_percentage=0.0,
                    ),
                    "item_002": ProductionPlanAssignment(
                        schedule_item_id="item_002",
                        workplace_id="workplace_001",
                        assigned_quantity=3,
                        assigned_worker_id="worker_001",
                        assigned_equipment_id="equipment_001",
                        completion_percentage=0.0,
                    ),
                },
                distribution_strategy=DistributionStrategy.DISTRIBUTION_STRATEGY_BALANCED,
                workshop_plan=test_workshop_plan,
                production_schedule=test_production_schedule,
            ),
            results=SimulationResults(
                profit=1500000,
                cost=1000000,
                profitability=1.5,
            ),
            room_id="room_001",
            is_completed=False,
        )

        self.simulations[simulation_id] = simulation
        self.simulation_history[simulation_id] = []

    # -----------------------------------------------------------------
    #          Базовые методы симуляции
    # -----------------------------------------------------------------

    async def create_simulation(
        self, request: CreateSimulationRquest, context
    ) -> SimulationResponse:
        simulation_id = f"sim_{uuid.uuid4().hex[:8]}"

        simulation = Simulation(
            capital=1000000,
            step=0,
            simulation_id=simulation_id,
            parameters=SimulationParameters(),
            results=SimulationResults(),
            is_completed=False,
        )

        self.simulations[simulation_id] = simulation
        self.simulation_history[simulation_id] = []

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def get_simulation(
        self, request: GetSimulationRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        # Если симуляция не найдена, создаем новую
        if simulation_id not in self.simulations:
            simulation = Simulation(
                capital=1000000,
                step=0,
                simulation_id=simulation_id,
                parameters=SimulationParameters(),
                results=SimulationResults(),
                is_completed=False,
            )
            self.simulations[simulation_id] = simulation
            self.simulation_history[simulation_id] = []

        simulation = self.simulations[simulation_id]

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Конфигурация персонала
    # -----------------------------------------------------------------

    async def set_logist(
        self, request: SetLogistRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        # Создаем тестового логиста
        logist = Logist(
            worker_id=request.worker_id,
            name=f"Логист {request.worker_id}",
            qualification=5,
            specialty="Логистика",
            salary=80000,
            speed=50,
            vehicle_type="Микроавтобус",
        )

        simulation = self.simulations[simulation_id]
        simulation.parameters.logist.CopyFrom(logist)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_warehouse_inventory_worker(
        self, request: SetWarehouseInventoryWorkerRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        # Создаем тестового работника
        worker = Worker(
            worker_id=request.worker_id,
            name="Складской работник",
            qualification=3,
            specialty="Кладовщик",
            salary=45000,
        )

        simulation = self.simulations[simulation_id]

        if request.warehouse_type == 1:  # WAREHOUSE_TYPE_MATERIALS
            simulation.parameters.materials_warehouse.inventory_worker.CopyFrom(worker)
        elif request.warehouse_type == 2:  # WAREHOUSE_TYPE_PRODUCTS
            simulation.parameters.product_warehouse.inventory_worker.CopyFrom(worker)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_worker_on_workerplace(
        self, request: SetWorkerOnWorkerplaceRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        # Создаем тестового работника
        worker = Worker(
            worker_id=request.worker_id,
            name="Работник на месте",
            qualification=4,
            specialty="Оператор",
            salary=60000,
        )

        simulation = self.simulations[simulation_id]

        # Ищем рабочее место и устанавливаем работника
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.workplace_id == request.workplace_id:
                workplace.worker.CopyFrom(worker)
                break

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def unset_worker_on_workerplace(
        self, request: UnSetWorkerOnWorkerplaceRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Убираем работника со всех рабочих мест
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.worker.worker_id == request.worker_id:
                workplace.ClearField("worker")

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Конфигурация поставщиков
    # -----------------------------------------------------------------

    async def add_supplier(
        self, request: AddSupplierRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        # Создаем тестового поставщика
        supplier = Supplier(
            supplier_id=request.supplier_id,
            name=f"Поставщик {request.supplier_id}",
            product_name="Тестовые материалы",
            delivery_period=7,
            special_delivery_period=3,
            reliability=0.85,
            product_quality=0.88,
            cost=100000,
            special_delivery_cost=180000,
        )

        simulation = self.simulations[simulation_id]

        if request.is_backup:
            simulation.parameters.backup_suppliers.append(supplier)
        else:
            simulation.parameters.suppliers.append(supplier)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def delete_supplier(
        self, request: DeleteSupplierRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        supplier_id = request.supplier_id

        # Удаляем из основных поставщиков
        suppliers_to_keep = [
            s for s in simulation.parameters.suppliers if s.supplier_id != supplier_id
        ]
        simulation.parameters.suppliers.clear()
        simulation.parameters.suppliers.extend(suppliers_to_keep)

        # Удаляем из запасных поставщиков
        backup_suppliers_to_keep = [
            s
            for s in simulation.parameters.backup_suppliers
            if s.supplier_id != supplier_id
        ]
        simulation.parameters.backup_suppliers.clear()
        simulation.parameters.backup_suppliers.extend(backup_suppliers_to_keep)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Конфигурация складов
    # -----------------------------------------------------------------

    async def increase_warehouse_size(
        self, request: IncreaseWarehouseSizeRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        if request.warehouse_type == 1:  # WAREHOUSE_TYPE_MATERIALS
            simulation.parameters.materials_warehouse.size += request.size
        elif request.warehouse_type == 2:  # WAREHOUSE_TYPE_PRODUCTS
            simulation.parameters.product_warehouse.size += request.size

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Конфигурация процесса (Инженеринг)
    # -----------------------------------------------------------------

    async def add_process_rote(
        self, request: AddProcessRouteRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        route = Route(
            length=request.length,
            from_workplace=request.from_workplace,
            to_workplace=request.to_workplace,
        )

        simulation = self.simulations[simulation_id]
        simulation.parameters.processes.routes.append(route)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def delete_process_rote(
        self, request: DeleteProcesRouteRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        routes_to_keep = [
            r
            for r in simulation.parameters.processes.routes
            if not (
                r.from_workplace == request.from_workplace
                and r.to_workplace == request.to_workplace
            )
        ]
        simulation.parameters.processes.routes.clear()
        simulation.parameters.processes.routes.extend(routes_to_keep)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_equipment_on_workplace(
        self, request: SetEquipmentOnWorkplaceRequst, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        # Создаем тестовое оборудование
        equipment = Equipment(
            equipment_id=request.equipment_id,
            name=f"Оборудование {request.equipment_id}",
            reliability=0.9,
            maintenance_period=30,
            maintenance_cost=40000,
            cost=1000000,
            repair_cost=200000,
            repair_time=3,
        )

        simulation = self.simulations[simulation_id]

        # Ищем рабочее место и устанавливаем оборудование
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.workplace_id == request.workplace_id:
                workplace.equipment.CopyFrom(equipment)
                break

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def unset_equipment_on_workplace(
        self, request: UnSetEquipmentOnWorkplaceRequst, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Убираем оборудование с указанного рабочего места
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.workplace_id == request.workplace_id:
                workplace.ClearField("equipment")
                break

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Управление картой процесса (Инженеринг)
    # -----------------------------------------------------------------

    async def configure_workplace_in_graph(
        self, request: ConfigureWorkplaceInGraphRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Проверяем, существует ли уже рабочее место
        existing_workplace = None
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.workplace_id == request.workplace_id:
                existing_workplace = workplace
                break

        worker = Worker()
        if request.worker_id:
            worker.worker_id = request.worker_id
            worker.name = f"Работник {request.worker_id}"
            worker.qualification = 4
            worker.specialty = "Оператор"
            worker.salary = 60000

        equipment = Equipment()
        if request.equipment_id:
            equipment.equipment_id = request.equipment_id
            equipment.name = f"Оборудование {request.equipment_id}"
            equipment.reliability = 0.9
            equipment.maintenance_period = 30
            equipment.maintenance_cost = 40000
            equipment.cost = 1000000
            equipment.repair_cost = 200000
            equipment.repair_time = 3

        workplace = Workplace(
            workplace_id=request.workplace_id,
            workplace_name=f"Рабочее место {request.workplace_id}",
            required_speciality=request.workplace_type or "Общая",
            required_qualification=4,
            worker=worker,
            equipment=equipment,
            required_stages=[],
            is_start_node=request.is_start_node,
            is_end_node=request.is_end_node,
            next_workplace_ids=list(request.next_workplace_ids),
        )

        if existing_workplace:
            existing_workplace.CopyFrom(workplace)
        else:
            simulation.parameters.processes.workplaces.append(workplace)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def remove_workplace_from_graph(
        self, request: RemoveWorkplaceFromGraphRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Удаляем рабочее место
        workplaces_to_keep = [
            w
            for w in simulation.parameters.processes.workplaces
            if w.workplace_id != request.workplace_id
        ]
        simulation.parameters.processes.workplaces.clear()
        simulation.parameters.processes.workplaces.extend(workplaces_to_keep)

        # Удаляем маршруты, связанные с этим рабочим местом
        routes_to_keep = [
            r
            for r in simulation.parameters.processes.routes
            if r.from_workplace != request.workplace_id
            and r.to_workplace != request.workplace_id
        ]
        simulation.parameters.processes.routes.clear()
        simulation.parameters.processes.routes.extend(routes_to_keep)

        # Обновляем next_workplace_ids у других рабочих мест
        for workplace in simulation.parameters.processes.workplaces:
            if request.workplace_id in workplace.next_workplace_ids:
                next_ids_to_keep = [
                    wid
                    for wid in workplace.next_workplace_ids
                    if wid != request.workplace_id
                ]
                workplace.next_workplace_ids.clear()
                workplace.next_workplace_ids.extend(next_ids_to_keep)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_workplace_as_start_node(
        self, request: SetWorkplaceAsStartNodeRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Сбрасываем все start_node
        for workplace in simulation.parameters.processes.workplaces:
            workplace.is_start_node = False

        # Устанавливаем указанное рабочее место как начальное
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.workplace_id == request.workplace_id:
                workplace.is_start_node = True
                break

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_workplace_as_end_node(
        self, request: SetWorkplaceAsEndNodeRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Сбрасываем все end_node
        for workplace in simulation.parameters.processes.workplaces:
            workplace.is_end_node = False

        # Устанавливаем указанное рабочее место как конечное
        for workplace in simulation.parameters.processes.workplaces:
            if workplace.workplace_id == request.workplace_id:
                workplace.is_end_node = True
                workplace.next_workplace_ids.clear()  # Конечное не имеет следующих
                break

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def update_process_graph(
        self, request: UpdateProcessGraphRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.processes.CopyFrom(request.process_graph)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Распределение производственного плана (Производство)
    # -----------------------------------------------------------------

    async def distribute_production_plan(
        self, request: DistributeProductionPlanRequest, context
    ) -> ProductionPlanDistributionResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return ProductionPlanDistributionResponse()

        simulation = self.simulations[simulation_id]

        # Очищаем предыдущие распределения
        simulation.parameters.ClearField("production_assignments")

        assignments = []
        total_assigned = 0

        if (
            simulation.parameters.production_schedule
            and simulation.parameters.workshop_plan
        ):
            # Простое распределение: каждому заданию - первое доступное рабочее место
            for (
                schedule_item
            ) in simulation.parameters.production_schedule.schedule_items:
                if simulation.parameters.workshop_plan.workplace_nodes:
                    workplace_node = (
                        simulation.parameters.workshop_plan.workplace_nodes[0]
                    )

                    assignment = ProductionPlanAssignment(
                        schedule_item_id=schedule_item.item_id,
                        workplace_id=workplace_node.workplace_id,
                        assigned_quantity=schedule_item.planned_quantity,
                        assigned_worker_id=(
                            workplace_node.assigned_worker.worker_id
                            if workplace_node.assigned_worker.worker_id
                            else ""
                        ),
                        assigned_equipment_id=(
                            workplace_node.assigned_equipment.equipment_id
                            if workplace_node.assigned_equipment.equipment_id
                            else ""
                        ),
                        completion_percentage=0.0,
                    )

                    assignments.append(assignment)
                    simulation.parameters.production_assignments[
                        schedule_item.item_id
                    ].CopyFrom(assignment)
                    total_assigned += schedule_item.planned_quantity

        return ProductionPlanDistributionResponse(
            assignments=assignments,
            efficiency_score=0.85,
            total_assigned_quantity=total_assigned,
            warnings=(
                ["Распределение выполнено в упрощенном режиме"] if assignments else []
            ),
            timestamp=datetime.now().isoformat(),
        )

    async def get_production_plan_distribution(
        self, request: GetProductionPlanDistributionRequest, context
    ) -> ProductionPlanDistributionResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return ProductionPlanDistributionResponse()

        simulation = self.simulations[simulation_id]

        assignments = list(simulation.parameters.production_assignments.values())
        total_assigned = sum(a.assigned_quantity for a in assignments)

        return ProductionPlanDistributionResponse(
            assignments=assignments,
            efficiency_score=0.85,
            total_assigned_quantity=total_assigned,
            warnings=[],
            timestamp=datetime.now().isoformat(),
        )

    async def update_production_assignment(
        self, request: UpdateProductionAssignmentRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.production_assignments[
            request.assignment.schedule_item_id
        ].CopyFrom(request.assignment)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def update_workshop_plan(
        self, request: UpdateWorkshopPlanRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.workshop_plan.CopyFrom(request.workshop_plan)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Конфигурация тендеров
    # -----------------------------------------------------------------

    async def add_tender(
        self, request: AddTenderRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        # Создаем тестового заказчика
        consumer = Consumer(
            consumer_id="test_consumer",
            name="Тестовый заказчик",
            type="Коммерческая",
        )

        # Создаем тестовый тендер
        tender = Tender(
            tender_id=request.tender_id,
            consumer=consumer,
            cost=1000000,
            quantity_of_products=5,
            penalty_per_day=500000,
            warranty_years=2,
            payment_form="100% по факту",
        )

        simulation = self.simulations[simulation_id]
        simulation.parameters.tenders.append(tender)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def delete_tender(
        self, request: RemoveTenderRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        tenders_to_keep = [
            t for t in simulation.parameters.tenders if t.tender_id != request.tender_id
        ]
        simulation.parameters.tenders.clear()
        simulation.parameters.tenders.extend(tenders_to_keep)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Общие настройки
    # -----------------------------------------------------------------

    async def set_dealing_with_defects(
        self, request: SetDealingWithDefectsRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.dealing_with_defects = request.dealing_with_defects

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_has_certification(
        self, request: SetHasCertificationRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.has_certification = request.has_certification

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def add_production_improvement(
        self, request: AddProductionImprovementRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.production_improvements.append(
            request.production_improvement
        )

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def delete_production_improvement(
        self, request: DeleteProductionImprovementRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        improvements_to_keep = [
            i
            for i in simulation.parameters.production_improvements
            if i != request.production_improvement
        ]
        simulation.parameters.production_improvements.clear()
        simulation.parameters.production_improvements.extend(improvements_to_keep)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_sales_strategy(
        self, request: SetSalesStrategyRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.sales_strategy = request.sales_strategy

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Специфичные настройки по ролям
    # -----------------------------------------------------------------

    async def set_quality_inspection(
        self, request: SetQualityInspectionRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        simulation.parameters.quality_inspections.clear()
        simulation.parameters.quality_inspections[request.material_id].CopyFrom(
            request.inspection
        )

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_delivery_schedule(
        self, request: SetDeliveryScheduleRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Map fields в protobuf не требуют инициализации, можно сразу использовать
        simulation.parameters.delivery_schedules[request.supplier_id].CopyFrom(
            request.schedule
        )

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_equipment_maintenance_interval(
        self, request: SetEquipmentMaintenanceIntervalRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Map fields в protobuf не требуют инициализации, можно сразу использовать
        simulation.parameters.equipment_maintenance_intervals[request.equipment_id] = (
            request.interval_days
        )

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def update_production_schedule(
        self, request: UpdateProductionScheduleRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.production_schedule.CopyFrom(request.schedule)

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_certification_status(
        self, request: SetCertificationStatusRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Ищем сертификацию
        found = False
        for cert in simulation.parameters.certifications:
            if cert.certificate_type == request.certificate_type:
                cert.is_obtained = request.is_obtained
                found = True
                break

        # Если не нашли, добавляем новую
        if not found:
            simulation.parameters.certifications.append(
                Certification(
                    certificate_type=request.certificate_type,
                    is_obtained=request.is_obtained,
                    implementation_cost=500000,
                    implementation_time_days=90,
                )
            )

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_lean_improvement_status(
        self, request: SetLeanImprovementStatusRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Ищем улучшение
        found = False
        for improvement in simulation.parameters.lean_improvements:
            if improvement.improvement_id == request.improvement_id:
                improvement.is_implemented = request.is_implemented
                found = True
                break

        # Если не нашли, добавляем новое
        if not found:
            simulation.parameters.lean_improvements.append(
                LeanImprovement(
                    improvement_id=request.improvement_id,
                    name=f"Улучшение {request.improvement_id}",
                    is_implemented=request.is_implemented,
                    implementation_cost=200000,
                    efficiency_gain=0.15,
                )
            )

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def set_sales_strategy_with_details(
        self, request: SetSalesStrategyWithDetailsRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]
        simulation.parameters.sales_strategy = request.strategy
        simulation.parameters.sales_growth_forecast = request.growth_forecast
        simulation.parameters.unit_production_cost = request.unit_cost

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Методы получения метрик и мониторинга
    # -----------------------------------------------------------------

    async def get_factory_metrics(
        self, request: GetMetricsRequest, context
    ) -> FactoryMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return FactoryMetricsResponse()

        simulation = self.simulations[simulation_id]

        metrics = FactoryMetrics(
            profitability=0.25 + random.random() * 0.15,  # 25-40%
            on_time_delivery_rate=0.85 + random.random() * 0.10,  # 85-95%
            oee=0.75 + random.random() * 0.15,  # 75-90%
            warehouse_metrics={
                "materials": WarehouseMetrics(
                    fill_level=0.35 + random.random() * 0.15,
                    current_load=350,
                    max_capacity=1000,
                    material_levels={"Сталь": 200, "Электроника": 100},
                ),
                "products": WarehouseMetrics(
                    fill_level=0.24 + random.random() * 0.10,
                    current_load=120,
                    max_capacity=500,
                    material_levels={"Готовые": 50, "Комплектующие": 70},
                ),
            },
            total_procurement_cost=1000000 + random.randint(-200000, 200000),
            defect_rate=0.03 + random.random() * 0.02,  # 3-5%
        )

        return FactoryMetricsResponse(
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
        )

    async def get_production_metrics(
        self, request: GetMetricsRequest, context
    ) -> ProductionMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return ProductionMetricsResponse()

        # Генерируем тестовые данные
        months = [
            "Янв",
            "Фев",
            "Мар",
            "Апр",
            "Май",
            "Июн",
            "Июл",
            "Авг",
            "Сен",
            "Окт",
            "Ноя",
            "Дек",
        ]
        monthly_data = []
        for i, month in enumerate(months[: request.step or 4]):
            monthly_data.append(
                ProductionMetrics.MonthlyProductivity(
                    month=month, units_produced=random.randint(80, 120)
                )
            )

        metrics = ProductionMetrics(
            monthly_productivity=monthly_data,
            average_equipment_utilization=0.78 + random.random() * 0.12,
            wip_count=random.randint(50, 100),
            finished_goods_count=random.randint(200, 300),
            material_reserves={"Сталь": 200, "Электроника": 100, "Крепеж": 150},
        )

        # Внеплановый ремонт
        unplanned_repairs = UnplannedRepair(
            repairs=[
                UnplannedRepair.RepairRecord(
                    month="Янв",
                    repair_cost=150000,
                    equipment_id="equipment_001",
                    reason="Поломка двигателя",
                ),
                UnplannedRepair.RepairRecord(
                    month="Фев",
                    repair_cost=80000,
                    equipment_id="equipment_002",
                    reason="Замена режущего инструмента",
                ),
            ],
            total_repair_cost=230000,
        )

        return ProductionMetricsResponse(
            metrics=metrics,
            unplanned_repairs=unplanned_repairs,
            timestamp=datetime.now().isoformat(),
        )

    async def get_quality_metrics(
        self, request: GetMetricsRequest, context
    ) -> QualityMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return QualityMetricsResponse()

        metrics = QualityMetrics(
            defect_percentage=0.035 + random.random() * 0.015,  # 3.5-5%
            good_output_percentage=96.5 - random.random() * 1.5,  # 95-96.5%
            defect_causes=[
                QualityMetrics.DefectCause(
                    cause="Некачественный материал", count=25, percentage=45.5
                ),
                QualityMetrics.DefectCause(
                    cause="Ошибка оператора", count=15, percentage=27.3
                ),
                QualityMetrics.DefectCause(
                    cause="Неисправность оборудования", count=10, percentage=18.2
                ),
                QualityMetrics.DefectCause(
                    cause="Другие причины", count=5, percentage=9.1
                ),
            ],
            average_material_quality=0.92 + random.random() * 0.04,
            average_supplier_failure_probability=0.08 + random.random() * 0.04,
            procurement_volume=4500000 + random.randint(-500000, 500000),
        )

        return QualityMetricsResponse(
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
        )

    async def get_engineering_metrics(
        self, request: GetMetricsRequest, context
    ) -> EngineeringMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return EngineeringMetricsResponse()

        # Операции и их хронометраж
        operations = [
            EngineeringMetrics.OperationTiming(
                operation_name="Резка металла",
                cycle_time=45,
                takt_time=50,
                timing_cost=12000,
            ),
            EngineeringMetrics.OperationTiming(
                operation_name="Сборка узлов",
                cycle_time=120,
                takt_time=130,
                timing_cost=18000,
            ),
            EngineeringMetrics.OperationTiming(
                operation_name="Контроль качества",
                cycle_time=30,
                takt_time=35,
                timing_cost=8000,
            ),
        ]

        # Причины простоев
        downtimes = [
            EngineeringMetrics.DowntimeRecord(
                cause="Переналадка оборудования",
                total_minutes=240,
                average_per_shift=30,
            ),
            EngineeringMetrics.DowntimeRecord(
                cause="Отсутствие материалов", total_minutes=180, average_per_shift=22.5
            ),
            EngineeringMetrics.DowntimeRecord(
                cause="Техническое обслуживание",
                total_minutes=120,
                average_per_shift=15,
            ),
        ]

        # Анализ дефектов (Парето)
        defects = [
            EngineeringMetrics.DefectAnalysis(
                defect_type="Трещины",
                count=35,
                percentage=45.5,
                cumulative_percentage=45.5,
            ),
            EngineeringMetrics.DefectAnalysis(
                defect_type="Неправильные размеры",
                count=20,
                percentage=26.0,
                cumulative_percentage=71.5,
            ),
            EngineeringMetrics.DefectAnalysis(
                defect_type="Заусенцы",
                count=12,
                percentage=15.6,
                cumulative_percentage=87.1,
            ),
            EngineeringMetrics.DefectAnalysis(
                defect_type="Другие",
                count=10,
                percentage=12.9,
                cumulative_percentage=100.0,
            ),
        ]

        metrics = EngineeringMetrics(
            operation_timings=operations,
            downtime_records=downtimes,
            defect_analysis=defects,
        )

        # График хронометража
        timing_chart = OperationTimingChart(
            timing_data=[
                OperationTimingChart.TimingData(
                    process_name="Резка металла",
                    cycle_time=45,
                    takt_time=50,
                    timing_cost=12000,
                ),
                OperationTimingChart.TimingData(
                    process_name="Сборка узлов",
                    cycle_time=120,
                    takt_time=130,
                    timing_cost=18000,
                ),
                OperationTimingChart.TimingData(
                    process_name="Контроль качества",
                    cycle_time=30,
                    takt_time=35,
                    timing_cost=8000,
                ),
            ],
            chart_type="bar_chart",
        )

        # График причин простоев
        downtime_chart = DowntimeChart(
            downtime_data=[
                DowntimeChart.DowntimeData(
                    process_name="Резка металла",
                    cause="Переналадка",
                    downtime_minutes=120,
                ),
                DowntimeChart.DowntimeData(
                    process_name="Сборка узлов",
                    cause="Отсутствие материалов",
                    downtime_minutes=180,
                ),
                DowntimeChart.DowntimeData(
                    process_name="Контроль качества",
                    cause="Техническое обслуживание",
                    downtime_minutes=60,
                ),
            ],
            chart_type="bar_chart",
        )

        return EngineeringMetricsResponse(
            metrics=metrics,
            operation_timing_chart=timing_chart,
            downtime_chart=downtime_chart,
            timestamp=datetime.now().isoformat(),
        )

    async def get_commercial_metrics(
        self, request: GetMetricsRequest, context
    ) -> CommercialMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return CommercialMetricsResponse()

        # Выручка по годам
        yearly_revenues = []
        base_year = 2024
        for i in range(4):
            revenue = 15000000 + i * 2000000 + random.randint(-500000, 500000)
            yearly_revenues.append(
                CommercialMetrics.YearlyRevenue(year=base_year + i, revenue=revenue)
            )

        metrics = CommercialMetrics(
            yearly_revenues=yearly_revenues,
            tender_revenue_plan=25000000,
            total_payments=18000000,
            total_receipts=22000000,
            sales_forecast={
                "Агрессивная": 0.15,
                "Умеренная": 0.08,
                "Консервативная": 0.04,
            },
            strategy_costs={
                "Агрессивная": 85000,
                "Умеренная": 105000,
                "Консервативная": 120000,
            },
            tender_graph=[
                CommercialMetrics.TenderGraphPoint(
                    strategy="ДЗЗ", unit_size="1U", is_mastered=True
                ),
                CommercialMetrics.TenderGraphPoint(
                    strategy="ДЗЗ", unit_size="2U", is_mastered=True
                ),
                CommercialMetrics.TenderGraphPoint(
                    strategy="ДЗЗ", unit_size="3U", is_mastered=False
                ),
                CommercialMetrics.TenderGraphPoint(
                    strategy="Ретрансляция", unit_size="1U", is_mastered=True
                ),
                CommercialMetrics.TenderGraphPoint(
                    strategy="Ретрансляция", unit_size="2U", is_mastered=False
                ),
                CommercialMetrics.TenderGraphPoint(
                    strategy="Научная деятельность", unit_size="1U", is_mastered=True
                ),
            ],
            project_profitabilities=[
                CommercialMetrics.ProjectProfitability(
                    project_name="Проект А", profitability=0.28
                ),
                CommercialMetrics.ProjectProfitability(
                    project_name="Проект Б", profitability=0.35
                ),
                CommercialMetrics.ProjectProfitability(
                    project_name="Проект В", profitability=0.22
                ),
                CommercialMetrics.ProjectProfitability(
                    project_name="Проект Г", profitability=0.31
                ),
            ],
            on_time_completed_orders=18,
        )

        # График освоенных моделей
        model_mastery_chart = ModelMasteryChart(
            model_points=[
                ModelMasteryChart.ModelPoint(
                    strategy="ДЗЗ",
                    unit_size="1U",
                    is_mastered=True,
                    model_name="Спутник связи",
                ),
                ModelMasteryChart.ModelPoint(
                    strategy="ДЗЗ",
                    unit_size="2U",
                    is_mastered=True,
                    model_name="Ретранслятор",
                ),
                ModelMasteryChart.ModelPoint(
                    strategy="ДЗЗ",
                    unit_size="3U",
                    is_mastered=False,
                    model_name="Многофункциональный",
                ),
                ModelMasteryChart.ModelPoint(
                    strategy="Ретрансляция",
                    unit_size="1U",
                    is_mastered=True,
                    model_name="Транспондер",
                ),
                ModelMasteryChart.ModelPoint(
                    strategy="Ретрансляция",
                    unit_size="2U",
                    is_mastered=False,
                    model_name="Усилитель",
                ),
                ModelMasteryChart.ModelPoint(
                    strategy="Научная деятельность",
                    unit_size="1U",
                    is_mastered=True,
                    model_name="Исследовательский",
                ),
            ]
        )

        # График рентабельности проектов
        project_chart = ProjectProfitabilityChart(
            projects=[
                ProjectProfitabilityChart.ProjectData(
                    project_name="Проект А", profitability=0.28
                ),
                ProjectProfitabilityChart.ProjectData(
                    project_name="Проект Б", profitability=0.35
                ),
                ProjectProfitabilityChart.ProjectData(
                    project_name="Проект В", profitability=0.22
                ),
                ProjectProfitabilityChart.ProjectData(
                    project_name="Проект Г", profitability=0.31
                ),
            ],
            chart_type="bar_chart",
        )

        return CommercialMetricsResponse(
            metrics=metrics,
            model_mastery_chart=model_mastery_chart,
            project_profitability_chart=project_chart,
            timestamp=datetime.now().isoformat(),
        )

    async def get_procurement_metrics(
        self, request: GetMetricsRequest, context
    ) -> ProcurementMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return ProcurementMetricsResponse()

        supplier_performances = [
            ProcurementMetrics.SupplierPerformance(
                supplier_id="supplier_001",
                delivered_quantity=1250,
                projected_defect_rate=0.08,
                planned_reliability=0.95,
                actual_reliability=0.92,
                planned_cost=1500000,
                actual_cost=1450000,
                actual_defect_count=15,
            ),
            ProcurementMetrics.SupplierPerformance(
                supplier_id="supplier_002",
                delivered_quantity=850,
                projected_defect_rate=0.05,
                planned_reliability=0.90,
                actual_reliability=0.88,
                planned_cost=1200000,
                actual_cost=1180000,
                actual_defect_count=8,
            ),
        ]

        metrics = ProcurementMetrics(
            supplier_performances=supplier_performances, total_procurement_value=2630000
        )

        return ProcurementMetricsResponse(
            metrics=metrics,
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_metrics(
        self, request: GetAllMetricsRequest, context
    ) -> AllMetricsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return AllMetricsResponse()

        # Получаем все метрики
        factory_metrics = await self.get_factory_metrics(
            GetMetricsRequest(simulation_id=simulation_id), context
        )
        production_metrics = await self.get_production_metrics(
            GetMetricsRequest(simulation_id=simulation_id), context
        )
        quality_metrics = await self.get_quality_metrics(
            GetMetricsRequest(simulation_id=simulation_id), context
        )
        engineering_metrics = await self.get_engineering_metrics(
            GetMetricsRequest(simulation_id=simulation_id), context
        )
        commercial_metrics = await self.get_commercial_metrics(
            GetMetricsRequest(simulation_id=simulation_id), context
        )
        procurement_metrics = await self.get_procurement_metrics(
            GetMetricsRequest(simulation_id=simulation_id), context
        )

        return AllMetricsResponse(
            factory=factory_metrics.metrics,
            production=production_metrics.metrics,
            quality=quality_metrics.metrics,
            engineering=engineering_metrics.metrics,
            commercial=commercial_metrics.metrics,
            procurement=procurement_metrics.metrics,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Методы получения данных для вкладок
    # -----------------------------------------------------------------

    async def get_production_schedule(
        self, request: GetProductionScheduleRequest, context
    ) -> ProductionScheduleResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return ProductionScheduleResponse()

        simulation = self.simulations[simulation_id]

        # Если нет расписания, создаем тестовое
        if not simulation.parameters.HasField("production_schedule"):
            new_schedule = ProductionSchedule(
                schedule_items=[
                    ProductionSchedule.ScheduleItem(
                        item_id="item_001",
                        priority=1,
                        plan_number="П-001",
                        plan_date="2024-01-15",
                        product_name="Спутник связи",
                        planned_quantity=10,
                        actual_quantity=3,
                        remaining_to_produce=7,
                        planned_completion_date="2024-03-15",
                        order_number="ЗАК-001",
                        tender_id="tender_001",
                    )
                ]
            )
            simulation.parameters.production_schedule.CopyFrom(new_schedule)

        return ProductionScheduleResponse(
            schedule=simulation.parameters.production_schedule,
            timestamp=datetime.now().isoformat(),
        )

    async def get_workshop_plan(
        self, request: GetWorkshopPlanRequest, context
    ) -> WorkshopPlanResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return WorkshopPlanResponse()

        simulation = self.simulations[simulation_id]

        # Если нет плана цеха, создаем тестовый
        if not simulation.parameters.HasField("workshop_plan"):
            new_workshop_plan = WorkshopPlan(
                workplace_nodes=[
                    WorkshopPlan.WorkplaceNode(
                        workplace_id="workplace_001",
                        assigned_worker=Worker(
                            worker_id="worker_001",
                            name="Иванов И.И.",
                            qualification=5,
                            specialty="Слесарь",
                            salary=75000,
                        ),
                        assigned_equipment=Equipment(
                            equipment_id="equipment_001",
                            name="Токарный станок",
                            reliability=0.95,
                            maintenance_period=30,
                            maintenance_cost=50000,
                            cost=1500000,
                            repair_cost=300000,
                            repair_time=5,
                        ),
                        maintenance_interval=30,
                        is_start_node=True,
                        is_end_node=False,
                        assigned_schedule_items=["item_001"],
                        max_capacity_per_day=2,
                        current_utilization=0.75,
                    )
                ],
                logistic_routes=[
                    Route(
                        length=10,
                        from_workplace="workplace_001",
                        to_workplace="workplace_002",
                    ),
                    Route(
                        length=15,
                        from_workplace="workplace_002",
                        to_workplace="workplace_003",
                    ),
                ],
                production_schedule_id="schedule_001",
            )
            simulation.parameters.workshop_plan.CopyFrom(new_workshop_plan)

        return WorkshopPlanResponse(
            workshop_plan=simulation.parameters.workshop_plan,
            timestamp=datetime.now().isoformat(),
        )

    async def get_unplanned_repair(
        self, request: GetUnplannedRepairRequest, context
    ) -> UnplannedRepairResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return UnplannedRepairResponse()

        # Тестовые данные о внеплановом ремонте
        unplanned_repair = UnplannedRepair(
            repairs=[
                UnplannedRepair.RepairRecord(
                    month="Янв",
                    repair_cost=150000,
                    equipment_id="equipment_001",
                    reason="Поломка двигателя",
                ),
                UnplannedRepair.RepairRecord(
                    month="Фев",
                    repair_cost=80000,
                    equipment_id="equipment_002",
                    reason="Замена режущего инструмента",
                ),
                UnplannedRepair.RepairRecord(
                    month="Мар",
                    repair_cost=120000,
                    equipment_id="equipment_003",
                    reason="Ремонт системы ЧПУ",
                ),
            ],
            total_repair_cost=350000,
        )

        return UnplannedRepairResponse(
            unplanned_repair=unplanned_repair,
            timestamp=datetime.now().isoformat(),
        )

    async def get_warehouse_load_chart(
        self, request: GetWarehouseLoadChartRequest, context
    ) -> WarehouseLoadChartResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return WarehouseLoadChartResponse()

        # Генерируем тестовые данные для графика загрузки
        data_points = []
        max_capacity = 1000 if request.warehouse_id.endswith("materials") else 500

        for i in range(30):  # 30 дней
            load = random.randint(200, max_capacity - 100)
            data_points.append(
                WarehouseLoadChart.LoadPoint(
                    timestamp=f"2024-01-{i+1:02d}", load=load, max_capacity=max_capacity
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
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return RequiredMaterialsResponse()

        # Тестовые данные о необходимых материалах
        materials = [
            RequiredMaterial(
                material_id="mat_001",
                name="Листовой металл",
                has_contracted_supplier=True,
                required_quantity=500,
                current_stock=200,
            ),
            RequiredMaterial(
                material_id="mat_002",
                name="Электронные компоненты",
                has_contracted_supplier=True,
                required_quantity=1000,
                current_stock=450,
            ),
            RequiredMaterial(
                material_id="mat_003",
                name="Крепежные изделия",
                has_contracted_supplier=False,
                required_quantity=2000,
                current_stock=800,
            ),
            RequiredMaterial(
                material_id="mat_004",
                name="Пластик ABS",
                has_contracted_supplier=True,
                required_quantity=300,
                current_stock=150,
            ),
        ]

        return RequiredMaterialsResponse(
            materials=materials,
            timestamp=datetime.now().isoformat(),
        )

    async def get_available_improvements(
        self, request: GetAvailableImprovementsRequest, context
    ) -> AvailableImprovementsResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return AvailableImprovementsResponse()

        simulation = self.simulations[simulation_id]

        return AvailableImprovementsResponse(
            improvements=simulation.parameters.lean_improvements,
            timestamp=datetime.now().isoformat(),
        )

    async def get_defect_policies(
        self, request: GetDefectPoliciesRequest, context
    ) -> DefectPoliciesResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return DefectPoliciesResponse()

        simulation = self.simulations[simulation_id]

        available_policies = [
            "Утилизировать",
            "Переделать",
            "Продать как есть",
            "Вернуть поставщику",
        ]

        return DefectPoliciesResponse(
            available_policies=available_policies,
            current_policy=simulation.parameters.dealing_with_defects or "Переделать",
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Пошаговая симуляция
    # -----------------------------------------------------------------

    async def run_simulation_step(
        self, request: RunSimulationStepRequest, context
    ) -> SimulationStepResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationStepResponse()

        simulation = self.simulations[simulation_id]

        # Выполняем шаги симуляции
        for step in range(min(request.step_count, 4 - simulation.step)):
            simulation.step += 1

            # Обновляем капитал (упрощенная модель)
            profit = random.randint(-200000, 500000)
            simulation.capital += profit

            # Обновляем результаты
            simulation.results.profit += profit
            simulation.results.cost += random.randint(100000, 300000)
            simulation.results.profitability = (
                simulation.results.profit / simulation.results.cost
                if simulation.results.cost > 0
                else 0
            )

            # Сохраняем шаг в историю
            step_response = SimulationStepResponse(
                simulation=Simulation(
                    capital=simulation.capital,
                    step=simulation.step,
                    simulation_id=simulation.simulation_id,
                    parameters=simulation.parameters,
                    results=simulation.results,
                    room_id=simulation.room_id,
                    is_completed=simulation.is_completed,
                ),
                timestamp=datetime.now().isoformat(),
            )

            if simulation_id not in self.simulation_history:
                self.simulation_history[simulation_id] = []
            self.simulation_history[simulation_id].append(step_response)

        # Проверяем завершение симуляции
        if simulation.step >= 4:
            simulation.is_completed = True

        # Получаем метрики для текущего шага
        factory_metrics = await self.get_factory_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=simulation.step),
            context,
        )
        production_metrics = await self.get_production_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=simulation.step),
            context,
        )
        quality_metrics = await self.get_quality_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=simulation.step),
            context,
        )
        engineering_metrics = await self.get_engineering_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=simulation.step),
            context,
        )
        commercial_metrics = await self.get_commercial_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=simulation.step),
            context,
        )
        procurement_metrics = await self.get_procurement_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=simulation.step),
            context,
        )

        return SimulationStepResponse(
            simulation=simulation,
            factory_metrics=factory_metrics.metrics,
            production_metrics=production_metrics.metrics,
            quality_metrics=quality_metrics.metrics,
            engineering_metrics=engineering_metrics.metrics,
            commercial_metrics=commercial_metrics.metrics,
            procurement_metrics=procurement_metrics.metrics,
            timestamp=datetime.now().isoformat(),
        )

    async def get_simulation_history(
        self, request: GetSimulationHistoryRequest, context
    ) -> SimulationHistoryResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationHistoryResponse()

        history = self.simulation_history.get(simulation_id, [])

        return SimulationHistoryResponse(
            steps=history,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Валидация
    # -----------------------------------------------------------------

    async def validate_configuration(
        self, request: ValidateConfigurationRequest, context
    ) -> ValidationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            return ValidationResponse(
                is_valid=False,
                errors=[f"Симуляция с ID {simulation_id} не найдена"],
                warnings=[],
                timestamp=datetime.now().isoformat(),
            )

        simulation = self.simulations[simulation_id]
        errors = []
        warnings = []

        # Проверяем обязательные параметры

        # Проверка логиста
        if not simulation.parameters.logist.worker_id:
            errors.append("Не выбран логист")

        # Проверка поставщиков
        if not simulation.parameters.suppliers:
            errors.append("Не выбраны основные поставщики")

        # Проверка складов
        if simulation.parameters.materials_warehouse.size == 0:
            warnings.append("Размер склада материалов не задан")

        # Проверка производственного графа
        if not simulation.parameters.processes.workplaces:
            errors.append("Не настроен производственный граф")
        else:
            # Проверяем наличие начального и конечного узлов
            has_start = any(
                w.is_start_node for w in simulation.parameters.processes.workplaces
            )
            has_end = any(
                w.is_end_node for w in simulation.parameters.processes.workplaces
            )

            if not has_start:
                warnings.append("Не указан начальный узел в производственном графе")
            if not has_end:
                warnings.append("Не указан конечный узел в производственном графе")

        # Проверка производственного плана
        if (
            not simulation.parameters.HasField("production_schedule")
            or not simulation.parameters.production_schedule.schedule_items
        ):
            warnings.append("Не настроен производственный план")

        # Проверка стратегии продаж
        if not simulation.parameters.sales_strategy:
            warnings.append("Не выбрана стратегия продаж")

        return ValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            timestamp=datetime.now().isoformat(),
        )

    # -----------------------------------------------------------------
    #          Справочные данные (прокси к DatabaseManager)
    # -----------------------------------------------------------------

    async def get_reference_data(
        self, request: GetReferenceDataRequest, context
    ) -> ReferenceDataResponse:
        # В реальной реализации здесь был бы вызов DatabaseManager
        # Для тестов возвращаем заглушку
        return ReferenceDataResponse(timestamp=datetime.now().isoformat())

    async def get_material_types(
        self, request: GetMaterialTypesRequest, context
    ) -> MaterialTypesResponse:
        return MaterialTypesResponse(timestamp=datetime.now().isoformat())

    async def get_equipment_types(
        self, request: GetEquipmentTypesRequest, context
    ) -> EquipmentTypesResponse:
        return EquipmentTypesResponse(timestamp=datetime.now().isoformat())

    async def get_workplace_types(
        self, request: GetWorkplaceTypesRequest, context
    ) -> WorkplaceTypesResponse:
        return WorkplaceTypesResponse(timestamp=datetime.now().isoformat())

    async def get_available_defect_policies(
        self, request: GetAvailableDefectPoliciesRequest, context
    ) -> DefectPoliciesListResponse:
        return DefectPoliciesListResponse(timestamp=datetime.now().isoformat())

    async def get_available_improvements_list(
        self, request: GetAvailableImprovementsListRequest, context
    ) -> ImprovementsListResponse:
        return ImprovementsListResponse(timestamp=datetime.now().isoformat())

    async def get_available_certifications(
        self, request: GetAvailableCertificationsRequest, context
    ) -> CertificationsListResponse:
        return CertificationsListResponse(timestamp=datetime.now().isoformat())

    async def get_available_sales_strategies(
        self, request: GetAvailableSalesStrategiesRequest, context
    ) -> SalesStrategiesListResponse:
        return SalesStrategiesListResponse(timestamp=datetime.now().isoformat())

    # -----------------------------------------------------------------
    #          Старые методы (для обратной совместимости)
    # -----------------------------------------------------------------

    async def run_simulation(
        self, request: RunSimulationRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Запускаем полную симуляцию (4 шага)
        step_response = await self.run_simulation_step(
            RunSimulationStepRequest(simulation_id=simulation_id, step_count=4), context
        )

        return SimulationResponse(
            simulation=step_response.simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def ping(self, request: PingRequest, context) -> SuccessResponse:
        return SuccessResponse(
            success=True,
            message="Simulation service is running",
            timestamp=datetime.now().isoformat(),
        )
