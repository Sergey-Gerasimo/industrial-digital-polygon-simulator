from datetime import datetime
from typing import Dict
import uuid

import grpc
from grpc_generated.simulator_pb2 import (
    AddProcessRouteRequest,
    AddProductionImprovementRequest,
    AddSupplierRequest,
    AddTenderRequest,
    Consumer,
    CreateSimulationRquest,
    DeleteProcesRouteRequest,
    DeleteProductionImprovementRequest,
    DeleteSupplierRequest,
    Equipment,
    GetSimulationRequest,
    IncreaseWarehouseSizeRequest,
    Logist,
    PingRequest,
    ProcessGraph,
    RemoveTenderRequest,
    Route,
    RunSimulationRequest,
    SetDealingWithDefectsRequest,
    SetEquipmentOnWorkplaceRequst,
    SetHasCertificationRequest,
    SetLogistRequest,
    SetSalesStrategyRequest,
    SetWarehouseInventoryWorkerRequest,
    SetWorkerOnWorkerplaceRequest,
    Simulation,
    SimulationParameters,
    SimulationResponse,
    SimulationResults,
    SuccessResponse,
    Supplier,
    Tender,
    UnSetEquipmentOnWorkplaceRequst,
    UnSetWorkerOnWorkerplaceRequest,
    Warehouse,
    Worker,
    Workplace,
)
from grpc_generated.simulator_pb2_grpc import SimulationServiceServicer


class SimulationServiceImpl(SimulationServiceServicer):

    def __init__(self):
        self.simulations: Dict[str, Simulation] = {}
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

        # Создаем тестовое рабочее место
        test_workplace = Workplace(
            workplace_id="workplace_001",
            workplace_name="Слесарный участок",
            required_speciality="Слесарь",
            required_qualification=4,
            worker=test_worker,
            equipment=test_equipment,
            required_stages=["Подготовка", "Резка"],
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
                    workplaces=[test_workplace],
                    routes=[
                        Route(
                            length=10,
                            from_workplace="workplace_001",
                            to_workplace="workplace_002",
                        ),
                    ],
                ),
                tenders=[
                    Tender(
                        tender_id="tender_001",
                        consumer=test_consumer,
                        cost=2500000,
                        quantity_of_products=10,
                    ),
                ],
                dealing_with_defects="Ремонтировать на месте",
                has_certification=True,
                production_improvements=["Автоматизация склада", "Внедрение ERP"],
                sales_strategy="Агрессивная",
            ),
            results=SimulationResults(
                profit=1500000,
                cost=1000000,
                profitability=1.5,
            ),
        )

        self.simulations[simulation_id] = simulation

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
        )

        self.simulations[simulation_id] = simulation

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
            )
            self.simulations[simulation_id] = simulation

        simulation = self.simulations[simulation_id]

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

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
        simulation.parameters.suppliers[:] = [
            s for s in simulation.parameters.suppliers if s.supplier_id != supplier_id
        ]

        # Удаляем из запасных поставщиков
        simulation.parameters.backup_suppliers[:] = [
            s
            for s in simulation.parameters.backup_suppliers
            if s.supplier_id != supplier_id
        ]

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

        simulation.parameters.processes.routes[:] = [
            r
            for r in simulation.parameters.processes.routes
            if not (
                r.from_workplace == request.from_workplace
                and r.to_workplace == request.to_workplace
            )
        ]

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

        simulation.parameters.tenders[:] = [
            t for t in simulation.parameters.tenders if t.tender_id != request.tender_id
        ]

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

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

        simulation.parameters.production_improvements[:] = [
            i
            for i in simulation.parameters.production_improvements
            if i != request.production_improvement
        ]

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

    async def run_simulation(
        self, request: RunSimulationRequest, context
    ) -> SimulationResponse:
        simulation_id = request.simulation_id

        if simulation_id not in self.simulations:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Симуляция с ID {simulation_id} не найдена")
            return SimulationResponse()

        simulation = self.simulations[simulation_id]

        # Генерируем тестовые результаты симуляции
        simulation.results = SimulationResults(
            profit=2000000,
            cost=1500000,
            profitability=1.33,
        )
        simulation.step = 4  # Завершаем симуляцию

        return SimulationResponse(
            simulation=simulation,
            timestamp=datetime.now().isoformat(),
        )

    async def ping(self, request: PingRequest, context) -> SuccessResponse:
        return SuccessResponse(
            success=True,
            message="Simulation service is running",
            timestamp=datetime.now().isoformat(),
        )
